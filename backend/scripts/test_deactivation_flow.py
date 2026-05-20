"""
End-to-end test for the deactivation/reactivation flow.

Tests:
  1. Login normally with an active test account
  2. Deactivate via PUT /api/auth/me/deactivate
  3. Try to login -> expect 403 ACCOUNT_DEACTIVATED
  4. Reactivate via POST /api/auth/reactivate
  5. Verify the returned token works (GET /api/auth/me)
  6. Login again normally -> expect 200

Usage:
  python scripts/test_deactivation_flow.py <username> <password>

The user must already exist with email_verified=True. If 2FA is enabled,
the test will skip reactivation step and report it.
"""

import sys
import httpx

BASE = "http://localhost:8000/api/auth"


def step(num: int, title: str):
    print()
    print(f"\u2500" * 70)
    print(f"  STEP {num}: {title}")
    print(f"\u2500" * 70)


def ok(msg: str):
    print(f"  [OK] {msg}")


def fail(msg: str):
    print(f"  [FAIL] {msg}")


def info(msg: str):
    print(f"  [..] {msg}")


def login(client: httpx.Client, username: str, password: str) -> httpx.Response:
    return client.post(
        f"{BASE}/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )


def reactivate(client: httpx.Client, username: str, password: str) -> httpx.Response:
    return client.post(
        f"{BASE}/reactivate",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )


def deactivate(client: httpx.Client, token: str, password: str) -> httpx.Response:
    return client.put(
        f"{BASE}/me/deactivate",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={"password": password, "reason": "Automated E2E test"},
    )


def me(client: httpx.Client, token: str) -> httpx.Response:
    return client.get(f"{BASE}/me", headers={"Authorization": f"Bearer {token}"})


def run_tests(username: str, password: str) -> int:
    client = httpx.Client(timeout=10.0)
    failures = 0

    # ── STEP 1: Initial login ──
    step(1, "Initial login (account must be active)")
    r = login(client, username, password)
    if r.status_code == 200:
        ok(f"Login OK -> token received (status {r.status_code})")
        token = r.json()["access_token"]
    elif r.status_code == 403 and r.json().get("detail") == "ACCOUNT_DEACTIVATED":
        info("Account is already deactivated. Reactivating it first to start clean...")
        rr = reactivate(client, username, password)
        if rr.status_code != 200:
            fail(f"Cannot reactivate to bootstrap test: {rr.status_code} {rr.text}")
            return 1
        token = rr.json()["access_token"]
        ok("Reactivated and got token to start clean state")
    else:
        fail(f"Login failed: {r.status_code} {r.text}")
        return 1

    # ── STEP 2: Deactivate ──
    step(2, "Deactivate account via PUT /me/deactivate")
    r = deactivate(client, token, password)
    if r.status_code == 200:
        ok(f"Deactivation OK (status {r.status_code}): {r.json()}")
    else:
        fail(f"Deactivation failed: {r.status_code} {r.text}")
        failures += 1
        return failures

    # ── STEP 3: Old token must be invalid ──
    step(3, "Old token should be invalid after deactivation (sessions killed)")
    r = me(client, token)
    if r.status_code in (401, 403):
        ok(f"Old token rejected as expected (status {r.status_code})")
    else:
        fail(f"Old token still works after deactivation! status={r.status_code}")
        failures += 1

    # ── STEP 4: Login -> should be blocked with reactivation signal ──
    step(4, "Login should return 403 ACCOUNT_DEACTIVATED")
    r = login(client, username, password)
    detail = ""
    try:
        detail = r.json().get("detail", "")
    except Exception:
        pass
    react_header = r.headers.get("x-reactivation-required") or r.headers.get(
        "X-Reactivation-Required"
    )
    if r.status_code == 403 and detail == "ACCOUNT_DEACTIVATED":
        ok(f"Got 403 ACCOUNT_DEACTIVATED as expected")
        if react_header == "true":
            ok("X-Reactivation-Required: true header is set")
        else:
            fail(f"X-Reactivation-Required header missing or wrong: {react_header!r}")
            failures += 1
    else:
        fail(f"Unexpected response: status={r.status_code} detail={detail!r}")
        failures += 1

    # ── STEP 5: Wrong password on /reactivate -> 401 ──
    step(5, "Reactivate with wrong password should return 401")
    r = reactivate(client, username, password + "_WRONG")
    if r.status_code == 401:
        ok(f"Wrong password correctly rejected (status {r.status_code})")
    else:
        fail(f"Wrong password got unexpected status {r.status_code}: {r.text}")
        failures += 1

    # ── STEP 6: Reactivate with correct credentials -> 200 + Token ──
    step(6, "Reactivate with correct credentials")
    r = reactivate(client, username, password)
    if r.status_code == 200:
        body = r.json()
        if "access_token" in body and body.get("user", {}).get("is_active") is True:
            ok("Reactivation OK -> token received, is_active=True")
            new_token = body["access_token"]
        else:
            fail(f"Reactivation response malformed: {body}")
            failures += 1
            return failures
    else:
        fail(f"Reactivation failed: {r.status_code} {r.text}")
        failures += 1
        return failures

    # ── STEP 7: New token works ──
    step(7, "New token from /reactivate should authenticate")
    r = me(client, new_token)
    if r.status_code == 200 and r.json().get("is_active") is True:
        ok(f"GET /me OK with new token, user is_active=True")
    else:
        fail(f"GET /me failed with new token: {r.status_code} {r.text}")
        failures += 1

    # ── STEP 8: Reactivating an already-active account should 400 ──
    step(8, "Reactivating an already-active account should return 400")
    r = reactivate(client, username, password)
    if r.status_code == 400:
        ok(f"Already-active reactivation rejected (status {r.status_code})")
    else:
        fail(f"Expected 400, got {r.status_code}: {r.text}")
        failures += 1

    # ── STEP 9: Normal login again -> 200 ──
    step(9, "Normal login should work again after reactivation")
    r = login(client, username, password)
    if r.status_code == 200:
        ok(f"Login OK -> token received (status {r.status_code})")
    else:
        fail(f"Login failed after reactivation: {r.status_code} {r.text}")
        failures += 1

    return failures


def main():
    print()
    print("=" * 70)
    print("  Deactivation / Reactivation E2E test")
    print("=" * 70)

    if len(sys.argv) < 3:
        print()
        print("Usage: python scripts/test_deactivation_flow.py <username> <password>")
        print()
        print("Pre-requisites:")
        print("  - Backend running on http://localhost:8000")
        print("  - User must exist, be email_verified, not banned, no 2FA")
        print()
        sys.exit(2)

    username = sys.argv[1]
    password = sys.argv[2]

    failures = run_tests(username, password)

    print()
    print("=" * 70)
    if failures == 0:
        print("  [SUCCESS] All checks passed.")
    else:
        print(f"  [FAILURE] {failures} check(s) failed.")
    print("=" * 70)
    print()
    sys.exit(0 if failures == 0 else 1)


if __name__ == "__main__":
    main()
