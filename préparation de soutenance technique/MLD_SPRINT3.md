# MLD — Sprint 3 (Intégration Gmail / Outlook & traitement à grande échelle)

> Modèle Logique de Données (MLD) — traduction relationnelle du MCD du sprint 3.
> À insérer dans la section **4.3.3 Conception de la base de données → Modèle logique de données (MLD)** du rapport.

## Image du MLD

![MLD Sprint 3](diagrammes/MLD_sprint3.png)

> Versions exportées dans `diagrammes/` :
> - `MLD_sprint3.png` — pour insertion dans Word / Markdown
> - `MLD_sprint3.pdf` — pour insertion vectorielle dans LaTeX (`\includegraphics`)
> - `MLD_sprint3.svg` — version vectorielle éditable
>
> Pour régénérer le diagramme : `python3 "préparation de soutenance technique/scripts/generate_mld_sprint3.py"`

---

## Conventions de notation

- **Tables** : rectangles avec en-tête bleu foncé et nom en `snake_case`.
- **Clé primaire (PK)** : 🔑 icône, ligne en fond crème, identifiant souligné.
- **Clé étrangère (FK)** : 🔗 icône, ligne en fond bleu clair, flèche vers la PK référencée.
- **Cardinalité graphique** : extrémité « patte d'oie » (crow's foot) côté `n`, simple barre côté `1`.
- **Notation textuelle classique** :
  ```
  table(#pk, attr1, attr2, #fk_xxx → table_cible.pk)
  ```
  où `#` indique une clé (PK ou FK).

---

## Règles de passage MCD → MLD appliquées

| Règle Merise | Application sprint 3 |
|---|---|
| Une **entité** devient une **table** ; son identifiant devient la **PK**. | `utilisateur`, `fournisseur_email`, `email_importe`, `lot_analyse`, `analyse` |
| Une **association (1,n) — (1,1)** se traduit par une **FK** dans la table côté « 1,1 ». | `email_importe.id_utilisateur`, `email_importe.id_fournisseur`, `lot_analyse.id_utilisateur`, `analyse.id_lot` |
| Une **association (0,1) — (0,n)** se traduit par une **FK NULLABLE** dans la table côté « 0,1 ». | `analyse.message_id` (NULLABLE car analyse manuelle = pas d'email source) |
| Une **classe-association (n,n)** devient une **table dédiée** avec FK vers chaque entité + ses propres attributs. | `identifiant_email` |

---

## Description des relations (6)

### 1. `utilisateur`
```
utilisateur(#id_utilisateur, email, username, role)
```
| Colonne | Type logique | Rôle |
|---|---|---|
| **id_utilisateur** (PK) | INT | Identifiant interne |
| email | VARCHAR | Unique |
| username | VARCHAR | Unique |
| role | ENUM ou VARCHAR | `USER` / `ADMIN` / `SUPERADMIN` |

### 2. `fournisseur_email`
```
fournisseur_email(#id_fournisseur, nom, url_autorisation, url_token, url_api, scopes)
```
| Colonne | Type logique | Rôle |
|---|---|---|
| **id_fournisseur** (PK) | INT | Identifiant interne |
| nom | VARCHAR | Unique (`gmail`, `outlook`) |
| url_autorisation | VARCHAR | Endpoint OAuth |
| url_token | VARCHAR | Endpoint d'échange |
| url_api | VARCHAR | API du fournisseur |
| scopes | TEXT | Liste de scopes OAuth |

### 3. `identifiant_email` *(table dédiée — issue de la classe-association)*
```
identifiant_email(
  #id_identifiant,
  #id_utilisateur → utilisateur.id_utilisateur,
  #id_fournisseur → fournisseur_email.id_fournisseur,
  access_token, refresh_token, expiration_token,
  adresse_email
)
```
| Colonne | Type logique | Rôle |
|---|---|---|
| **id_identifiant** (PK) | INT | Identifiant interne |
| **id_utilisateur** (FK) | INT | → `utilisateur.id_utilisateur` |
| **id_fournisseur** (FK) | INT | → `fournisseur_email.id_fournisseur` |
| access_token | TEXT | Jeton d'accès (chiffré au niveau application) |
| refresh_token | TEXT | Jeton de rafraîchissement (chiffré au niveau application) |
| expiration_token | TIMESTAMP | Date d'expiration |
| adresse_email | VARCHAR | Adresse du compte connecté |

> **Contrainte d'unicité** : `UNIQUE(id_utilisateur, id_fournisseur)` — un même utilisateur ne peut connecter qu'**un seul** compte par fournisseur.

### 4. `email_importe`
```
email_importe(
  #message_id,
  #id_utilisateur → utilisateur.id_utilisateur,
  #id_fournisseur → fournisseur_email.id_fournisseur,
  sujet, expediteur, destinataire,
  apercu, corps,
  date_reception, a_pieces_jointes
)
```
| Colonne | Type logique | Rôle |
|---|---|---|
| **message_id** (PK) | VARCHAR | Identifiant du message côté fournisseur |
| **id_utilisateur** (FK) | INT | → `utilisateur.id_utilisateur` |
| **id_fournisseur** (FK) | INT | → `fournisseur_email.id_fournisseur` |
| sujet | VARCHAR | |
| expediteur | VARCHAR | |
| destinataire | VARCHAR | |
| apercu | TEXT | |
| corps | TEXT | |
| date_reception | TIMESTAMP | |
| a_pieces_jointes | BOOLEAN | |

### 5. `lot_analyse`
```
lot_analyse(
  #id_lot,
  #id_utilisateur → utilisateur.id_utilisateur,
  source, nb_total,
  nb_safe, nb_suspicious, nb_dangerous,
  date_debut, date_fin
)
```
| Colonne | Type logique | Rôle |
|---|---|---|
| **id_lot** (PK) | INT | Identifiant du lot |
| **id_utilisateur** (FK) | INT | → `utilisateur.id_utilisateur` (lanceur du lot) |
| source | VARCHAR | `manuel` / `gmail` / `outlook` |
| nb_total | INT | Nombre d'éléments soumis |
| nb_safe | INT | Compteur Safe |
| nb_suspicious | INT | Compteur Suspicious |
| nb_dangerous | INT | Compteur Dangerous |
| date_debut | TIMESTAMP | |
| date_fin | TIMESTAMP | |

### 6. `analyse`
```
analyse(
  #id_analyse,
  #id_lot → lot_analyse.id_lot,
  #message_id → email_importe.message_id  (NULLABLE),
  type_analyse, apercu_contenu,
  niveau_menace, confiance,
  date_creation
)
```
| Colonne | Type logique | Rôle |
|---|---|---|
| **id_analyse** (PK) | INT | Identifiant de l'analyse |
| **id_lot** (FK) | INT | → `lot_analyse.id_lot` (NOT NULL) |
| **message_id** (FK) | VARCHAR | → `email_importe.message_id` (NULL si saisie manuelle) |
| type_analyse | VARCHAR | En sprint 3, toujours `email` |
| apercu_contenu | TEXT | |
| niveau_menace | VARCHAR | `safe` / `suspicious` / `dangerous` |
| confiance | FLOAT | Score 0–1 |
| date_creation | TIMESTAMP | |

---

## Schéma textuel récapitulatif

```
utilisateur          (#id_utilisateur, email, username, role)
fournisseur_email    (#id_fournisseur, nom, url_autorisation, url_token, url_api, scopes)
identifiant_email    (#id_identifiant,
                      #id_utilisateur → utilisateur.id_utilisateur,
                      #id_fournisseur → fournisseur_email.id_fournisseur,
                      access_token, refresh_token, expiration_token, adresse_email,
                      UNIQUE(id_utilisateur, id_fournisseur))
email_importe        (#message_id,
                      #id_utilisateur → utilisateur.id_utilisateur,
                      #id_fournisseur → fournisseur_email.id_fournisseur,
                      sujet, expediteur, destinataire, apercu, corps,
                      date_reception, a_pieces_jointes)
lot_analyse          (#id_lot,
                      #id_utilisateur → utilisateur.id_utilisateur,
                      source, nb_total, nb_safe, nb_suspicious, nb_dangerous,
                      date_debut, date_fin)
analyse              (#id_analyse,
                      #id_lot → lot_analyse.id_lot,
                      #message_id → email_importe.message_id  (NULL OK),
                      type_analyse, apercu_contenu, niveau_menace,
                      confiance, date_creation)
```

---

## Traçabilité MCD → MLD

| MCD (entité ou association) | MLD (table ou colonne FK) |
|---|---|
| Entité `Utilisateur` | Table `utilisateur` |
| Entité `FournisseurEmail` | Table `fournisseur_email` |
| Classe-association `IdentifiantEmail` (n,n entre Utilisateur et FournisseurEmail) | Table `identifiant_email` + 2 FK + UNIQUE |
| Entité `EmailImporté` | Table `email_importe` |
| Entité `LotAnalyse` | Table `lot_analyse` |
| Entité `Analyse` | Table `analyse` |
| Association `se_connecte` | FKs dans `identifiant_email` |
| Association `importe` (1,1 / 1,n) | FK `email_importe.id_utilisateur` |
| Association `provient_de` (1,1 / 1,n) | FK `email_importe.id_fournisseur` |
| Association `lance` (1,1 / 1,n) | FK `lot_analyse.id_utilisateur` |
| Association `contient` (1,1 / 1,n) | FK `analyse.id_lot` (NOT NULL) |
| Association `concerne` (0,1 / 0,n) | FK `analyse.message_id` (NULLABLE) |

---

## Snippet LaTeX prêt à coller

```latex
\subsection*{Modèle logique de données (MLD)}

À partir du MCD précédent, nous avons procédé au passage au modèle logique
relationnel selon les règles classiques de Merise.

\begin{figure}[H]
    \centering
    \includegraphics[width=\textwidth]{figures/MLD_sprint3.pdf}
    \caption{Modèle Logique de Données du sprint 3}
    \label{fig:mld_sprint3}
\end{figure}

Le schéma logique (figure~\ref{fig:mld_sprint3}) compte 6 relations :
\begin{itemize}
    \item \texttt{utilisateur(\underline{id\_utilisateur}, email, username, role)}
    \item \texttt{fournisseur\_email(\underline{id\_fournisseur}, nom, url\_autorisation, url\_token, url\_api, scopes)}
    \item \texttt{identifiant\_email(\underline{id\_identifiant}, \#id\_utilisateur, \#id\_fournisseur, access\_token, refresh\_token, expiration\_token, adresse\_email)}
    \item \texttt{email\_importe(\underline{message\_id}, \#id\_utilisateur, \#id\_fournisseur, sujet, expediteur, destinataire, apercu, corps, date\_reception, a\_pieces\_jointes)}
    \item \texttt{lot\_analyse(\underline{id\_lot}, \#id\_utilisateur, source, nb\_total, nb\_safe, nb\_suspicious, nb\_dangerous, date\_debut, date\_fin)}
    \item \texttt{analyse(\underline{id\_analyse}, \#id\_lot, \#message\_id, type\_analyse, apercu\_contenu, niveau\_menace, confiance, date\_creation)}
\end{itemize}

La table \textbf{identifiant\_email} est issue de la transformation de la
classe-association du MCD : elle porte les jetons OAuth et matérialise la
liaison \og un utilisateur connecte un compte chez un fournisseur \fg{}.
Une contrainte d'unicité \texttt{UNIQUE(id\_utilisateur, id\_fournisseur)}
garantit qu'un utilisateur ne peut connecter qu'un seul compte par fournisseur.
```

---

## Étapes suivantes

- **MPD / Script SQL** : `CREATE TABLE` PostgreSQL avec types précis (SERIAL, VARCHAR(255), TIMESTAMP, BOOLEAN), index sur les FK, contraintes `NOT NULL` / `UNIQUE`, et migration Alembic. Dis-moi si tu veux que j'enchaîne.
