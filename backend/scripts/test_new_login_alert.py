"""
Test isolé du flow "nouvelle connexion → email d'alerte".

Ce script reproduit EXACTEMENT le chemin de code utilisé par /api/auth/login
quand un device inconnu est détecté, mais sans passer par le login HTTP :

    notification_service.send_new_login_alert(...)
        → NotificationPreference (création si absente)
        → rendu Jinja2 du template new_login_alert.html
        → email_service.send_email (SMTP TLS Gmail)
        → NotificationHistory (log du résultat)

Cela permet de vérifier que :
  1. Les credentials SMTP du .env sont valides
  2. Le template HTML s'affiche correctement
  3. Les préférences utilisateur permettent l'envoi
  4. L'email arrive bien dans la boîte de réception

Usage :
    cd backend
    python scripts/test_new_login_alert.py <username_ou_email>

Exemple :
    python scripts/test_new_login_alert.py Lobna
    python scripts/test_new_login_alert.py user@example.com

Le mail de test sera envoyé à l'adresse email enregistrée du compte (ou à
notification_email si l'utilisateur l'a configurée dans ses préférences).
"""

from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Permettre l'import "app.*" même quand on lance le script depuis backend/
BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

from dotenv import load_dotenv

load_dotenv(BACKEND_ROOT / ".env")

from sqlalchemy import select  # noqa: E402

from app.database import AsyncSessionLocal  # noqa: E402

# IMPORTANT : on doit importer TOUS les modèles avant la moindre requête,
# sinon les relationships string-based (ex: User.analyses → "AnalysisHistory")
# ne sont pas résolues et SQLAlchemy lève KeyError au compile_state.
# C'est exactement ce que main.py fait dans son lifespan.
from app.models import (  # noqa: E402, F401
    user_models,
    database_models,
    email_provider_models,
    session_models,
    notification_models,
    audit_models,
    email_verification_models,
    password_reset_models,
)
from app.models.user_models import User  # noqa: E402
from app.services.notification_service import notification_service  # noqa: E402


# ─── Couleurs ANSI ──────────────────────────────────────────────────────────
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    OK = "\033[92m"
    WARN = "\033[93m"
    FAIL = "\033[91m"
    INFO = "\033[96m"


if sys.platform == "win32":
    os.system("")


def step(msg: str) -> None:
    print(f"\n{C.BOLD}{C.INFO}━━━ {msg} ━━━{C.RESET}")


def ok(msg: str) -> None:
    print(f"{C.OK}[OK]{C.RESET} {msg}")


def fail(msg: str) -> None:
    print(f"{C.FAIL}[FAIL]{C.RESET} {msg}")


def warn(msg: str) -> None:
    print(f"{C.WARN}[WARN]{C.RESET} {msg}")


def info(msg: str) -> None:
    print(f"{C.INFO}[..]{C.RESET} {msg}")


async def find_user(db, identifier: str) -> User | None:
    """Cherche un user par username puis par email."""
    result = await db.execute(select(User).where(User.username == identifier))
    user = result.scalar_one_or_none()
    if user:
        return user
    result = await db.execute(select(User).where(User.email == identifier))
    return result.scalar_one_or_none()


async def main(identifier: str) -> int:
    step("0. Vérification des variables SMTP")
    required = ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD"]
    missing = [v for v in required if not os.getenv(v)]
    if missing:
        fail(f"Variables manquantes dans .env : {', '.join(missing)}")
        return 1
    ok(f"SMTP_HOST = {os.getenv('SMTP_HOST')}:{os.getenv('SMTP_PORT')}")
    ok(f"SMTP_USER = {os.getenv('SMTP_USER')}")
    ok(f"FROM_EMAIL = {os.getenv('FROM_EMAIL', os.getenv('SMTP_USER'))}")

    step(f"1. Recherche du compte : {identifier}")
    async with AsyncSessionLocal() as db:
        user = await find_user(db, identifier)
        if user is None:
            fail(f"Aucun utilisateur trouvé pour '{identifier}' (ni username ni email)")
            return 2
        ok(f"User trouvé : id={user.id}  username={user.username}  email={user.email}")

        step("2. Préparation du payload (simulé : nouvelle connexion depuis Firefox/Linux)")
        login_details = {
            "device": "Firefox on Linux (test_new_login_alert.py)",
            "browser": "Firefox 125.0",
            "location": "Paris, France (TEST)",
            "ip_address": "203.0.113.42",
            "login_time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        }
        for k, v in login_details.items():
            info(f"  {k}: {v}")

        step("3. Appel direct de notification_service.send_new_login_alert()")
        info("(Ceci va : vérifier les préférences → rendre le template → envoyer SMTP → logger dans NotificationHistory)")
        try:
            success = await notification_service.send_new_login_alert(
                db=db,
                user=user,
                login_details=login_details,
            )
        except Exception as e:
            fail(f"Exception levée : {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return 3

        if success:
            recipient = user.email  # par défaut
            # On ne re-query pas notification_email ici, send_new_login_alert le gère.
            ok(f"Email envoyé avec succès → vérifie la boîte {recipient}")
            ok("Si tu ne vois rien : regarde dans les spams / dossier 'Toutes les messageries'")
            return 0

        fail("send_new_login_alert a renvoyé False")
        warn("Causes possibles :")
        warn("  • new_login_alerts désactivé dans NotificationPreference de cet utilisateur")
        warn("  • email_notifications_enabled = False")
        warn("  • Échec SMTP (mauvais mot de passe app, port bloqué, etc.)")
        warn("Inspecte phishguard.log et la table notification_history pour le détail.")
        return 4


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    rc = asyncio.run(main(sys.argv[1]))
    sys.exit(rc)
