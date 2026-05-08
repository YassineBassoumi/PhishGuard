"""
Génère le diagramme de cas d'utilisation du Sprint 4.1 — PhishGuard.

Sprint 4.1 — Sécurité avancée — couvre les user stories suivantes :
  17. Authentification 2FA (activation, désactivation, codes de secours)
  18. Gérer les sessions actives (consultation, révocation simple/globale)
  19. Supprimer mon compte (suppression irréversible avec ré-authentification)

Le diagramme est défini en PlantUML (fichier .puml versionné côté repo) puis
exporté en PNG / SVG / PDF dans le dossier `diagrammes/`.

Pré-requis :
  * Java (>=11) disponible sur le PATH.
  * `plantuml.jar` accessible via la variable d'environnement PLANTUML_JAR
    ou présent dans le dossier courant.
  * `cairosvg` (pip install cairosvg) pour produire le PDF à partir du SVG —
    PlantUML ne génère pas un PDF utilisable par défaut sans dépendances
    Apache FOP supplémentaires.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIAG_DIR = ROOT / "diagrammes"
PUML_FILE = DIAG_DIR / "UC_sprint4_1.puml"


def find_plantuml_jar() -> Path:
    """Localise le jar PlantUML.

    Ordre de recherche :
      1. variable d'environnement PLANTUML_JAR
      2. plantuml.jar dans le dossier courant
      3. /home/ubuntu/tools/plantuml.jar (chemin par défaut sur l'env Devin)
    """
    candidates = []
    env = os.environ.get("PLANTUML_JAR")
    if env:
        candidates.append(Path(env))
    candidates.extend(
        [
            Path.cwd() / "plantuml.jar",
            Path("/home/ubuntu/tools/plantuml.jar"),
        ]
    )
    for c in candidates:
        if c.exists():
            return c
    raise FileNotFoundError(
        "plantuml.jar introuvable. Définissez PLANTUML_JAR ou placez le jar "
        "dans le dossier courant."
    )


def render(fmt: str, jar: Path) -> Path:
    """Exporte le .puml dans le format demandé via PlantUML."""
    cmd = ["java", "-jar", str(jar), f"-t{fmt}", str(PUML_FILE)]
    subprocess.run(cmd, check=True, cwd=str(DIAG_DIR))
    return DIAG_DIR / f"UC_sprint4_1.{fmt}"


def svg_to_pdf(svg_path: Path, pdf_path: Path) -> Path | None:
    """Convertit le SVG en PDF avec cairosvg (étape optionnelle)."""
    try:
        import cairosvg  # type: ignore
    except ImportError:
        print(
            "[avertissement] cairosvg indisponible — étape PDF ignorée. "
            "Installez-le via `pip install cairosvg` pour activer l'export PDF."
        )
        return None
    cairosvg.svg2pdf(url=str(svg_path), write_to=str(pdf_path))
    return pdf_path


def main() -> None:
    if not PUML_FILE.exists():
        raise FileNotFoundError(f"Fichier source absent : {PUML_FILE}")

    jar = find_plantuml_jar()
    print(f"PlantUML jar : {jar}")

    png = render("png", jar)
    print(f"PNG généré   : {png}")

    svg = render("svg", jar)
    print(f"SVG généré   : {svg}")

    pdf = DIAG_DIR / "UC_sprint4_1.pdf"
    svg_to_pdf(svg, pdf)
    print(f"PDF généré   : {pdf}")


if __name__ == "__main__":
    main()
