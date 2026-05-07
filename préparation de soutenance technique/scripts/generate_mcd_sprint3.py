"""
Génère le MCD (Modèle Conceptuel de Données) du Sprint 3 — PhishGuard.

Style Merise inspiré de l'exemple fourni :
  * entités : rectangles avec en-tête bleu clair + liste d'attributs
  * associations : losanges blancs portant un verbe
  * cardinalités : étiquettes (0,n / 1,n / 1,1) sur les arêtes

Périmètre Sprint 3 (Intégration Gmail / Outlook & traitement à grande échelle) :
  - Connecter un compte Gmail / Outlook (OAuth 2.0)
  - Stockage des tokens (UserEmailCredential)
  - Consultation de la boîte email connectée
  - Analyse en masse (multi-sélection depuis la boîte ou saisie manuelle)
  - Historique des analyses, statistiques, notifications
"""
from graphviz import Digraph
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent.parent / "diagrammes"
OUT_DIR.mkdir(exist_ok=True)

ENTITY_HEADER_BG = "#7FB3D5"   # bleu clair (en-tête)
ENTITY_HEADER_FG = "#FFFFFF"
ENTITY_BODY_BG = "#FFFFFF"
ENTITY_BORDER = "#1F4E79"

ASSOC_BG = "#FFFFFF"
ASSOC_BORDER = "#1F4E79"


def entity_node(name: str, attrs: list[tuple[str, str]]) -> str:
    """Construit une étiquette HTML-like Graphviz pour une entité Merise."""
    rows = ""
    for key, typ in attrs:
        rows += (
            f'<TR><TD ALIGN="LEFT" BGCOLOR="{ENTITY_BODY_BG}" '
            f'PORT="{key}">'
            f'<FONT POINT-SIZE="10">{key}</FONT>'
            f'<FONT POINT-SIZE="9" COLOR="#666666">  : {typ}</FONT>'
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
                ("id", "Integer (PK)"),
                ("email", "String (unique)"),
                ("username", "String (unique)"),
                ("hashedPassword", "String"),
                ("role", "Enum (USER/ADMIN/SUPERADMIN)"),
                ("isActive", "Boolean"),
                ("isBanned", "Boolean"),
                ("emailVerified", "Boolean"),
                ("twoFactorEnabled", "Boolean"),
                ("profilePicture", "String"),
                ("createdAt", "DateTime"),
                ("lastLogin", "DateTime"),
            ],
        ),
        shape="plaintext",
    )

    g.node(
        "FournisseurEmail",
        label=entity_node(
            "FournisseurEmail",
            [
                ("id", "Integer (PK)"),
                ("providerName", "String (unique)"),
                ("oauthAuthorizeUrl", "Text"),
                ("oauthTokenUrl", "Text"),
                ("apiBaseUrl", "Text"),
                ("scopes", "Text"),
                ("isActive", "Boolean"),
                ("createdAt", "DateTime"),
            ],
        ),
        shape="plaintext",
    )

    g.node(
        "IdentifiantEmail",
        label=entity_node(
            "IdentifiantEmail",
            [
                ("id", "Integer (PK)"),
                ("provider", "String"),
                ("accessToken", "Text (chiffré)"),
                ("refreshToken", "Text (chiffré)"),
                ("tokenExpiry", "DateTime"),
                ("emailAddress", "String"),
                ("createdAt", "DateTime"),
                ("updatedAt", "DateTime"),
            ],
        ),
        shape="plaintext",
    )

    g.node(
        "EmailImporte",
        label=entity_node(
            "EmailImporté",
            [
                ("messageId", "String (PK)"),
                ("subject", "String"),
                ("sender", "String"),
                ("recipient", "String"),
                ("snippet", "Text"),
                ("body", "Text"),
                ("receivedAt", "DateTime"),
                ("hasAttachments", "Boolean"),
            ],
        ),
        shape="plaintext",
    )

    g.node(
        "LotAnalyse",
        label=entity_node(
            "LotAnalyse",
            [
                ("id", "Integer (PK)"),
                ("source", "Enum (manuel/gmail/outlook)"),
                ("totalItems", "Integer"),
                ("safeCount", "Integer"),
                ("suspiciousCount", "Integer"),
                ("dangerousCount", "Integer"),
                ("startedAt", "DateTime"),
                ("completedAt", "DateTime"),
            ],
        ),
        shape="plaintext",
    )

    g.node(
        "Analyse",
        label=entity_node(
            "Analyse",
            [
                ("id", "Integer (PK)"),
                ("analysisType", "Enum (email/url)"),
                ("contentPreview", "Text"),
                ("threatLevel", "Enum (safe/suspicious/dangerous)"),
                ("confidence", "Float"),
                ("features", "JSON"),
                ("recommendations", "JSON"),
                ("createdAt", "DateTime"),
            ],
        ),
        shape="plaintext",
    )

    g.node(
        "Statistique",
        label=entity_node(
            "Statistique",
            [
                ("id", "Integer (PK)"),
                ("totalAnalyses", "Integer"),
                ("threatsDetected", "Integer"),
                ("emailsAnalyzed", "Integer"),
                ("urlsAnalyzed", "Integer"),
                ("lastUpdated", "DateTime"),
            ],
        ),
        shape="plaintext",
    )

    g.node(
        "Notification",
        label=entity_node(
            "Notification",
            [
                ("id", "Integer (PK)"),
                ("type", "String"),
                ("title", "String"),
                ("message", "Text"),
                ("severity", "Enum (info/warn/error)"),
                ("isRead", "Boolean"),
                ("createdAt", "DateTime"),
            ],
        ),
        shape="plaintext",
    )

    g.node(
        "JournalAudit",
        label=entity_node(
            "JournalAudit",
            [
                ("id", "Integer (PK)"),
                ("action", "String"),
                ("resource", "String"),
                ("details", "JSON"),
                ("ipAddress", "String"),
                ("status", "Enum (success/fail)"),
                ("createdAt", "DateTime"),
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
    assoc("a_possede", "possède")
    assoc("a_recoit", "reçoit")
    assoc("a_genere", "génère")

    # ─── Arêtes avec cardinalités ───────────────────────────────────────────
    edge_attr = {"arrowhead": "none", "arrowtail": "none", "dir": "none"}

    # Utilisateur ─(0,n)─ se_connecte ─(0,n)─ FournisseurEmail
    # via la classe-association IdentifiantEmail
    g.edge("Utilisateur", "a_connecte", taillabel="0,n", **edge_attr)
    g.edge("a_connecte", "FournisseurEmail", headlabel="0,n", **edge_attr)
    # IdentifiantEmail est porté par l'association se_connecte (classe-association)
    g.edge("a_connecte", "IdentifiantEmail",
           style="dashed", arrowhead="none", arrowtail="none", dir="none",
           color="#777777", label="(porte les attributs)")

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
    with g.subgraph() as s:
        s.attr(rank="same")
        s.node("Statistique")
        s.node("Notification")
        s.node("JournalAudit")

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

    # Utilisateur ─(1,1)─ possède ─(1,1)─ Statistique
    g.edge("Utilisateur", "a_possede", taillabel="1,1", **edge_attr)
    g.edge("a_possede", "Statistique", headlabel="1,1", **edge_attr)

    # Utilisateur ─(1,n)─ reçoit ─(1,1)─ Notification
    g.edge("Utilisateur", "a_recoit", taillabel="1,n", **edge_attr)
    g.edge("a_recoit", "Notification", headlabel="1,1", **edge_attr)

    # Utilisateur ─(1,n)─ génère ─(1,1)─ JournalAudit
    g.edge("Utilisateur", "a_genere", taillabel="1,n", **edge_attr)
    g.edge("a_genere", "JournalAudit", headlabel="1,1", **edge_attr)

    return g


if __name__ == "__main__":
    g = build_mcd_sprint3()
    out = g.render(filename=str(OUT_DIR / "MCD_sprint3"), cleanup=True, format="png")
    print(f"MCD généré : {out}")
    out_pdf = g.render(filename=str(OUT_DIR / "MCD_sprint3"), cleanup=True, format="pdf")
    print(f"MCD PDF    : {out_pdf}")
    out_svg = g.render(filename=str(OUT_DIR / "MCD_sprint3"), cleanup=True, format="svg")
    print(f"MCD SVG    : {out_svg}")
