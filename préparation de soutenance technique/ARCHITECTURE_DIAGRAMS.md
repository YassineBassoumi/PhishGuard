# 🏗️ Diagrammes d'Architecture — PhishGuard

> Tous les diagrammes sont en **Mermaid**. Ils s'affichent automatiquement sur GitHub et dans tous les éditeurs Markdown modernes (VS Code, Obsidian, Notion…).
> En cas de besoin pour les slides : copier le code, le coller sur https://mermaid.live et exporter en PNG/SVG.

---

## 1. Architecture globale (haut niveau)

```mermaid
flowchart LR
    User([👤 Utilisateur]) -->|HTTPS| Frontend
    Frontend["🖥️ Frontend<br/>React 19 + Vite<br/>(localhost:5173)"]
    Frontend -->|REST API<br/>JWT Bearer| Backend
    Backend["⚙️ Backend FastAPI<br/>Python 3.11<br/>(localhost:8000)"]
    Backend --> DB[(🗄️ PostgreSQL<br/>Supabase)]
    Backend --> ML["🤖 Modèles ML<br/>LinearSVC + RandomForest"]
    Backend -->|OAuth 2.0| Gmail[📧 Gmail API]
    Backend -->|OAuth 2.0| Outlook[📧 Outlook API<br/>Microsoft Graph]
    Backend -->|SMTP| Mailer[✉️ Service email<br/>notifications]
    Backend -->|HTTPS| GeoIP[🌍 ipapi.co<br/>géolocalisation]
```

---

## 2. Architecture en couches (backend)

```mermaid
flowchart TB
    subgraph Routes ["🛣️ Routes FastAPI (app/routes/)"]
        R1[auth.py]
        R2[analysis.py]
        R3[gmail.py / outlook.py]
        R4[admin.py]
        R5[two_factor.py]
        R6[sessions.py]
        R7[notifications.py]
        R8[...]
    end

    subgraph Middleware ["🛡️ Middlewares"]
        M1[rate_limiter.py<br/>100 req/min/IP]
        M2[database_monitor.py]
        M3[CORS]
    end

    subgraph Services ["🔧 Services (logique métier)"]
        S1[auth_service.py]
        S2[detector.py<br/>+ detection/]
        S3[gmail_service.py]
        S4[outlook_service.py]
        S5[email_service.py]
        S6[notification_service.py]
        S7[session_service.py]
        S8[two_factor_service.py]
        S9[stats_service.py]
        S10[audit_service.py]
    end

    subgraph Models ["📊 Modèles SQLAlchemy"]
        DM1[user_models.py]
        DM2[database_models.py<br/>analysis_history, statistics]
        DM3[email_provider_models.py]
        DM4[session_models.py]
        DM5[notification_models.py]
        DM6[audit_models.py]
        DM7[password_reset_models.py]
        DM8[email_verification_models.py]
    end

    DB[(🗄️ PostgreSQL)]

    Routes --> Middleware
    Routes --> Services
    Services --> Models
    Models --> DB
```

---

## 3. Modèle de données (ER simplifié)

```mermaid
erDiagram
    USERS ||--o{ ANALYSIS_HISTORY : "effectue"
    USERS ||--o| STATISTICS : "a"
    USERS ||--o{ USER_EMAIL_CREDENTIALS : "connecte"
    USERS ||--o{ USER_SESSIONS : "ouvre"
    USERS ||--o{ NOTIFICATIONS : "reçoit"
    USERS ||--o{ AUDIT_LOGS : "génère"
    USERS ||--o{ PASSWORD_RESET_TOKENS : "demande"
    USERS ||--o{ EMAIL_VERIFICATION_TOKENS : "vérifie"
    EMAIL_PROVIDERS ||--o{ USER_EMAIL_CREDENTIALS : "supporte"

    USERS {
        int id PK
        string email UK
        string username UK
        string hashed_password
        enum role "USER, ADMIN, SUPERADMIN"
        bool is_active
        bool is_banned
        bool email_verified
        bool two_factor_enabled
        string two_factor_secret
        string profile_picture
        datetime created_at
        datetime last_login
    }

    ANALYSIS_HISTORY {
        int id PK
        int user_id FK
        string analysis_type "email|url"
        text content_preview
        string threat_level "safe|suspicious|dangerous"
        float confidence
        json features
        json recommendations
        datetime created_at
    }

    STATISTICS {
        int id PK
        int user_id FK "NULL = global"
        int total_analyses
        int threats_detected
        int emails_analyzed
        int urls_analyzed
        datetime last_updated
    }

    USER_EMAIL_CREDENTIALS {
        int id PK
        int user_id FK
        int provider_id FK
        text access_token
        text refresh_token
        datetime token_expiry
        string email_address
        bool is_active
    }

    USER_SESSIONS {
        int id PK
        int user_id FK
        string jti UK "JWT ID"
        string device_info
        string ip_address
        string location
        bool is_active
        datetime expires_at
        datetime last_activity
    }

    NOTIFICATIONS {
        int id PK
        int user_id FK
        string type
        string title
        text message
        string severity
        bool is_read
        datetime created_at
    }

    AUDIT_LOGS {
        int id PK
        int user_id FK
        string action
        string resource
        json details
        string ip_address
        string status
        datetime created_at
    }
```

---

## 4. Séquence — Inscription + connexion + 2FA

```mermaid
sequenceDiagram
    actor U as 👤 Utilisateur
    participant F as 🖥️ Frontend React
    participant B as ⚙️ Backend FastAPI
    participant DB as 🗄️ PostgreSQL
    participant Mail as ✉️ SMTP

    Note over U,Mail: 1. Inscription
    U->>F: Saisit email + password
    F->>B: POST /api/auth/register
    B->>B: Hash bcrypt du password
    B->>DB: INSERT user
    B->>DB: INSERT email_verification_token
    B->>Mail: Envoi email de vérification
    B-->>F: 201 Created + JWT
    F-->>U: Redirige vers dashboard

    Note over U,Mail: 2. Vérification email
    U->>F: Clique lien dans email
    F->>B: POST /api/email-verification/verify {token}
    B->>DB: UPDATE user.email_verified = true
    B-->>F: 200 OK

    Note over U,Mail: 3. Activation 2FA
    U->>F: Clique "Activer 2FA"
    F->>B: POST /api/2fa/setup
    B->>B: Génère secret TOTP + QR
    B-->>F: {secret, qr_code_base64}
    U->>U: Scanne QR avec Authy/Google Auth
    U->>F: Saisit code 6 chiffres
    F->>B: POST /api/2fa/enable {code}
    B->>B: Vérifie TOTP
    B->>DB: UPDATE two_factor_enabled = true
    B-->>F: 200 OK + backup_codes
```

---

## 5. Séquence — Analyse d'un email avec approche hybride

```mermaid
sequenceDiagram
    actor U as 👤 Utilisateur
    participant F as 🖥️ Frontend
    participant B as ⚙️ Backend
    participant H as 🤖 HybridDetector
    participant E as 📧 EmailDetector<br/>(LinearSVC)
    participant URL as 🔗 URLDetector<br/>(RandomForest)
    participant DB as 🗄️ PostgreSQL

    U->>F: Colle un email suspect
    F->>B: POST /api/analyze-email<br/>{content}
    B->>B: Vérifie JWT + rate limit

    B->>H: analyze_email_hybrid(content)
    H->>H: preprocess_raw_email()<br/>(strip headers / HTML)
    H->>E: analyze(text)
    E->>E: TF-IDF vectorize
    E->>E: model.decision_function()
    E->>E: sigmoid → confidence
    E-->>H: (threat, conf, features, recs)

    H->>H: Extract URLs from content

    loop Pour chaque URL
        H->>URL: analyze(url)
        URL->>URL: Check whitelist + IP privée
        URL->>URL: Extract 23 features
        URL->>URL: RandomForest predict
        URL-->>H: (threat, conf, features, recs)
    end

    H->>H: Combine résultats<br/>+ build decision_trace
    H-->>B: Final result + trace

    B->>DB: INSERT analysis_history
    B->>DB: UPDATE statistics
    B-->>F: 200 OK<br/>{threat_level, confidence, features,<br/>recommendations, url_results, trace}
    F-->>U: Affiche résultat coloré + indicateurs
```

---

## 6. Séquence — Connexion à Gmail via OAuth 2.0

```mermaid
sequenceDiagram
    actor U as 👤 Utilisateur
    participant F as 🖥️ Frontend
    participant B as ⚙️ Backend
    participant G as 🟦 Google OAuth
    participant Gmail as 📧 Gmail API
    participant DB as 🗄️ PostgreSQL

    U->>F: Clique "Connecter Gmail"
    F->>B: GET /api/email/gmail/auth
    B->>B: Génère auth_url + state
    B-->>F: {auth_url}
    F->>G: Redirect vers auth_url<br/>(scopes: gmail.readonly)
    U->>G: Autorise l'application
    G->>F: Redirect /api/gmail/callback?code=...
    F->>B: GET /api/gmail/callback?code=...
    B->>G: Échange code → tokens
    G-->>B: {access_token, refresh_token}
    B->>DB: INSERT user_email_credentials<br/>(tokens chiffrés)
    B-->>F: Redirect /dashboard?auth=success

    Note over U,DB: Plus tard — récupération des emails

    U->>F: Ouvre la liste Gmail
    F->>B: POST /api/email/emails {provider:"gmail"}
    B->>DB: Charge credentials
    alt Token expiré
        B->>G: Refresh token
        G-->>B: Nouveau access_token
        B->>DB: UPDATE access_token
    end
    B->>Gmail: GET /messages
    Gmail-->>B: Liste emails
    B-->>F: Emails formatés
    F-->>U: Affiche la boîte
```

---

## 7. Diagramme de cas d'utilisation (use cases)

```mermaid
flowchart TB
    User([👤 Utilisateur])
    Admin([👑 Admin])

    subgraph Public ["Cas d'usage publics"]
        UC1[S'inscrire]
        UC2[Se connecter]
        UC3[Demander reset password]
        UC4[Vérifier email]
    end

    subgraph Auth ["Cas d'usage authentifiés"]
        UC5[Analyser un email]
        UC6[Analyser une URL]
        UC7[Analyse en masse]
        UC8[Connecter Gmail/Outlook]
        UC9[Voir l'historique]
        UC10[Voir le dashboard]
        UC11[Activer 2FA]
        UC12[Gérer ses sessions]
        UC13[Modifier son profil]
        UC14[Supprimer son compte]
    end

    subgraph Adm ["Cas d'usage admin"]
        UC15[Lister les utilisateurs]
        UC16[Bannir / débannir]
        UC17[Voir audit logs]
        UC18[Stats globales]
        UC19[Gérer rate limits]
        UC20[Voir tentatives brute force]
    end

    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5
    User --> UC6
    User --> UC7
    User --> UC8
    User --> UC9
    User --> UC10
    User --> UC11
    User --> UC12
    User --> UC13
    User --> UC14

    Admin --> UC15
    Admin --> UC16
    Admin --> UC17
    Admin --> UC18
    Admin --> UC19
    Admin --> UC20
```

---

## 8. Pipeline de détection ML (vue détaillée)

```mermaid
flowchart TB
    Input["📨 Input utilisateur<br/>(email texte ou URL)"]

    Input --> Type{Type ?}
    Type -->|email/texte| EmailFlow
    Type -->|url| URLFlow

    subgraph EmailFlow ["Pipeline EMAIL — analyse hybride"]
        E1[preprocess_raw_email<br/>strip RFC822 headers, HTML]
        E2[Extraire les URLs du texte]
        E3[Texte nettoyé → TF-IDF → LinearSVC]
        E4[Pour chaque URL → URLDetector]
        E5[Combiner résultats]
        E6[Ajouter règles<br/>urgence, credentials, typo]
        E1 --> E2 --> E3 --> E5
        E2 --> E4 --> E5
        E5 --> E6
    end

    subgraph URLFlow ["Pipeline URL"]
        U1{IP privée ?}
        U2[→ safe 95%]
        U3{Domaine en whitelist ?}
        U4[→ safe 98%]
        U5[Extraire 23 features]
        U6[RandomForest predict]
        U7[Règles complémentaires<br/>shorteners, typos, TLDs risqués]
        U1 -->|oui| U2
        U1 -->|non| U3
        U3 -->|oui| U4
        U3 -->|non| U5 --> U6 --> U7
    end

    EmailFlow --> Out[Threat: safe / suspicious / dangerous<br/>Confidence: 0-100%<br/>Features: liste<br/>Recommendations: liste]
    URLFlow --> Out
```

---

## 9. Flux d'authentification JWT + 2FA

```mermaid
flowchart LR
    Login[Login form<br/>email + password]
    Login -->|POST /api/auth/login| Verify
    Verify{Password<br/>valide ?}
    Verify -->|non| Fail[401 + log audit]
    Verify -->|oui| Has2FA{2FA<br/>activée ?}
    Has2FA -->|non| Issue[Issue JWT + session]
    Has2FA -->|oui| Ask2FA[Demande code 6 chiffres]
    Ask2FA -->|POST /api/2fa/verify| Check2FA{Code<br/>valide ?}
    Check2FA -->|non| Fail
    Check2FA -->|oui| Issue
    Issue --> Done[200 OK<br/>+ token + user data]
```

---

## 10. Architecture de déploiement (cible production)

```mermaid
flowchart TB
    Internet([🌍 Internet])
    Internet -->|HTTPS| LB[🔀 Reverse Proxy<br/>Nginx + SSL Let's Encrypt]
    LB --> FE[📦 Frontend<br/>build statique<br/>servi par Nginx]
    LB --> API[⚙️ Backend FastAPI<br/>gunicorn + uvicorn workers]
    API --> DB[(🗄️ PostgreSQL<br/>Supabase managed)]
    API --> Cache[(⚡ Redis<br/>rate limiting + cache)]
    API --> Storage[💾 Object Storage<br/>profile pictures]
    API --> Sentry[📊 Sentry<br/>error tracking]
    API --> Promet[📈 Prometheus + Grafana<br/>metrics]
```
