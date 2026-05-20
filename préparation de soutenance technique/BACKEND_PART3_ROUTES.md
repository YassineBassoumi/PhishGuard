# Documentation Backend - Partie 3: Routes API

## 🛣️ Routes API (app/routes/)

### **auth.py**
**Rôle:** Authentification et gestion des comptes.

**Endpoints:**

1. **POST `/api/auth/register`**
   - Inscription nouvel utilisateur
   - Body: `{username, email, password}`
   - Validation: email unique, mot de passe fort
   - Envoie email de vérification
   - Retourne: token JWT + user data

2. **POST `/api/auth/login`**
   - Connexion utilisateur
   - Body (form-data): `{username, password, scope?}`
   - Vérifie: email vérifié, compte non banni, compte actif
   - Si compte désactivé (`is_active=False`) → **403** avec `detail: "ACCOUNT_DEACTIVATED"`
   - Si 2FA activé → exige code TOTP ou backup code dans le champ `scope`
   - Crée session avec géolocalisation
   - Détecte première connexion
   - Retourne: token JWT + user data

3. **POST `/api/auth/logout`**
   - Déconnexion utilisateur
   - Révoque la session active
   - Nécessite: token JWT

4. **GET `/api/auth/me`**
   - Récupère infos utilisateur connecté
   - Nécessite: token JWT
   - Retourne: user data complet

5. **PUT `/api/auth/change-password`**
   - Changement de mot de passe
   - Body: `{old_password, new_password}`
   - Vérifie ancien mot de passe
   - Envoie notification email

6. **PUT `/api/auth/me/deactivate`**
   - Désactivation réversible du compte
   - Body: `{password, reason?}` (raison optionnelle, max 500 chars)
   - Vérifie le mot de passe
   - Met `is_active = False`
   - Révoque toutes les sessions actives
   - Retourne: confirmation de désactivation
   - **Réversible** : le compte n'est pas supprimé, il peut être réactivé

7. **POST `/api/auth/reactivate`**
   - Réactivation d'un compte désactivé
   - Body (form-data): `{username, password, scope?}`
   - Vérifie les credentials (password + 2FA si activé)
   - Remet `is_active = True`
   - Crée une nouvelle session
   - Retourne: token JWT + user data (comme un login normal)
   - **Note** : accessible uniquement si le compte est désactivé

**Sécurité:**
- Rate limiting: 5 tentatives/minute
- Hachage bcrypt des mots de passe
- JWT avec expiration (30 min)
- Détection brute force
- Désactivation réversible (pas de perte de données)

---

### **analysis.py**
**Rôle:** Analyse de phishing (URLs, emails, texte).

**Endpoints (préfixe `/api`):**

1. **POST `/api/analyze-email`**
   - Analyse texte/email avec approche **hybride** par défaut (texte + URLs séparément)
   - Body: `{content: str}`
   - Auth requise
   - Retourne: `threat_level`, `confidence`, `features`, `recommendations`, `decision_trace`, `url_results`

2. **POST `/api/analyze-url`**
   - Analyse une URL
   - Body: `{url: str}`
   - Auth requise

3. **POST `/api/analyze-email-hybrid`**
   - Même chose que `/analyze-email` mais explicite l'usage hybride

4. **POST `/api/analyze-bulk`**
   - Analyse en masse (jusqu'à 100 items)
   - Body: `{items: ["email1…", …], content_type: "email"|"url"}`
   - Traitement parallélisé via `asyncio`

5. **POST `/api/analyze-progressive`** / **POST `/api/analyze-email-progressive`**
   - Variantes pour analyse étape par étape (UI temps réel)

6. **GET `/api/stats`**
   - Statistiques utilisateur (cumulées)

7. **GET `/api/history`**
   - Historique des analyses (pagination)

8. **GET `/api/threat-distribution`**
   - Distribution `safe / suspicious / dangerous` pour graphiques dashboard

9. **GET `/api/health`**
   - Health check (statut service + chargement modèles)

**Modèles ML Utilisés:**
- `phishing_model.pkl` (LinearSVC, 97,5%) + `vectorizer.pkl` — Détection emails/texte
- `url_classifier.pkl` (Random Forest, 94,6%) — Détection URLs

---

### **gmail.py**
**Rôle:** Intégration Gmail via OAuth2.

**Endpoints:**

1. **GET `/api/gmail/auth`**
   - Initie OAuth2 flow
   - Génère URL d'autorisation Google
   - Scopes: gmail.readonly
   - Retourne: `{auth_url}`

2. **GET `/api/gmail/callback`**
   - Callback OAuth2
   - Reçoit code d'autorisation
   - Échange contre access/refresh tokens
   - Stocke tokens chiffrés en DB
   - Redirige vers frontend

3. **GET `/api/gmail/emails`**
   - Récupère emails Gmail
   - Query: `?max_results=50&query=...`
   - Utilise Gmail API
   - Retourne: liste d'emails formatés

4. **POST `/api/gmail/disconnect`**
   - Déconnecte Gmail
   - Révoque tokens
   - Supprime credentials DB

**Sécurité:**
- Tokens OAuth2 chiffrés
- Refresh automatique
- Scopes minimaux (readonly)

---

### **outlook.py**
**Rôle:** Intégration Outlook/Hotmail via OAuth2.

**Endpoints:**

1. **GET `/api/outlook/auth`**
   - Initie OAuth2 flow Microsoft
   - Génère URL d'autorisation
   - Scopes: Mail.Read
   - Retourne: `{auth_url}`

2. **GET `/api/outlook/callback`**
   - Callback OAuth2
   - Échange code contre tokens
   - Stocke credentials
   - Redirige vers frontend

3. **GET `/api/outlook/emails`**
   - Récupère emails Outlook
   - Query: `?max_results=50`
   - Utilise Microsoft Graph API
   - Retourne: liste d'emails

4. **POST `/api/outlook/disconnect`**
   - Déconnecte Outlook
   - Révoque tokens

---

### **email_providers.py**
**Rôle:** Gestion unifiée des providers.

**Endpoints:**

1. **GET `/api/email/providers`**
   - Liste providers disponibles
   - Retourne: `[{id, name, icon, available}]`
   - Gmail et Outlook

2. **GET `/api/email/providers/connected`**
   - Providers connectés par l'utilisateur
   - Retourne: `{connected_providers: [...]}`

3. **GET `/api/email/{provider}/auth`**
   - Route unifiée pour auth
   - Provider: gmail/outlook
   - Redirige vers provider spécifique

---

### **admin.py**
**Rôle:** Panel d'administration (superadmin uniquement).

**Endpoints:**

1. **GET `/api/admin/users`**
   - Liste tous les utilisateurs
   - Query: `?search=...&role=...&status=...`
   - Pagination
   - Filtres multiples
   - Nécessite: role superadmin

2. **POST `/api/admin/users/{user_id}/ban`**
   - Bannir un utilisateur
   - Body: `{reason}`
   - Révoque toutes les sessions
   - Envoie notification

3. **POST `/api/admin/users/{user_id}/unban`**
   - Débannir un utilisateur
   - Restaure l'accès

4. **PUT `/api/admin/users/{user_id}/role`**
   - Changer le rôle
   - Body: `{role: "admin"/"user"}`
   - Audit log créé

5. **DELETE `/api/admin/users/{user_id}`**
   - Supprimer un compte
   - Supprime toutes les données associées
   - Irréversible

6. **GET `/api/admin/statistics`**
   - Statistiques globales
   - Total utilisateurs
   - Analyses par jour
   - Menaces détectées
   - Graphiques admin

7. **GET `/api/admin/audit-logs`**
   - Logs d'audit système
   - Filtres par action, user, date
   - Pagination

**Sécurité:**
- Vérification role superadmin
- Audit de toutes les actions
- Rate limiting strict

---

### **two_factor.py**
**Rôle:** Authentification à deux facteurs (2FA).

**Endpoints (préfixe `/api/2fa`):**

1. **GET `/api/2fa/status`**
   - Récupère le statut 2FA de l'utilisateur
   - Retourne: `{enabled: bool, backup_codes_remaining: int}`

2. **POST `/api/2fa/setup`**
   - Initie la configuration 2FA
   - Génère secret TOTP + QR code + 8 codes de secours
   - Stocke le secret et les codes en base (2FA pas encore activé)
   - Retourne: `{secret, qr_code, backup_codes}`
   - ⚠️ Ne pas appeler si 2FA déjà activé

3. **POST `/api/2fa/enable`**
   - Active définitivement 2FA après vérification
   - Body: `{token}` (code 6 chiffres depuis l'app authenticator)
   - Vérifie le token TOTP contre le secret stocké
   - Si valide → `two_factor_enabled = True`
   - Envoie notification email "2FA Enabled"

4. **POST `/api/2fa/disable`**
   - Désactive 2FA
   - Body: `{password}`
   - Vérifie le mot de passe uniquement
   - Efface secret et codes de secours
   - Envoie notification email "2FA Disabled"

5. **POST `/api/2fa/verify`**
   - Vérifie un token TOTP (pour test)
   - Body: `{token}` (6 chiffres)
   - Nécessite: 2FA activé
   - Retourne: `{valid: bool, message}`

6. **POST `/api/2fa/regenerate-backup-codes`**
   - Régénère 8 nouveaux codes de secours
   - Invalide tous les anciens codes
   - Nécessite: 2FA activé
   - Retourne: `{backup_codes: [...]}`

**Technologie:**
- TOTP (Time-based One-Time Password, RFC 6238)
- Compatible Google Authenticator, Authy, Microsoft Authenticator
- 8 codes de secours (format `XXXX-XXXX`, alphanumériques sans ambiguïté)
- Chaque code de secours est à usage unique
- Codes normalisés à la vérification (insensible à la casse, tirets/espaces ignorés)

**Flow complet d'activation :**
```
1. POST /setup  → QR code + secret + 8 backup codes
2. User scanne QR code dans Google Authenticator
3. POST /enable {token: "123456"}  → 2FA activé
```

**Utilisation des backup codes au login :**
```
1. POST /auth/login {username, password, scope: "ABCD-1234"}
2. Backend essaie TOTP → échoue
3. Backend essaie backup code → match
4. Code consommé (supprimé de la liste)
5. Login réussi
```

---

### **sessions.py**
**Rôle:** Gestion des sessions actives.

**Endpoints:**

1. **GET `/api/sessions`**
   - Liste sessions actives
   - Retourne: device, location, IP, last_activity
   - Session actuelle marquée

2. **DELETE `/api/sessions/{session_id}`**
   - Révoque une session spécifique
   - Déconnecte l'appareil

3. **DELETE `/api/sessions/all`**
   - Révoque toutes les sessions
   - Sauf la session actuelle
   - Déconnecte tous les appareils

**Informations Trackées:**
- Device (mobile/desktop/tablet)
- Navigateur et version
- Système d'exploitation
- Localisation (ville, pays)
- Adresse IP
- Dernière activité

---

### **password_reset.py**
**Rôle:** Réinitialisation mot de passe.

**Endpoints:**

1. **POST `/api/password-reset/request`**
   - Demande reset mot de passe
   - Body: `{email}`
   - Génère token (valide 1h)
   - Envoie email avec lien
   - Rate limit: 3 requêtes/heure

2. **POST `/api/password-reset/verify`**
   - Vérifie validité du token
   - Body: `{token}`
   - Retourne: `{valid: true/false}`

3. **POST `/api/password-reset/reset`**
   - Réinitialise le mot de passe
   - Body: `{token, new_password}`
   - Vérifie token non expiré
   - Hash nouveau mot de passe
   - Marque token utilisé
   - Révoque toutes les sessions

**Sécurité:**
- Token unique et aléatoire
- Expiration 1 heure
- Usage unique
- Email de confirmation

---

### **email_verification.py**
**Rôle:** Vérification des emails.

**Endpoints:**

1. **POST `/api/email-verification/send`**
   - Envoie email de vérification
   - Génère token (valide 24h)
   - Rate limit: 3 emails/heure
   - Nécessite: authentification

2. **POST `/api/email-verification/verify`**
   - Vérifie l'email
   - Body: `{token}`
   - Marque email vérifié
   - Marque token utilisé
   - Retourne: succès/erreur

3. **GET `/api/email-verification/status`**
   - Statut de vérification
   - Retourne: `{is_verified: bool}`

---

### **notifications.py**
**Rôle:** Système de notifications.

**Endpoints:**

1. **GET `/api/notifications`**
   - Liste toutes les notifications
   - Query: `?unread_only=true`
   - Pagination
   - Tri par date (récent d'abord)

2. **GET `/api/notifications/recent`**
   - 10 notifications récentes
   - Pour le badge de notification

3. **PUT `/api/notifications/{notification_id}/read`**
   - Marque comme lue
   - Met à jour read_at

4. **DELETE `/api/notifications/{notification_id}`**
   - Supprime une notification

5. **POST `/api/notifications/mark-all-read`**
   - Marque toutes comme lues

**Types de Notifications:**
- Nouvelle connexion détectée
- Mot de passe changé
- 2FA activé/désactivé
- Menace détectée dans analyse
- Tentative de connexion échouée

---

### **profile.py**
**Rôle:** Gestion du profil utilisateur.

**Endpoints:**

1. **GET `/api/profile`**
   - Récupère profil complet
   - Inclut: stats, sessions, 2FA status

2. **PUT `/api/profile`**
   - Met à jour profil
   - Body: `{username, email}`
   - Validation unicité

3. **POST `/api/profile/picture`**
   - Upload photo de profil
   - Multipart form data
   - Formats: JPG, PNG, GIF, WebP
   - Taille max: 5MB
   - Génère nom unique (UUID)
   - Stocke dans uploads/profile_pictures/

4. **GET `/api/profile/picture/{filename}`**
   - Récupère photo de profil
   - Retourne: fichier image

5. **DELETE `/api/profile/picture`**
   - Supprime photo de profil
   - Supprime fichier du disque

6. **DELETE `/api/profile`**
   - Supprime le compte
   - Body: `{password}` (confirmation)
   - Supprime toutes les données
   - Révoque sessions
   - Supprime fichiers

---

### **security.py**
**Rôle:** Endpoints de sécurité.

**Endpoints:**

1. **GET `/api/security/audit-logs`**
   - Logs d'audit personnels
   - Historique des actions
   - Filtres par action, date

2. **POST `/api/security/report-suspicious`**
   - Signaler activité suspecte
   - Body: `{description, session_id}`
   - Crée ticket support

3. **GET `/api/security/login-attempts`**
   - Tentatives de connexion récentes
   - Succès et échecs
   - Détection brute force

---

## 🔒 Authentification et Autorisation

### **Dépendances FastAPI**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Décode JWT
    # Vérifie expiration
    # Récupère user depuis DB
    # Retourne user ou 401
```

### **Vérification Rôles**

```python
async def require_admin(user = Depends(get_current_user)):
    if user.role not in ["admin", "superadmin"]:
        raise HTTPException(403, "Admin access required")
    return user

async def require_superadmin(user = Depends(get_current_user)):
    if user.role != "superadmin":
        raise HTTPException(403, "Superadmin access required")
    return user
```

---

Cette partie couvre toutes les routes API du backend PhishGuard.
