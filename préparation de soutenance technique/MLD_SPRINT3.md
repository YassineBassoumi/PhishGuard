# MLD — Sprint 3 (Intégration Gmail / Outlook & traitement à grande échelle)

> Modèle Logique de Données (MLD) **aligné sur le schéma Supabase réel** du backend PhishGuard.
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

- **Noms de tables et colonnes** : exactement ceux du code backend (cf. `backend/app/models/*.py`), donc en **anglais snake_case**.
- **Clé primaire (PK)** : déclarée avec son type logique.
- **Clé étrangère (FK)** : listée dans la rubrique `Relations`.
- **Contraintes** : domaine de valeurs, unicité, nullabilité, comportement ON DELETE.

---

## Périmètre du sprint 3 dans la base réelle

Sur les 11 tables de la base Supabase, **4 sont mobilisées** par les cas d'usage du sprint 3 :

| Table | Sprint d'origine | Rôle dans le sprint 3 |
|---|---|---|
| `users` | sprint 1 | Acteurs (utilisateur, administrateur, super-administrateur) |
| `email_providers` | **sprint 3** | Catalogue des fournisseurs OAuth (Gmail, Outlook) |
| `user_email_credentials` | **sprint 3** | Jetons OAuth d'un utilisateur pour un fournisseur |
| `analysis_history` | sprint 1/2 | Résultats d'analyse (y compris l'analyse en masse) |

> **Choix de conception** : les emails ne sont pas persistés en base. Ils sont récupérés à la volée via Gmail API / Microsoft Graph et restent côté fournisseur. De même, l'analyse en masse insère plusieurs lignes dans `analysis_history` ; il n'existe pas (encore) de table de regroupement par lot.

---

## Description des relations (4)

### 1. users
```
(id, email, username, role)
```
**Clé primaire :** `id` (INTEGER, auto-incrémenté)

**Contraintes :**
- `email` UNIQUE NOT NULL
- `username` UNIQUE NOT NULL
- `role` ∈ {`USER`, `ADMIN`, `SUPERADMIN`} (SQLEnum `UserRole`)

> *Note* : la table `users` réelle contient d'autres colonnes (`hashed_password`, `is_active`, `is_banned`, `email_verified`, `two_factor_enabled`, `profile_picture`, etc.) mais elles relèvent d'autres sprints (auth, 2FA, administration) et ne sont pas représentées ici, conformément au périmètre du sprint 3.

---

### 2. email_providers
```
(id, provider_name, oauth_authorize_url, oauth_token_url,
 api_base_url, scopes, is_active, created_at)
```
**Clé primaire :** `id` (INTEGER, auto-incrémenté)

**Contraintes :**
- `provider_name` UNIQUE NOT NULL ∈ {`gmail`, `outlook`}
- `oauth_authorize_url` NOT NULL
- `oauth_token_url` NOT NULL
- `api_base_url` NOT NULL
- `scopes` NOT NULL (chaîne de scopes séparés par espace)
- `is_active` BOOLEAN — défaut `true`
- `created_at` TIMESTAMP — défaut `NOW()`

---

### 3. user_email_credentials
```
(id, user_id, provider,
 access_token, refresh_token, token_expiry,
 email_address, created_at, updated_at)
```
**Clé primaire :** `id` (INTEGER, auto-incrémenté)

**Relations :**
- `user_id` → Référence vers `users.id` (ON DELETE CASCADE)

**Contraintes :**
- `UNIQUE(user_id, provider)` — un utilisateur ne peut connecter qu'**un seul** compte par fournisseur
- `provider` VARCHAR(20) NOT NULL ∈ {`gmail`, `outlook`}
- `access_token` TEXT NOT NULL — chiffré au niveau applicatif (Fernet/AES-GCM)
- `refresh_token` TEXT NULLABLE — chiffré au niveau applicatif
- `token_expiry` TIMESTAMP NULLABLE
- `email_address` VARCHAR(255) NULLABLE — adresse du compte connecté
- `created_at`, `updated_at` TIMESTAMP

> *Note de conception* : `provider` est stocké comme une chaîne (`'gmail'`/`'outlook'`) plutôt qu'une FK vers `email_providers.provider_name`. Ce choix simplifie les requêtes mais nécessite une cohérence applicative.

---

### 4. analysis_history
```
(id, user_id,
 analysis_type, content_preview,
 threat_level, confidence,
 features, recommendations,
 created_at)
```
**Clé primaire :** `id` (INTEGER, auto-incrémenté)

**Relations :**
- `user_id` → Référence vers `users.id` (ON DELETE CASCADE, NULLABLE — analyses anonymes possibles)

**Contraintes :**
- `analysis_type` VARCHAR(10) NOT NULL ∈ {`email`, `url`}
- `content_preview` TEXT NOT NULL
- `threat_level` VARCHAR(20) NOT NULL ∈ {`safe`, `suspicious`, `dangerous`}
- `confidence` FLOAT NOT NULL ∈ [0, 1]
- `features` JSON NULLABLE — caractéristiques détectées par le modèle ML
- `recommendations` JSON NULLABLE — recommandations générées
- `created_at` TIMESTAMP — défaut `NOW()`

> *Note* : le sprint 3 réutilise cette table existante. Une analyse en masse génère **plusieurs lignes** dans `analysis_history` (une par email analysé), sans regroupement physique.

---

## Schéma textuel récapitulatif

```
users                    (#id, email, username, role)
email_providers          (#id, provider_name, oauth_authorize_url, oauth_token_url,
                          api_base_url, scopes, is_active, created_at)
user_email_credentials   (#id,
                          #user_id → users.id  (ON DELETE CASCADE),
                          provider, access_token, refresh_token, token_expiry,
                          email_address, created_at, updated_at,
                          UNIQUE(user_id, provider))
analysis_history         (#id,
                          #user_id → users.id  (ON DELETE CASCADE, NULL OK),
                          analysis_type, content_preview, threat_level, confidence,
                          features, recommendations, created_at)
```

---

## Traçabilité MCD → MLD (Supabase)

| MCD (entité ou association) | MLD réel (table ou colonne) |
|---|---|
| Entité `Utilisateur` | Table `users` (colonnes sprint 3 : id, email, username, role) |
| Entité `FournisseurEmail` | Table `email_providers` |
| Classe-association `IdentifiantEmail` | Table `user_email_credentials` + UNIQUE(user_id, provider) |
| Entité `EmailImporté` | ❌ **Non persistée** — récupération à la volée via Gmail/Microsoft Graph |
| Entité `LotAnalyse` | ❌ **Non persistée** — éclatée en N lignes dans `analysis_history` |
| Entité `Analyse` | Table `analysis_history` |
| Association `se_connecte` | FK `user_email_credentials.user_id` |
| Association `lance` / `effectue` | FK `analysis_history.user_id` |
| Association `concerne` (Analyse → EmailImporté) | ❌ Pas de FK vers les emails (non persistés) |

---

## Snippet LaTeX prêt à coller

```latex
\subsection*{Modèle logique de données (MLD)}

À partir du MCD précédent, nous avons procédé au passage au modèle logique
relationnel selon les règles classiques de Merise. Ce MLD est aligné sur le
schéma réel de la base PostgreSQL (Supabase) actuellement en production.

\begin{figure}[H]
    \centering
    \includegraphics[width=\textwidth]{figures/MLD_sprint3.pdf}
    \caption{Modèle Logique de Données du sprint 3 — aligné Supabase}
    \label{fig:mld_sprint3}
\end{figure}

\paragraph{Description des relations.}

\begin{enumerate}
    \item \textbf{users}\\
    \texttt{(id, email, username, role)}\\
    Clé primaire : \texttt{id} (INTEGER)\\
    Contraintes :
    \begin{itemize}
        \item \texttt{email} UNIQUE NOT NULL
        \item \texttt{username} UNIQUE NOT NULL
        \item \texttt{role} $\in$ \{\texttt{USER}, \texttt{ADMIN}, \texttt{SUPERADMIN}\}
    \end{itemize}

    \item \textbf{email\_providers}\\
    \texttt{(id, provider\_name, oauth\_authorize\_url, oauth\_token\_url, api\_base\_url, scopes, is\_active, created\_at)}\\
    Clé primaire : \texttt{id} (INTEGER)\\
    Contraintes :
    \begin{itemize}
        \item \texttt{provider\_name} UNIQUE NOT NULL
        \item \texttt{provider\_name} $\in$ \{\texttt{gmail}, \texttt{outlook}\}
    \end{itemize}

    \item \textbf{user\_email\_credentials}\\
    \texttt{(id, user\_id, provider, access\_token, refresh\_token, token\_expiry, email\_address, created\_at, updated\_at)}\\
    Clé primaire : \texttt{id} (INTEGER)\\
    Relations :
    \begin{itemize}
        \item \texttt{user\_id} $\rightarrow$ Référence vers \textbf{users} (ON DELETE CASCADE)
    \end{itemize}
    Contraintes :
    \begin{itemize}
        \item \texttt{UNIQUE(user\_id, provider)}
        \item \texttt{access\_token}, \texttt{refresh\_token} chiffrés au niveau applicatif
    \end{itemize}

    \item \textbf{analysis\_history}\\
    \texttt{(id, user\_id, analysis\_type, content\_preview, threat\_level, confidence, features, recommendations, created\_at)}\\
    Clé primaire : \texttt{id} (INTEGER)\\
    Relations :
    \begin{itemize}
        \item \texttt{user\_id} $\rightarrow$ Référence vers \textbf{users} (ON DELETE CASCADE, NULLABLE)
    \end{itemize}
    Contraintes :
    \begin{itemize}
        \item \texttt{analysis\_type} $\in$ \{\texttt{email}, \texttt{url}\}
        \item \texttt{threat\_level} $\in$ \{\texttt{safe}, \texttt{suspicious}, \texttt{dangerous}\}
        \item \texttt{confidence} $\in [0, 1]$
    \end{itemize}
\end{enumerate}

\paragraph{Justification des absences.} Les emails consultés depuis Gmail ou
Outlook ne sont pas persistés en base : ils sont récupérés à la volée via les
API des fournisseurs (Gmail API, Microsoft Graph) et seul un cache léger est
maintenu en mémoire le temps de l'analyse. De même, une analyse en masse
génère $N$ lignes dans \texttt{analysis\_history} sans regroupement physique
par lot : le rapport agrégé (compteurs Safe/Suspicious/Dangerous) est calculé
côté applicatif au moment du retour de la requête.
```

---

## Étapes suivantes

- **MPD / Script SQL** : `CREATE TABLE` PostgreSQL avec types précis (SERIAL, VARCHAR, TIMESTAMP WITH TIME ZONE, JSON), index sur les FK, contraintes `NOT NULL` / `UNIQUE` / `CHECK`. Dis-moi si tu veux que j'enchaîne.
