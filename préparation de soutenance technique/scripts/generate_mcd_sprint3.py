"""
Génère le MCD (Modèle Conceptuel de Données) du Sprint 3 — PhishGuard.

Style Merise (pur conceptuel, conforme à la convention de l'exemple fourni) :
  * entités : rectangles avec en-tête bleu clair + liste d'attributs
              (uniquement les NOMS — aucun type technique, aucun (PK))
  * identifiant : attribut SOULIGNÉ (convention Merise)
  * associations : losanges blancs portant un verbe
  * cardinalités : étiquettes (0,n / 1,n / 1,1 / 0,1) sur les arêtes

Périmètre Sprint 3 (Intégration Gmail / Outlook & traitement à grande échelle) :
  - Connecter un compte Gmail / Outlook (OAuth 2.0)
  - Stockage des tokens (classe-association IdentifiantEmail)
  - Consultation de la boîte email connectée
  - Analyse en masse (multi-sélection depuis la boîte ou saisie manuelle)
  - Historique d'analyse (Analyse) avec regroupement en lots (LotAnalyse)

Entités volontairement exclues du MCD du sprint 3 :
  - JournalAudit : entité purement technique (sécurité/conformité)
  - Notification, Statistique : non visibles dans les cas d'usage
    de ce sprint (le MCD décrit le périmètre fonctionnel du sprint).
"""
from graphviz import Digraph
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent.parent / "diagrammes"
OUT_DIR.mkdir(exist_ok=True)

ENTITY_HEADER_BG = "#7FB3D5"
ENTITY_HEADER_FG = "#FFFFFF"
ENTITY_BODY_BG = "#FFFFFF"
ENTITY_BORDER = "#1F4E79"

ASSOC_BG = "#FFFFFF"
ASSOC_BORDER = "#1F4E79"


def entity_node(name: str, attrs: list[str], identifier: str = "id") -> str:
    """Construit une étiquette HTML-like pour une entité Merise.

    Convention : nom seul pour chaque attribut, identifiant souligné.
    """
    rows = ""
    for attr in attrs:
        if attr == identifier:
            content = f"<U>{attr}</U>"
        else:
            content = attr
        rows += (
            f'<TR><TD ALIGN="LEFT" BGCOLOR="{ENTITY_BODY_BG}">'
            f'<FONT POINT-SIZE="11">{content}</FONT>'
            f"</TD></TR>"
        )
    label = (
        '<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" '
        f'COLOR="{ENTITY_BORDER}">'
        f'<TR><TD BGCOLOR="{ENTITY_HEADER_BG}" ALIGN="CENTER">'
        f'<FONT COLOR="{ENTITY_HEADER_FG}" POINT-SIZE="13"><B>{name}</B></FONT>'
        "</TD></TR>"
        f"{rows}"
        "</TABLE>>"
    )
    return label


def build_mcd_sprint3() -> Digraph:
    g = Digraph("MCD_Sprint3", format="png")
    g.attr(
        rankdir="TB",
        splines="polyline",
        nodesep="0.5",
        ranksep="0.9",
        fontname="Helvetica",
        bgcolor="white",
        concentrate="false",
    )
    g.attr("node", fontname="Helvetica")
    g.attr("edge", fontname="Helvetica", fontsize="10", color="#333333")

    # ─── Entités ────────────────────────────────────────────────────────────
    g.node(
        "Utilisateur",
        label=entity_node(
            "Utilisateur",
            [
                "id",
                "email",
                "username",
                "role",
            ],
        ),
        shape="plaintext",
    )

    g.node(
        "FournisseurEmail",
        label=entity_node(
            "FournisseurEmail",
            [
                "id",
                "nom",
                "urlAutorisation",
                "urlToken",
                "urlApi",
                "scopes",
                "estActif",
                "dateCreation",
            ],
        ),
        shape="plaintext",
    )

    g.node(
        "IdentifiantEmail",
        label=entity_node(
            "IdentifiantEmail",
            [
                "id",
                "accessToken",
                "refreshToken",
                "expirationToken",
                "adresseEmail",
                "dateCreation",
                "dateMiseAJour",
            ],
        ),
        shape="plaintext",
    )

    g.node(
        "EmailImporte",
        label=entity_node(
            "EmailImporté",
            [
                "messageId",
                "sujet",
                "expediteur",
                "destinataire",
                "apercu",
                "corps",
                "dateReception",
                "aPiecesJointes",
            ],
            identifier="messageId",
        ),
        shape="plaintext",
    )

    g.node(
        "LotAnalyse",
        label=entity_node(
            "LotAnalyse",
            [
                "id",
                "source",
                "nbTotal",
                "nbSafe",
                "nbSuspicious",
                "nbDangerous",
                "dateDebut",
                "dateFin",
            ],
        ),
        shape="plaintext",
    )

    g.node(
        "Analyse",
        label=entity_node(
            "Analyse",
            [
                "id",
                "typeAnalyse",
                "apercuContenu",
                "niveauMenace",
                "confiance",
                "caracteristiques",
                "recommandations",
                "dateCreation",
            ],
        ),
        shape="plaintext",
    )

    # ─── Associations (losanges) ────────────────────────────────────────────
    def assoc(name: str, label: str):
        g.node(
            name,
            label=label,
            shape="diamond",
            style="filled",
            fillcolor=ASSOC_BG,
            color=ASSOC_BORDER,
            fontname="Helvetica-Bold",
            fontsize="11",
            margin="0.2,0.05",
        )

    assoc("a_connecte", "se_connecte")
    assoc("a_importe", "importe")
    assoc("a_provient", "provient_de")
    assoc("a_lance", "lance")
    assoc("a_contient", "contient")
    assoc("a_concerne", "concerne")
    assoc("a_effectue", "effectue")

    # ─── Arêtes avec cardinalités ───────────────────────────────────────────
    edge_attr = {"arrowhead": "none", "arrowtail": "none", "dir": "none"}

    # Utilisateur ─(0,n)─ se_connecte ─(0,n)─ FournisseurEmail
    # via la classe-association IdentifiantEmail
    g.edge("Utilisateur", "a_connecte", taillabel="0,n", **edge_attr)
    g.edge("a_connecte", "FournisseurEmail", headlabel="0,n", **edge_attr)
    g.edge("a_connecte", "IdentifiantEmail",
           style="dashed", arrowhead="none", arrowtail="none", dir="none",
           color="#777777")

    # Groupes de rangs pour un layout plus lisible
    with g.subgraph() as s:
        s.attr(rank="same")
        s.node("Utilisateur")
        s.node("FournisseurEmail")
    with g.subgraph() as s:
        s.attr(rank="same")
        s.node("IdentifiantEmail")
        s.node("EmailImporte")
    with g.subgraph() as s:
        s.attr(rank="same")
        s.node("LotAnalyse")
        s.node("Analyse")

    # Utilisateur ─(1,n)─ importe ─(1,1)─ EmailImporté
    g.edge("Utilisateur", "a_importe", taillabel="1,n", **edge_attr)
    g.edge("a_importe", "EmailImporte", headlabel="1,1", **edge_attr)

    # EmailImporté ─(1,1)─ provient_de ─(1,n)─ FournisseurEmail
    g.edge("EmailImporte", "a_provient", taillabel="1,1", **edge_attr)
    g.edge("a_provient", "FournisseurEmail", headlabel="1,n", **edge_attr)

    # Utilisateur ─(1,n)─ lance ─(1,1)─ LotAnalyse
    g.edge("Utilisateur", "a_lance", taillabel="1,n", **edge_attr)
    g.edge("a_lance", "LotAnalyse", headlabel="1,1", **edge_attr)

    # LotAnalyse ─(1,n)─ contient ─(0,1)─ Analyse
    g.edge("LotAnalyse", "a_contient", taillabel="1,n", **edge_attr)
    g.edge("a_contient", "Analyse", headlabel="0,1", **edge_attr)

    # Analyse ─(0,1)─ concerne ─(0,n)─ EmailImporté
    g.edge("Analyse", "a_concerne", taillabel="0,1", **edge_attr)
    g.edge("a_concerne", "EmailImporte", headlabel="0,n", **edge_attr)

    # Utilisateur ─(1,n)─ effectue ─(1,1)─ Analyse
    g.edge("Utilisateur", "a_effectue", taillabel="1,n", **edge_attr)
    g.edge("a_effectue", "Analyse", headlabel="1,1", **edge_attr)

    return g


if __name__ == "__main__":
    g = build_mcd_sprint3()
    out = g.render(filename=str(OUT_DIR / "MCD_sprint3"), cleanup=True, format="png")
    print(f"MCD généré : {out}")
    out_pdf = g.render(filename=str(OUT_DIR / "MCD_sprint3"), cleanup=True, format="pdf")
    print(f"MCD PDF    : {out_pdf}")
    out_svg = g.render(filename=str(OUT_DIR / "MCD_sprint3"), cleanup=True, format="svg")
    print(f"MCD SVG    : {out_svg}")
