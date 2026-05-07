"""
Database retry utility for handling TRANSIENT connection errors only.

Why this exists
---------------
Supabase / PostgreSQL connections can drop unexpectedly: idle timeout,
server restart, network blip, SSL renegotiation, deadlock, etc. Without
retries, a single unlucky request returns a 500 to the user, while the
very same request 200ms later would succeed.

Design
------
The decorator distinguishes:
  - **Transient errors** (connection drop, timeout, deadlock) -> retry with
    exponential backoff after rolling back the aborted transaction.
  - **Deterministic errors** (UndefinedColumn, syntax, integrity violation)
    -> raise immediately. Retrying would be useless and just spams logs.

The distinction is made on the PostgreSQL **SQLSTATE** code (5-char value
attached to every asyncpg exception, e.g. ``42703`` for undefined_column,
``08006`` for connection_failure). See:
https://www.postgresql.org/docs/current/errcodes-appendix.html
"""

import asyncio
import logging
from functools import wraps
from typing import Optional

from sqlalchemy.exc import DBAPIError, OperationalError, InterfaceError
from sqlalchemy.ext.asyncio import AsyncSession
from asyncpg.exceptions import ConnectionDoesNotExistError

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# SQLSTATE classification
# ---------------------------------------------------------------------------
# Class 08 = Connection Exceptions (always transient)
# Class 40 = Transaction Rollback (deadlock, serialization) -> retry
# Class 57 = Operator Intervention (admin shutdown) -> retry
# Class 53 = Insufficient Resources (too_many_connections) -> retry
_RETRIABLE_SQLSTATES: frozenset[str] = frozenset({
    "08000", "08001", "08003", "08004", "08006", "08007",  # connection
    "40001", "40P01",                                          # serialization, deadlock
    "53300",                                                    # too_many_connections
    "57P01", "57P02", "57P03",                                  # admin shutdown / cannot connect now
})

# Class 42 = Syntax Error or Access Rule Violation (NEVER retry: schema bug)
# Class 23 = Integrity Constraint Violation (NEVER retry: business error)
# Class 22 = Data Exception (NEVER retry: bad input)
# 25P02 = in_failed_sql_transaction (cause is upstream, retry pointless)
_NON_RETRIABLE_PREFIXES: tuple[str, ...] = ("22", "23", "42")
_NON_RETRIABLE_SQLSTATES: frozenset[str] = frozenset({
    "25P02",  # in_failed_sql_transaction
    "42501",  # insufficient_privilege
})


def _get_sqlstate(exc: BaseException) -> Optional[str]:
    """
    Extract the PostgreSQL SQLSTATE from a (possibly wrapped) exception.

    SQLAlchemy wraps the original asyncpg exception in DBAPIError; we walk
    the ``__cause__`` / ``__context__`` chain to find the underlying asyncpg
    exception, which exposes ``.sqlstate``.
    """
    candidate: Optional[BaseException] = exc
    seen: set[int] = set()
    while candidate is not None and id(candidate) not in seen:
        seen.add(id(candidate))
        sqlstate = getattr(candidate, "sqlstate", None)
        if sqlstate:
            return str(sqlstate)
        # asyncpg also exposes pgcode in some wrappers
        pgcode = getattr(candidate, "pgcode", None)
        if pgcode:
            return str(pgcode)
        candidate = candidate.__cause__ or candidate.__context__
    return None


def _is_retriable(exc: BaseException) -> bool:
    """Return True if the exception represents a transient DB error."""
    sqlstate = _get_sqlstate(exc)
    if sqlstate:
        if sqlstate in _NON_RETRIABLE_SQLSTATES:
            return False
        if sqlstate.startswith(_NON_RETRIABLE_PREFIXES):
            return False
        if sqlstate in _RETRIABLE_SQLSTATES or sqlstate.startswith("08"):
            return True
        # Unknown SQLSTATE -> conservative: don't retry
        return False

    # Fallback for exceptions without a SQLSTATE (rare: pure network errors)
    msg = str(exc).lower()
    transient_patterns = (
        "connection was closed",
        "connection reset",
        "connection refused",
        "server closed the connection",
        "connection is closed",
        "timeout",
        "ssl connection",
    )
    return any(p in msg for p in transient_patterns)


def _find_session(args: tuple, kwargs: dict) -> Optional[AsyncSession]:
    """
    Locate the AsyncSession argument so we can rollback the aborted
    transaction before retrying. Supports both ``func(db, ...)`` and
    ``func(..., db=db)`` calling conventions.
    """
    db = kwargs.get("db")
    if isinstance(db, AsyncSession):
        return db
    for arg in args:
        if isinstance(arg, AsyncSession):
            return arg
    return None


def retry_on_db_error(max_retries: int = 3, delay: float = 0.5):
    """
    Decorator to retry async DB operations on TRANSIENT errors only.

    Will retry on:
      - Connection drops, resets, timeouts (SQLSTATE class 08*)
      - Deadlocks (40P01) and serialization failures (40001)
      - Server admin shutdown / cannot-connect-now (57P0*)
      - Too many connections (53300)

    Will NOT retry on:
      - Schema errors (UndefinedColumn 42703, UndefinedTable 42P01, ...)
      - Syntax errors (42601), permission errors (42501)
      - Integrity violations (unique 23505, FK 23503, NOT NULL 23502, ...)
      - Data exceptions (class 22)
      - InFailedSQLTransactionError (25P02): cause is upstream

    Between retries the session is rolled back so the next attempt runs in
    a fresh transaction. Backoff is exponential: ``delay * 2**(attempt-1)``.

    Args:
        max_retries: Maximum number of attempts (default 3).
        delay: Initial delay between retries in seconds (default 0.5s).
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            session = _find_session(args, kwargs)
            last_exception: Optional[BaseException] = None

            for attempt in range(1, max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except (DBAPIError, OperationalError, InterfaceError,
                        ConnectionDoesNotExistError) as exc:
                    last_exception = exc

                    # Deterministic error -> abort immediately
                    if not _is_retriable(exc):
                        raise

                    # Last attempt failed -> propagate
                    if attempt == max_retries:
                        raise

                    sqlstate = _get_sqlstate(exc) or "unknown"
                    backoff = delay * (2 ** (attempt - 1))
                    logger.warning(
                        "Transient DB error in %s [SQLSTATE=%s], "
                        "retry %d/%d in %.2fs: %s",
                        func.__name__, sqlstate, attempt, max_retries,
                        backoff, str(exc)[:120],
                    )

                    # Rollback FIRST so the aborted transaction is cleared,
                    # then back off, then retry on a clean session.
                    if session is not None:
                        try:
                            await session.rollback()
                        except Exception as rollback_exc:  # noqa: BLE001
                            logger.debug(
                                "Rollback during retry of %s failed: %s",
                                func.__name__, rollback_exc,
                            )

                    await asyncio.sleep(backoff)

            # Defensive: should be unreachable because the loop either
            # returns or raises on the last iteration.
            assert last_exception is not None
            raise last_exception

        return wrapper
    return decorator
