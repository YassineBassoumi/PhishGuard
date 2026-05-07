"""
Script de diagnostic SMTP pour PhishGuard.

Lit le .env du backend, puis teste chaque étape de l'envoi SMTP en isolation
avec des messages d'erreur clairs pour identifier précisément la cause d'un
échec d'envoi d'email.

Usage :
    cd backend
    python scripts/test_smtp.py [email_destinataire]

Si email_destinataire n'est pas fourni, le script envoie le test à SMTP_USER
(donc à toi-même).
"""

from __future__ import annotations

import os
import smtplib
import socket
import ssl
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv


# ─────────────────────────────────────────────────────────────────────────────
# Couleurs ANSI pour PowerShell (Windows 10+)
# ─────────────────────────────────────────────────────────────────────────────
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    OK = "\033[92m"
    WARN = "\033[93m"
    FAIL = "\033[91m"
    INFO = "\033[96m"


def step(label: str) -> None:
    print(f"\n{C.BOLD}{C.INFO}━━━ {label} ━━━{C.RESET}")


def ok(msg: str) -> None:
    print(f"{C.OK}[OK]{C.RESET} {msg}")


def fail(msg: str) -> None:
    print(f"{C.FAIL}[FAIL]{C.RESET} {msg}")


def warn(msg: str) -> None:
    print(f"{C.WARN}[WARN]{C.RESET} {msg}")


def info(msg: str) -> None:
    print(f"{C.INFO}[..]{C.RESET} {msg}")


# Active les codes ANSI sous Windows
if sys.platform == "win32":
    os.system("")


def main() -> int:
    # ─── Étape 0 : Charger le .env ──────────────────────────────────────────
    step("0. Chargement du fichier .env")

    backend_root = Path(__file__).resolve().parent.parent
    env_path = backend_root / ".env"

    if not env_path.exists():
        fail(f".env introuvable : {env_path}")
        return 1

    ok(f".env trouvé : {env_path}")
    load_dotenv(env_path)

    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port_raw = os.getenv("SMTP_PORT", "")
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    from_email = os.getenv("FROM_EMAIL", smtp_user)
    from_name = os.getenv("FROM_NAME", "PhishGuard AI")

    # ─── Étape 1 : Validation des variables d'environnement ─────────────────
    step("1. Validation des variables")

    issues = []

    if not smtp_host:
        issues.append("SMTP_HOST est vide")
    else:
        ok(f"SMTP_HOST       = {smtp_host}")

    try:
        smtp_port = int(smtp_port_raw)
        ok(f"SMTP_PORT       = {smtp_port}")
    except ValueError:
        issues.append(f"SMTP_PORT n'est pas un entier : '{smtp_port_raw}'")
        smtp_port = 0

    if not smtp_user:
        issues.append("SMTP_USER est vide")
    elif "@" not in smtp_user:
        issues.append(f"SMTP_USER ne contient pas '@' : '{smtp_user}' (doit être l'adresse complète)")
    else:
        ok(f"SMTP_USER       = {smtp_user}")

    if not smtp_password:
        issues.append("SMTP_PASSWORD est vide")
    else:
        # Vérifications spécifiques au mot de passe
        pwd_len = len(smtp_password)
        masked = smtp_password[0] + "*" * (pwd_len - 2) + smtp_password[-1] if pwd_len > 2 else "***"
        ok(f"SMTP_PASSWORD   = {masked}  (longueur : {pwd_len})")

        if " " in smtp_password:
            warn(
                "Le mot de passe contient des ESPACES. Gmail affiche les mots "
                "de passe d'application comme 'abcd efgh ijkl mnop' mais il "
                "faut les coller SANS espaces. Retire les espaces du .env."
            )
            issues.append("Espaces dans SMTP_PASSWORD")

        if smtp_password.startswith('"') or smtp_password.endswith('"'):
            warn("Le mot de passe est entouré de guillemets. Retire-les du .env.")
            issues.append("Guillemets autour de SMTP_PASSWORD")

        if "gmail.com" in smtp_host.lower() and pwd_len != 16:
            warn(
                f"Pour Gmail, un mot de passe d'application fait EXACTEMENT 16 "
                f"caractères. Le tien en fait {pwd_len}. C'est probablement un "
                f"mot de passe Gmail normal, qui n'est plus accepté depuis 2022."
            )

    ok(f"FROM_EMAIL      = {from_email}")
    ok(f"FROM_NAME       = {from_name}")

    if issues:
        fail("Problèmes détectés dans le .env :")
        for issue in issues:
            print(f"   - {issue}")
        print()
        warn("Corrige le .env avant de continuer.")
        return 1

    # ─── Étape 2 : Résolution DNS ───────────────────────────────────────────
    step("2. Résolution DNS du serveur SMTP")
    info(f"Lookup de {smtp_host} ...")
    try:
        ip = socket.gethostbyname(smtp_host)
        ok(f"{smtp_host} → {ip}")
    except socket.gaierror as e:
        fail(f"Résolution DNS échouée : {e}")
        warn("Vérifie ta connexion Internet et que SMTP_HOST est correct.")
        return 1

    # ─── Étape 3 : Connexion TCP ────────────────────────────────────────────
    step("3. Connexion TCP au serveur SMTP")
    info(f"Connexion à {smtp_host}:{smtp_port} ...")
    try:
        sock = socket.create_connection((smtp_host, smtp_port), timeout=10)
        sock.close()
        ok(f"Connexion TCP réussie sur le port {smtp_port}")
    except socket.timeout:
        fail("Timeout — le port est probablement bloqué (pare-feu / antivirus / FAI)")
        return 1
    except ConnectionRefusedError:
        fail(f"Connexion refusée — vérifie que SMTP_PORT={smtp_port} est correct")
        return 1
    except OSError as e:
        fail(f"Erreur réseau : {e}")
        return 1

    # ─── Étape 4 : Handshake SMTP + STARTTLS ────────────────────────────────
    step("4. Handshake SMTP et chiffrement STARTTLS")
    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.set_debuglevel(0)
            code, msg = server.ehlo()
            ok(f"EHLO accepté (code {code})")

            if "starttls" not in [ext.lower() for ext in server.esmtp_features]:
                fail("Le serveur n'annonce pas STARTTLS")
                return 1

            ctx = ssl.create_default_context()
            server.starttls(context=ctx)
            server.ehlo()
            ok("STARTTLS établi (connexion chiffrée)")

            # ─── Étape 5 : LOGIN ────────────────────────────────────────────
            step("5. Authentification SMTP (LOGIN)")
            info(f"Login en tant que {smtp_user} ...")
            try:
                server.login(smtp_user, smtp_password)
                ok(f"{C.BOLD}AUTHENTIFICATION RÉUSSIE !{C.RESET}")
            except smtplib.SMTPAuthenticationError as e:
                fail(f"Login refusé par le serveur : {e.smtp_code} {e.smtp_error.decode(errors='replace')}")

                if e.smtp_code == 535:
                    print()
                    warn("Erreur 535 — Bad Credentials. Causes par ordre de probabilité :")
                    print("   1. Tu utilises ton mot de passe Gmail normal au lieu d'un mot de passe d'application")
                    print("   2. La 2FA n'est pas activée sur le compte Gmail")
                    print("   3. Le mot de passe d'application a été révoqué — régénère-en un nouveau")
                    print("   4. Tu as copié le mot de passe avec des espaces ou des caractères en trop")
                    print()
                    print(f"   Solution : https://myaccount.google.com/apppasswords")
                    print("   Génère un nouveau mot de passe d'application, copie-le SANS espaces, et relance.")

                return 1
            except smtplib.SMTPException as e:
                fail(f"Erreur SMTP imprévue au login : {e}")
                return 1

            # ─── Étape 6 : Envoi d'un email de test ─────────────────────────
            step("6. Envoi d'un email de test")

            recipient = sys.argv[1] if len(sys.argv) > 1 else smtp_user
            info(f"Destinataire : {recipient}")

            message = MIMEMultipart("alternative")
            message["Subject"] = "[PhishGuard] Test SMTP — diagnostic"
            message["From"] = f"{from_name} <{from_email}>"
            message["To"] = recipient

            text = (
                "Ceci est un email de test envoyé par scripts/test_smtp.py "
                "pour vérifier que la configuration SMTP de PhishGuard "
                "fonctionne correctement.\n\n"
                "Si tu lis ce message, l'envoi d'email du backend est "
                "opérationnel. Le bug d'envoi de reset password est donc "
                "résolu côté SMTP."
            )
            html = f"""\
            <html><body style="font-family: sans-serif;">
            <h2 style="color: #2C3E50;">PhishGuard — Test SMTP réussi ✓</h2>
            <p>{text.replace(chr(10), '<br>')}</p>
            <hr>
            <p style="color: #7F8C8D; font-size: 12px;">
                Envoyé depuis <code>scripts/test_smtp.py</code><br>
                Compte expéditeur : <code>{smtp_user}</code><br>
                Serveur : <code>{smtp_host}:{smtp_port}</code>
            </p>
            </body></html>"""

            message.attach(MIMEText(text, "plain"))
            message.attach(MIMEText(html, "html"))

            try:
                server.send_message(message)
                ok(f"{C.BOLD}EMAIL ENVOYÉ AVEC SUCCÈS à {recipient}{C.RESET}")
            except smtplib.SMTPRecipientsRefused as e:
                fail(f"Destinataire(s) refusé(s) : {e.recipients}")
                return 1
            except smtplib.SMTPException as e:
                fail(f"Erreur lors de l'envoi : {e}")
                return 1

    except smtplib.SMTPException as e:
        fail(f"Erreur SMTP : {e}")
        return 1

    # ─── Bilan final ────────────────────────────────────────────────────────
    print()
    print(f"{C.BOLD}{C.OK}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C.RESET}")
    print(f"{C.BOLD}{C.OK}  ✓ TOUTE LA CONFIG SMTP EST OPÉRATIONNELLE{C.RESET}")
    print(f"{C.BOLD}{C.OK}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C.RESET}")
    print()
    print(f"  Vérifie ta boîte mail : {recipient}")
    print(f"  (et le dossier SPAM si tu ne vois rien dans la boîte de réception)")
    print()
    print("  Si l'email est bien arrivé, tu peux maintenant relancer le")
    print("  backend FastAPI et les emails de reset password fonctionneront.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
