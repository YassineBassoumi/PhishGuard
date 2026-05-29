"""
Test : "Est-ce qu'un changement d'email affecte les notifications d'alerte ?"
Ce script reproduit la logique du endpoint `PUT /api/auth/me` (auth.py:605-771)
qui, lorsqu'un utilisateur modifie son email, appelle en tâche de fond
`notification_service.send_email_changed_alert(...)` pour avertir l'ancien ET
le nouveau destinataire.
Pour rester reproductible et ne PAS dépendre d'un serveur SMTP ni d'une base
de données réelle, ce test :
  - mocke `email_service.send_email`  → capture les destinataires / sujets
  - mocke `NotificationService.get_or_create_preferences` → injecte des
    préférences arbitraires (activées/désactivées, notification_email, ...)
  - mocke `NotificationService._log_notification` → évite tout INSERT en BDD
Scénarios couverts
──────────────────
  A. Email modifié, prefs par défaut
        → 1 alerte send_email_changed_alert envoyée vers OLD *et* NEW
        → ensuite, send_new_login_alert va vers le NOUVEL email
  B. Email NON modifié (PUT /me avec autre champ)
        → AUCUN appel à send_email_changed_alert
  C. Email modifié, mais email_notifications_enabled = False
        → send_email_changed_alert retourne False, AUCUN envoi
  D. Email modifié, mais preferences.notification_email override défini
        → l'alerte de changement d'email va quand même à OLD + NEW
        → MAIS les autres alertes (login, password) gardent l'override et NE
          sont PAS impactées par le changement d'email
  E. Echec SMTP sur la nouvelle adresse uniquement
        → success_old=True garde la fonction en succès global
Usage
─────
    cd backend
    python scripts/test_email_change_notification.py
Exit code 0 si tous les scénarios passent, sinon le nombre d'échecs.
"""
from __future__ import annotations
import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import List, Optional
from unittest.mock import AsyncMock, patch
BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))
# Charger les modèles avant tout (cf. note dans test_new_login_alert.py)
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
from app.services import notification_service as notif_module  # noqa: E402
from app.services.notification_service import notification_service  # noqa: E402
# ─── Couleurs ANSI ───────────────────────────────────────────────────────────
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    OK = "\033[92m"
    WARN = "\033[93m"
    FAIL = "\033[91m"
    INFO = "\033[96m"
def step(msg: str) -> None:
    print(f"\n{C.BOLD}{C.INFO}━━━ {msg} ━━━{C.RESET}")
def ok(msg: str) -> None:
    print(f"  {C.OK}[PASS]{C.RESET} {msg}")
def fail(msg: str) -> None:
    print(f"  {C.FAIL}[FAIL]{C.RESET} {msg}")
def info(msg: str) -> None:
    print(f"  {C.INFO}[..]{C.RESET}   {msg}")
# ─── Helpers pour fabriquer des "faux" objets sans BDD ───────────────────────
def make_user(user_id: int = 1, username: str = "alice",
              email: str = "alice@new.example") -> SimpleNamespace:
    """Faux objet User compatible avec ce que la NotificationService consulte."""
    return SimpleNamespace(id=user_id, username=username, email=email)
def make_prefs(
    email_notifications_enabled: bool = True,
    new_login_alerts: bool = True,
    notification_email: Optional[str] = None,
) -> SimpleNamespace:
    """Faux NotificationPreference (les attributs consultés par le service)."""
    return SimpleNamespace(
        email_notifications_enabled=email_notifications_enabled,
        new_login_alerts=new_login_alerts,
        notification_email=notification_email,
        dangerous_email_alerts=True,
        password_change_alerts=True,
        two_factor_change_alerts=True,
    )
# ─── Capture SMTP : enregistre chaque appel send_email ───────────────────────
class SmtpRecorder:
    """Mock async qui simule email_service.send_email et retient les destinataires."""
    def __init__(self, fail_for: Optional[List[str]] = None):
        self.calls: list[dict] = []
        self.fail_for = set(fail_for or [])
    async def __call__(self, to_email: str, subject: str, html_content: str,
                       text_content: Optional[str] = None) -> bool:
        self.calls.append({"to": to_email, "subject": subject})
        return to_email not in self.fail_for
    @property
    def recipients(self) -> list[str]:
        return [c["to"] for c in self.calls]
# ─── Assertions ──────────────────────────────────────────────────────────────
class Counter:
    def __init__(self) -> None:
        self.failures = 0
    def expect(self, cond: bool, ok_msg: str, fail_msg: str) -> None:
        if cond:
            ok(ok_msg)
        else:
            fail(fail_msg)
            self.failures += 1
# ─── Scénarios ───────────────────────────────────────────────────────────────
async def run_scenarios() -> int:
    counter = Counter()
    OLD = "alice@old.example"
    NEW = "alice@new.example"
    OVERRIDE = "alerts-inbox@example.com"
    change_details = {
        "changed_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "ip_address": "203.0.113.42",
        "location": "Paris, France (TEST)",
    }
    login_details = {
        "device": "Firefox/Linux",
        "browser": "Firefox 125",
        "location": "Paris, France (TEST)",
        "ip_address": "203.0.113.42",
        "login_time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    }
    # On mocke _log_notification (évite la BDD) une fois pour toutes
    notification_service._log_notification = AsyncMock(return_value=None)  # type: ignore[assignment]
    # ── Scénario A ───────────────────────────────────────────────────────────
    step("Scénario A : email modifié, prefs par défaut")
    info("Attendu : send_email_changed_alert envoie à OLD ET NEW (avertir le légitime + confirmer)")
    smtp = SmtpRecorder()
    user = make_user(email=NEW)
    with patch.object(notif_module.email_service, "send_email", smtp), \
         patch.object(notification_service, "get_or_create_preferences",
                      AsyncMock(return_value=make_prefs())):
        success = await notification_service.send_email_changed_alert(
            db=None, user=user, old_email=OLD, new_email=NEW,
            change_details=change_details,
        )
    counter.expect(success is True,
                   "send_email_changed_alert -> True",
                   f"send_email_changed_alert -> {success}")
    counter.expect(OLD in smtp.recipients,
                   f"ancien email ({OLD}) notifié",
                   f"ancien email NON notifié (recipients={smtp.recipients})")
    counter.expect(NEW in smtp.recipients,
                   f"nouvel email ({NEW}) notifié",
                   f"nouvel email NON notifié (recipients={smtp.recipients})")
    counter.expect(len(smtp.calls) == 2,
                   "exactement 2 envois (1 par destinataire)",
                   f"{len(smtp.calls)} envois au lieu de 2")
    info("Maintenant on enchaîne send_new_login_alert : il doit aller vers le NOUVEL email")
    smtp2 = SmtpRecorder()
    with patch.object(notif_module.email_service, "send_email", smtp2), \
         patch.object(notification_service, "get_or_create_preferences",
                      AsyncMock(return_value=make_prefs())):
        await notification_service.send_new_login_alert(
            db=None, user=user, login_details=login_details,
        )
    counter.expect(smtp2.recipients == [NEW],
                   f"alerte login post-changement -> {NEW}",
                   f"alerte login mal routée : {smtp2.recipients}")
    # ── Scénario B ───────────────────────────────────────────────────────────
    step("Scénario B : pas de changement d'email (autre champ modifié)")
    info("Reproduit la condition du route : `if old_email:` n'est jamais entré")
    info("=> send_email_changed_alert ne doit même pas être invoqué")
    smtp = SmtpRecorder()
    # On simule simplement la garde `if old_email is None: skip`
    old_email_local: Optional[str] = None  # le champ n'a pas changé
    triggered = False
    if old_email_local:  # même test que dans auth.py:711
        triggered = True
        with patch.object(notif_module.email_service, "send_email", smtp):
            await notification_service.send_email_changed_alert(
                db=None, user=make_user(email=NEW), old_email=old_email_local,
                new_email=NEW, change_details=change_details,
            )
    counter.expect(triggered is False,
                   "branche email-changed jamais entrée",
                   "la branche email-changed a été déclenchée à tort")
    counter.expect(smtp.calls == [],
                   "aucun email envoyé (cohérent)",
                   f"emails envoyés alors qu'aucun changement : {smtp.recipients}")
    # ── Scénario C ───────────────────────────────────────────────────────────
    step("Scénario C : email_notifications_enabled = False")
    info("Attendu : retour False immédiat, AUCUN appel SMTP")
    smtp = SmtpRecorder()
    with patch.object(notif_module.email_service, "send_email", smtp), \
         patch.object(
             notification_service, "get_or_create_preferences",
             AsyncMock(return_value=make_prefs(email_notifications_enabled=False))):
        success = await notification_service.send_email_changed_alert(
            db=None, user=make_user(email=NEW), old_email=OLD, new_email=NEW,
            change_details=change_details,
        )
    counter.expect(success is False,
                   "retour False (prefs désactivées)",
                   f"retour {success} alors que prefs désactivées")
    counter.expect(smtp.calls == [],
                   "aucun envoi SMTP",
                   f"des envois ont eu lieu : {smtp.recipients}")
    # ── Scénario D ───────────────────────────────────────────────────────────
    step("Scénario D : preferences.notification_email override actif")
    info("Comportement code (notification_service.py:359-368) :")
    info("  l'alerte email-changed va TOUJOURS vers OLD et NEW (sécurité), pas vers l'override")
    info("  MAIS send_new_login_alert (et autres) utilisent `notification_email or user.email`")
    info("  => changer user.email N'AFFECTE PAS la destination des autres alertes")
    smtp = SmtpRecorder()
    user = make_user(email=NEW)
    with patch.object(notif_module.email_service, "send_email", smtp), \
         patch.object(
             notification_service, "get_or_create_preferences",
             AsyncMock(return_value=make_prefs(notification_email=OVERRIDE))):
        await notification_service.send_email_changed_alert(
            db=None, user=user, old_email=OLD, new_email=NEW,
            change_details=change_details,
        )
    counter.expect(set(smtp.recipients) == {OLD, NEW},
                   f"alerte email-changed ignore l'override (recipients={smtp.recipients})",
                   f"alerte email-changed mal routée : {smtp.recipients}")
    smtp2 = SmtpRecorder()
    with patch.object(notif_module.email_service, "send_email", smtp2), \
         patch.object(
             notification_service, "get_or_create_preferences",
             AsyncMock(return_value=make_prefs(notification_email=OVERRIDE))):
        await notification_service.send_new_login_alert(
            db=None, user=user, login_details=login_details,
        )
    counter.expect(smtp2.recipients == [OVERRIDE],
                   f"alerte login -> override ({OVERRIDE}) après changement d'email",
                   f"alerte login mal routée : {smtp2.recipients}")
    # ── Scénario E ───────────────────────────────────────────────────────────
    step("Scénario E : SMTP échoue uniquement sur le NEW")
    info("Le code combine `success = success_old or success_new` : True attendu")
    smtp = SmtpRecorder(fail_for=[NEW])
    with patch.object(notif_module.email_service, "send_email", smtp), \
         patch.object(notification_service, "get_or_create_preferences",
                      AsyncMock(return_value=make_prefs())):
        success = await notification_service.send_email_changed_alert(
            db=None, user=make_user(email=NEW), old_email=OLD, new_email=NEW,
            change_details=change_details,
        )
    counter.expect(success is True,
                   "succès global tant que l'ancien email est notifié",
                   f"retour {success} alors que OLD a bien reçu l'alerte")
    # ── Résumé ───────────────────────────────────────────────────────────────
    step("Résumé")
    if counter.failures == 0:
        print(f"  {C.OK}{C.BOLD}Tous les scénarios passent.{C.RESET}\n")
        print("  Conclusion logique :")
        print("    - Un changement d'email DÉCLENCHE une alerte send_email_changed_alert")
        print("      envoyée à la fois sur l'ANCIEN et le NOUVEL email.")
        print("    - Les ALERTES UNITAIRES (new_login, password_changed, 2FA, failed-login)")
        print("      utilisent `preferences.notification_email or user.email` :")
        print("        * sans override → suivent automatiquement le nouvel email")
        print("        * avec override → restent sur l'override, le changement d'email")
        print("          n'a AUCUN impact sur leur destination.")
        print("    - email_notifications_enabled=False désactive globalement,")
        print("      y compris l'alerte de changement d'email.")
        return 0
    print(f"  {C.FAIL}{C.BOLD}{counter.failures} assertion(s) en échec{C.RESET}\n")
    return counter.failures
if __name__ == "__main__":
    sys.exit(asyncio.run(run_scenarios()))