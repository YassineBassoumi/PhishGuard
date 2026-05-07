"""
Génère le MLD (Modèle Logique de Données) du Sprint 3 — PhishGuard.

Le MLD est la traduction relationnelle du MCD : chaque entité devient une
relation (table) avec une clé primaire ; chaque association (1,n / 1,1)
introduit une clé étrangère ; chaque classe-association ou association n,n
devient une table de jointure.

Convention :
  * tables = rectangles avec en-tête bleu
  * clé primaire (PK) : icône 🔑 + soulignée
  * clé étrangère (FK) : icône 🔗 + flèche vers la table référencée
  * snake_case + préfixe id_xxx pour les identifiants (standard relationnel)
"""
from graphviz import Digraph
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent.parent / "diagrammes"
OUT_DIR.mkdir(exist_ok=True)

HEADER_BG = "#1F4E79"
HEADER_FG = "#FFFFFF"
ROW_BG = "#FFFFFF"
PK_BG = "#FFF8DC"      # crème pour PK
FK_BG = "#E8F4F9"      # bleu très clair pour FK
BORDER = "#1F4E79"

# Description des tables : (nom, [(col_name, kind, port_id)])
# kind ∈ {"pk", "fk", "col"} ; port_id sert d'ancre pour les flèches FK.
TABLES = {
    "utilisateur": [
        ("id_utilisateur", "pk", "pk"),
        ("email", "col", None),
        ("username", "col", None),
        ("role", "col", None),
    ],
    "fournisseur_email": [
        ("id_fournisseur", "pk", "pk"),
        ("nom", "col", None),
        ("url_autorisation", "col", None),
        ("url_token", "col", None),
        ("url_api", "col", None),
        ("scopes", "col", None),
    ],
    "identifiant_email": [
        ("id_identifiant", "pk", "pk"),
        ("id_utilisateur", "fk", "fk_user"),
        ("id_fournisseur", "fk", "fk_provider"),
        ("access_token", "col", None),
        ("refresh_token", "col", None),
        ("expiration_token", "col", None),
        ("adresse_email", "col", None),
    ],
    "email_importe": [
        ("message_id", "pk", "pk"),
        ("id_utilisateur", "fk", "fk_user"),
        ("id_fournisseur", "fk", "fk_provider"),
        ("sujet", "col", None),
        ("expediteur", "col", None),
        ("destinataire", "col", None),
        ("apercu", "col", None),
        ("corps", "col", None),
        ("date_reception", "col", None),
        ("a_pieces_jointes", "col", None),
    ],
    "lot_analyse": [
        ("id_lot", "pk", "pk"),
        ("id_utilisateur", "fk", "fk_user"),
        ("source", "col", None),
        ("nb_total", "col", None),
        ("nb_safe", "col", None),
        ("nb_suspicious", "col", None),
        ("nb_dangerous", "col", None),
        ("date_debut", "col", None),
        ("date_fin", "col", None),
    ],
    "analyse": [
        ("id_analyse", "pk", "pk"),
        ("id_lot", "fk", "fk_lot"),
        ("message_id", "fk", "fk_email"),
        ("type_analyse", "col", None),
        ("apercu_contenu", "col", None),
        ("niveau_menace", "col", None),
        ("confiance", "col", None),
        ("date_creation", "col", None),
    ],
}

# Liste des contraintes FK : (table_source, port_source, table_cible, port_cible)
FOREIGN_KEYS = [
    ("identifiant_email", "fk_user", "utilisateur", "pk"),
    ("identifiant_email", "fk_provider", "fournisseur_email", "pk"),
    ("email_importe", "fk_user", "utilisateur", "pk"),
    ("email_importe", "fk_provider", "fournisseur_email", "pk"),
    ("lot_analyse", "fk_user", "utilisateur", "pk"),
    ("analyse", "fk_lot", "lot_analyse", "pk"),
    ("analyse", "fk_email", "email_importe", "pk"),
]


def render_row(col_name: str, kind: str, port_id: str | None) -> str:
    """Rend une ligne de la table HTML."""
    if kind == "pk":
        bg = PK_BG
        marker = "🔑"
        text = f"<U>{col_name}</U>"
    elif kind == "fk":
        bg = FK_BG
        marker = "🔗"
        text = col_name
    else:
        bg = ROW_BG
        marker = ""
        text = col_name

    port = f' PORT="{port_id}"' if port_id else ""
    marker_cell = (
        f'<TD ALIGN="CENTER" BGCOLOR="{bg}"><FONT POINT-SIZE="9">{marker}</FONT></TD>'
        if marker
        else f'<TD ALIGN="CENTER" BGCOLOR="{bg}"></TD>'
    )
    return (
        f"<TR>"
        f"{marker_cell}"
        f'<TD ALIGN="LEFT" BGCOLOR="{bg}"{port}><FONT POINT-SIZE="11">{text}</FONT></TD>'
        f"</TR>"
    )


def table_label(name: str, columns: list[tuple[str, str, str | None]]) -> str:
    rows = "".join(render_row(c, k, p) for c, k, p in columns)
    return (
        '<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" '
        f'COLOR="{BORDER}" CELLPADDING="3">'
        f'<TR><TD COLSPAN="2" BGCOLOR="{HEADER_BG}" ALIGN="CENTER">'
        f'<FONT COLOR="{HEADER_FG}" POINT-SIZE="13"><B>{name}</B></FONT></TD></TR>'
        f"{rows}"
        "</TABLE>>"
    )


def build_mld_sprint3() -> Digraph:
    g = Digraph("MLD_Sprint3", format="png")
    g.attr(
        rankdir="LR",
        splines="spline",
        nodesep="0.6",
        ranksep="1.2",
        fontname="Helvetica",
        bgcolor="white",
    )
    g.attr("node", fontname="Helvetica", shape="plaintext")
    g.attr("edge", fontname="Helvetica", fontsize="9", color="#1F4E79", arrowsize="0.7")

    for name, cols in TABLES.items():
        g.node(name, label=table_label(name, cols))

    for src, src_port, dst, dst_port in FOREIGN_KEYS:
        g.edge(
            f"{src}:{src_port}:e",
            f"{dst}:{dst_port}:w",
            arrowhead="crow",
            arrowtail="none",
            dir="forward",
            color="#1F4E79",
            penwidth="1.3",
        )

    return g


if __name__ == "__main__":
    g = build_mld_sprint3()
    out = g.render(filename=str(OUT_DIR / "MLD_sprint3"), cleanup=True, format="png")
    print(f"MLD généré : {out}")
    out_pdf = g.render(filename=str(OUT_DIR / "MLD_sprint3"), cleanup=True, format="pdf")
    print(f"MLD PDF    : {out_pdf}")
    out_svg = g.render(filename=str(OUT_DIR / "MLD_sprint3"), cleanup=True, format="svg")
    print(f"MLD SVG    : {out_svg}")
