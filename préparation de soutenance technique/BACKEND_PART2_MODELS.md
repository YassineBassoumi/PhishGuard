# Documentation Backend - Partie 2: Modèles

## 📊 Modèles de Données (app/models/)

### **user_models.py**
**Rôle:** Modèle utilisateur principal.

**Table:** `users`

**Champs:**
```python
- id: UUID (clé primaire)
- username: String (unique)
- email: String (unique, indexé)
- hashed_password: String
- is_active: Boolean (compte actif)
- is_email_verified: Boolean
- is_first_login: Boolean
- role: Enum (user/admin/superadmin)
- is_banned: Boolean
- ban_reason: String (nullable)
- profile_picture: String (nom fichier)
- created_at: DateTime
- updated_at: DateTime
- last_login: DateTime
```

**Relations:**
- `analysis_history` - Historique d'analyses
- `statistics` - Statistiques utilisateur
- `email_credentials` - Credentials email providers
- `sessions` - Sessions actives
- `audit_logs` - Logs d'audit

**Méthodes:**
- `verify_password(password)` - Vérifie le mot de passe
- `get_password_hash(password)` - Hash le mot de passe

---

### **database_models.py**
**Rôle:** Modèles pour l'historique et statistiques.

**Tables:**

1. **`analysis_history`**
```python
- id: Integer (auto-increment)
- user_id: UUID (FK → users)
- content_type: Enum (url/email/text)
- content: Text
- threat_level: String (safe/suspicious/dangerous)
- confidence: Float (0-1)
- features: JSON (indicateurs détectés)
- recommendations: JSON
- analyzed_at: DateTime
```

2. **`statistics`**
```python
- id: Integer
- user_id: UUID (FK → users, unique)
- total_analyses: Integer
- threats_detected: Integer
- safe_count: Integer
- suspicious_count: Integer
- dangerous_count: Integer
- last_analysis: DateTime
```

**Utilisation:**
- Stocke chaque analyse effectuée
- Calcule les statistiques globales
- Affiche dans le dashboard

---

### **email_provider_models.py**
**Rôle:** Gestion des connexions email providers.

**Tables:**

1. **`email_providers`**
```python
- id: Integer
- name: String (gmail/outlook)
- is_active: Boolean
- created_at: DateTime
```

2. **`user_email_credentials`**
```python
- id: Integer
- user_id: UUID (FK → users)
- provider_id: Integer (FK → email_providers)
- access_token: Text (chiffré)
- refresh_token: Text (chiffré)
- token_expiry: DateTime
- email_address: String
- is_active: Boolean
- created_at: DateTime
- updated_at: DateTime
```

**Sécurité:**
- Tokens OAuth2 stockés chiffrés
- Refresh automatique des tokens expirés
- Révocation possible

---

### **session_models.py**
**Rôle:** Gestion des sessions utilisateur.

**Table:** `user_sessions`

**Champs:**
```python
- id: Integer
- user_id: UUID (FK → users)
- jti: String (JWT ID, unique, indexé)
- device_info: String
- ip_address: String
- location: String (ville, pays)
- user_agent: String
- is_active: Boolean
- created_at: DateTime
- expires_at: DateTime
- last_activity: DateTime
```

**Fonctionnalités:**
- Tracking des sessions actives
- Géolocalisation par IP
- Détection d'appareils
- Révocation de sessions
- Détection de connexions suspectes

---

### **notification_models.py**
**Rôle:** Système de notifications.

**Table:** `notifications`

**Champs:**
```python
- id: Integer
- user_id: UUID (FK → users)
- type: Enum (security_alert/threat_detected/system_update)
- title: String
- message: Text
- severity: Enum (info/warning/critical)
- is_read: Boolean
- created_at: DateTime
- read_at: DateTime (nullable)
- metadata: JSON (données additionnelles)
```

**Types de Notifications:**
- `security_alert` - Nouvelle connexion, changement mot de passe
- `threat_detected` - Menace détectée dans analyse
- `system_update` - Mises à jour système
- `brute_force_alert` - Tentatives de connexion multiples

---

### **audit_models.py**
**Rôle:** Logs d'audit pour la sécurité.

**Table:** `audit_logs`

**Champs:**
```python
- id: Integer
- user_id: UUID (FK → users, nullable)
- action: String (login/logout/analysis/etc.)
- resource: String (ressource affectée)
- details: JSON
- ip_address: String
- user_agent: String
- status: Enum (success/failure)
- created_at: DateTime
```

**Actions Trackées:**
- Authentification (login/logout)
- Analyses effectuées
- Modifications de profil
- Actions administratives
- Tentatives échouées

---

### **password_reset_models.py**
**Rôle:** Tokens de réinitialisation mot de passe.

**Table:** `password_reset_tokens`

**Champs:**
```python
- id: Integer
- user_id: UUID (FK → users)
- token: String (unique, indexé)
- expires_at: DateTime
- is_used: Boolean
- created_at: DateTime
- used_at: DateTime (nullable)
```

**Workflow:**
1. Utilisateur demande reset
2. Token généré (valide 1h)
3. Email envoyé avec lien
4. Token vérifié et marqué utilisé
5. Mot de passe mis à jour

---

### **email_verification_models.py**
**Rôle:** Vérification des emails utilisateurs.

**Table:** `email_verification_tokens`

**Champs:**
```python
- id: Integer
- user_id: UUID (FK → users)
- token: String (unique, indexé)
- expires_at: DateTime
- is_used: Boolean
- created_at: DateTime
- verified_at: DateTime (nullable)
```

**Workflow:**
1. Inscription utilisateur
2. Token généré (valide 24h)
3. Email de vérification envoyé
4. Utilisateur clique sur lien
5. Email marqué vérifié

---

## 📝 Schémas Pydantic (Validation)

### **auth_schemas.py**
**Schémas d'authentification:**

```python
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str (min 8 caractères)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    role: str
    is_email_verified: bool
    profile_picture: Optional[str]
```

---

### **schemas.py**
**Schémas d'analyse:**

```python
class AnalysisRequest(BaseModel):
    content: str
    content_type: Literal["url", "email", "text"]

class AnalysisResponse(BaseModel):
    threat_level: str
    confidence: float
    features: List[str]
    recommendations: List[str]
    analyzed_at: datetime

class BulkAnalysisRequest(BaseModel):
    items: List[str]
    content_type: str

class BulkAnalysisResult(BaseModel):
    results: List[AnalysisResponse]
    summary: Dict[str, int]
```

---

### **notification_schemas.py**
**Schémas de notifications:**

```python
class NotificationCreate(BaseModel):
    type: str
    title: str
    message: str
    severity: str

class NotificationResponse(BaseModel):
    id: int
    type: str
    title: str
    message: str
    severity: str
    is_read: bool
    created_at: datetime
```

---

## 🔗 Relations entre Modèles

```
User (1) ──────── (N) AnalysisHistory
  │
  ├─────────────── (1) Statistics
  │
  ├─────────────── (N) UserEmailCredentials
  │
  ├─────────────── (N) UserSessions
  │
  ├─────────────── (N) Notifications
  │
  ├─────────────── (N) AuditLogs
  │
  ├─────────────── (N) PasswordResetTokens
  │
  └─────────────── (N) EmailVerificationTokens

EmailProvider (1) ─ (N) UserEmailCredentials
```

---

## 💾 Migrations de Base de Données

### **Création Automatique**
Les tables sont créées automatiquement au démarrage via:
```python
await init_db()  # Dans main.py lifespan
```

### **Scripts de Migration**
Situés dans `backend/scripts/`:

1. **init_db.py**
   - Crée toutes les tables
   - Initialise les données de base

2. **promote_to_superadmin.py**
   - Promouvoir un utilisateur en superadmin
   - Usage: `python scripts/promote_to_superadmin.py username`

3. **verify_user.py**
   - Vérifier manuellement un email
   - Usage: `python scripts/verify_user.py username`

---

Cette partie couvre tous les modèles de données du backend PhishGuard.
