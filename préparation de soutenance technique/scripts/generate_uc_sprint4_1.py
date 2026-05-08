"""
Génère le diagramme de cas d'utilisation du Sprint 4.1 — PhishGuard.

Sprint 4.1 — Sécurité avancée — couvre les user stories suivantes :
  17. Authentification 2FA (activation, désactivation, codes de secours)
  18. Gérer les sessions actives (consultation, révocation simple/globale)
  19. Supprimer mon compte (suppression irréversible avec ré-authentification)

Le diagramme est défini dans `diagrammes/UC_sprint4_1.drawio` (format draw.io,
ouvrable sur https://app.diagrams.net) puis exporté en PNG / SVG / PDF dans le
même dossier.

Pré-requis :
  * draw.io desktop (CLI `drawio`) accessible via :
      - la variable d'environnement DRAWIO_BIN, OU
      - `drawio` dans le PATH, OU
      - l'AppImage extraite à `/home/ubuntu/tools/squashfs-root/drawio`
        (chemin par défaut sur l'environnement Devin).

  Sur une machine sans FUSE, on extrait l'AppImage avec :
      ./drawio.AppImage --appimage-extract
  puis on appelle directement `squashfs-root/drawio --no-sandbox ...`.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIAG_DIR = ROOT / "diagrammes"
DRAWIO_FILE = DIAG_DIR / "UC_sprint4_1.drawio"


def find_drawio_bin() -> list[str]:
    """Localise l'exécutable drawio.

    Ordre de recherche :
      1. variable d'environnement DRAWIO_BIN
      2. `drawio` dans le PATH
      3. /home/ubuntu/tools/squashfs-root/drawio (AppImage extraite par défaut)
    """
    env = os.environ.get("DRAWIO_BIN")
    if env and Path(env).exists():
        return [env, "--no-sandbox"]

    which = shutil.which("drawio")
    if which:
        return [which, "--no-sandbox"]

    fallback = Path("/home/ubuntu/tools/squashfs-root/drawio")
    if fallback.exists():
        return [str(fallback), "--no-sandbox"]

    raise FileNotFoundError(
        "Binaire drawio introuvable. Définissez DRAWIO_BIN, installez "
        "drawio-desktop, ou extrayez l'AppImage dans /home/ubuntu/tools/."
    )


def render(fmt: str, drawio_cmd: list[str]) -> Path:
    """Exporte le .drawio dans le format demandé via drawio-desktop CLI."""
    out = DIAG_DIR / f"UC_sprint4_1.{fmt}"
    cmd = [
        *drawio_cmd,
        "-x",
        "-f",
        fmt,
        "-o",
        str(out),
        str(DRAWIO_FILE),
    ]
    subprocess.run(cmd, check=True, cwd=str(DIAG_DIR))
    return out


def main() -> None:
    if not DRAWIO_FILE.exists():
        raise FileNotFoundError(f"Fichier source absent : {DRAWIO_FILE}")

    drawio_cmd = find_drawio_bin()
    print(f"draw.io CLI  : {' '.join(drawio_cmd)}")

    for fmt in ("png", "svg", "pdf"):
        out = render(fmt, drawio_cmd)
        print(f"{fmt.upper():3s} généré   : {out}")


if __name__ == "__main__":
    main()
