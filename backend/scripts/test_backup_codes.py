"""
End-to-end test for backup codes during 2FA login.

Tests:
  1. Login normally (no 2FA yet)
  2. Setup 2FA (get secret + backup codes)
  3. Enable 2FA using a valid TOTP code
  4. Attempt login without 2FA code -> 403 "2FA code required"
  5. Attempt login with wrong code -> 401
  6. Login with a backup code (format XXXX-XXXX) -> 200
  7. Verify the used backup code is consumed (count decreased)
  8. Login with the SAME backup code again -> 401 (consumed)
  9. Login with a SECOND backup code (without hyphen) -> 200
  10. Disable 2FA (cleanup)

Usage:
  python scripts/test_backup_codes.py <username> <password>

Pre-requisites:
  - Backend running on http://localhost:8000
  - User must exist, email_verified, is_active, NOT banned, 2FA currently OFF
"""

import sys
import httpx
import pyotp

BASE = "http://localhost:8000/api"


def step(num: int, title: str):
    print(f"\n{'─' * 70}\n  STEP {num}: {title}\n{'─' * 70}")


def ok(msg: str):
    print(f"  [OK] {msg}")


def fail(msg: str):
    print(f"  [FAIL] {msg}")


def info(msg: str):
    print(f"  [..] {msg}")


def login(client: httpx.Client, username: str, password: str, code: str = None) -> httpx.Response:
    data = {"username": username, "password": password}
    if code:
        data["scope"] = code
    return client.post(
        f"{BASE}/auth/login",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )


def run_tests(username: str, password: str) -> int:
    client = httpx.Client(timeout=15.0)
    failures = 0

    # ── STEP 1: Login (no 2FA) ──
    step(1, "Login normally (2FA must be OFF)")
    r = login(client, username, password)
    if r.status_code == 200:
        token = r.json()["access_token"]
        ok(f"Login OK, token received")
    else:
        fail(f"Login failed: {r.status_code} {r.text}")
        return 1

    headers = {"Authorization": f"Bearer {token}"}

    # ── STEP 2: Setup 2FA ──
    step(2, "Setup 2FA -> get secret + backup codes")
    r = client.post(f"{BASE}/2fa/setup", headers=headers)
    if r.status_code == 200:
        setup_data = r.json()
        secret = setup_data["secret"]
        backup_codes = setup_data["backup_codes"]
        ok(f"Setup OK: secret={secret[:8]}..., {len(backup_codes)} backup codes generated")
        info(f"Backup codes: {backup_codes}")
    else:
        fail(f"Setup failed: {r.status_code} {r.text}")
        return 1

    # ── STEP 3: Enable 2FA with valid TOTP ──
    step(3, "Enable 2FA with valid TOTP code")
    totp = pyotp.TOTP(secret)
    valid_code = totp.now()
    r = client.post(
        f"{BASE}/2fa/enable",
        headers={**headers, "Content-Type": "application/json"},
        json={"token": valid_code}
    )
    if r.status_code == 200:
        ok(f"2FA enabled successfully")
    else:
        fail(f"Enable failed: {r.status_code} {r.text}")
        return 1

    # ── STEP 4: Login without 2FA code -> 403 ──
    step(4, "Login without 2FA code -> expect 403 '2FA code required'")
    r = login(client, username, password)
    if r.status_code == 403:
        detail = r.json().get("detail", "")
        if "2FA code required" in detail:
            ok(f"Correctly rejected: {detail}")
        else:
            fail(f"Got 403 but wrong detail: {detail}")
            failures += 1
    else:
        fail(f"Expected 403, got {r.status_code}: {r.text}")
        failures += 1

    # ── STEP 5: Login with wrong code -> 401 ──
    step(5, "Login with wrong 2FA code -> expect 401")
    r = login(client, username, password, "999999")
    if r.status_code == 401:
        ok(f"Wrong code correctly rejected (status 401)")
    else:
        fail(f"Expected 401, got {r.status_code}: {r.text}")
        failures += 1

    # ── STEP 6: Login with backup code (with hyphen) -> 200 ──
    step(6, f"Login with backup code WITH hyphen: '{backup_codes[0]}'")
    r = login(client, username, password, backup_codes[0])
    if r.status_code == 200:
        ok(f"Backup code login SUCCESS! Token received.")
        new_token = r.json()["access_token"]
    else:
        fail(f"Backup code login failed: {r.status_code} {r.text}")
        failures += 1
        # Try to continue with old token
        new_token = token

    # ── STEP 7: Check backup code was consumed ──
    step(7, "Verify backup code was consumed (count decreased)")
    r = client.get(f"{BASE}/2fa/status", headers={"Authorization": f"Bearer {new_token}"})
    if r.status_code == 200:
        remaining = r.json().get("backup_codes_remaining", -1)
        expected = len(backup_codes) - 1
        if remaining == expected:
            ok(f"Backup codes remaining: {remaining} (was {len(backup_codes)}) — correctly consumed")
        else:
            fail(f"Expected {expected} remaining, got {remaining}")
            failures += 1
    else:
        fail(f"Status check failed: {r.status_code} {r.text}")
        failures += 1

    # ── STEP 8: Same backup code again -> 401 ──
    step(8, f"Login with SAME backup code again: '{backup_codes[0]}' -> expect 401")
    r = login(client, username, password, backup_codes[0])
    if r.status_code == 401:
        ok(f"Consumed backup code correctly rejected (status 401)")
    else:
        fail(f"Expected 401, got {r.status_code}: {r.text}")
        failures += 1

    # ── STEP 9: Login with second backup code (WITHOUT hyphen) -> 200 ──
    code_no_hyphen = backup_codes[1].replace("-", "")
    step(9, f"Login with backup code WITHOUT hyphen: '{code_no_hyphen}' (original: '{backup_codes[1]}')")
    r = login(client, username, password, code_no_hyphen)
    if r.status_code == 200:
        ok(f"Backup code (no hyphen) login SUCCESS!")
        new_token = r.json()["access_token"]
    else:
        fail(f"Backup code (no hyphen) login failed: {r.status_code} {r.text}")
        failures += 1

    # ── STEP 10: Disable 2FA (cleanup) ──
    step(10, "Disable 2FA (cleanup)")
    r = client.post(
        f"{BASE}/2fa/disable",
        headers={"Authorization": f"Bearer {new_token}", "Content-Type": "application/json"},
        json={"password": password}
    )
    if r.status_code == 200:
        ok(f"2FA disabled (cleanup done)")
    else:
        fail(f"Disable failed: {r.status_code} {r.text}")
        failures += 1

    return failures


def main():
    print("\n" + "=" * 70)
    print("  Backup Codes E2E Test")
    print("=" * 70)

    if len(sys.argv) < 3:
        print("\nUsage: python scripts/test_backup_codes.py <username> <password>")
        print("\nPre-requisites:")
        print("  - Backend running on http://localhost:8000")
        print("  - User exists, email_verified, is_active, NOT banned, 2FA OFF")
        sys.exit(2)

    username = sys.argv[1]
    password = sys.argv[2]

    failures = run_tests(username, password)

    print("\n" + "=" * 70)
    if failures == 0:
        print("  [SUCCESS] All 10 checks passed.")
    else:
        print(f"  [FAILURE] {failures} check(s) failed.")
    print("=" * 70 + "\n")
    sys.exit(0 if failures == 0 else 1)


if __name__ == "__main__":
    main()
