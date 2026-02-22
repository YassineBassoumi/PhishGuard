# Documentation Backend - Partie 4: Services

## 🔧 Services (app/services/)

Les services contiennent la logique métier de l'application. Ils sont appelés par les routes et interagissent avec la base de données et les APIs externes.

---

### **auth_service.py**
**Rôle:** Logique d'authentification et gestion des tokens.

**Fonctions Principales:**

1. **`create_access_token(data: dict)`**
   - Crée un JWT token
   - Ajoute expiration (30 min)
   - Signe avec SECRET_KEY
   - Retourne: token string

2. **`verify_token(token: str)`**
   - Décode et vérifie JWT
   - Vérifie expiration
   - Retourne: payload ou None

3. **`get_password_hash(password: str)`**
   - Hash le mot de passe avec bcrypt
   - Salt automatique
   - Retourne: hash string

4. **`verify_password(plain_password: str, hashed_password: str)`**
   - Vérifie mot de passe
   - Compare avec bcrypt
   - Retourne: bool

5. **`authenticate_user(email: str, password: str, db)`**
   - Récupère user par email
   - Vérifie mot de passe
   - Vérifie compte actif
   - Retourne: user ou None

**Utilisation:**
```python
# Dans auth.py route
token = create_access_token({"sub": user.email})
```

---

### **detector.py**
**Rôle:** Façade pour le système de détection ML.

**Classe:** `PhishingDetector`

**Méthodes:**

1. **`analyze_email(content: str)`**
   - Analyse contenu email
   - Utilise modèle ML email
   - Extrait features
   - Retourne: (threat_level, confidence, features, recommendations)

2. **`analyze_url(url: str)`**
   - Analyse URL
   - Utilise modèle ML URL
   - Extrait features (12 caractéristiques)
   - Retourne: (threat_level, confidence, features, recommendations)

**Modèles Chargés:**
- `phishing_model.pkl` - SVM pour emails
- `phishing_url_model_final_v3.pkl` - SVM pour URLs
- `vectorizer.pkl` - TF-IDF vectorizer

**Singleton:**
```python
detector = PhishingDetector()  # Instance unique
```

---

### **detection/** (Module ML)
**Rôle:** Système de détection modulaire et organisé.

**Structure:**
```
detection/
├── __init__.py
├── email_detector.py      # Détection emails
├── url_detector.py        # Détection URLs
├── feature_extractors/    # Extraction de features
│   ├── email_features.py
│   └── url_features.py
├── models/                # Chargement modèles ML
│   ├── model_loader.py
│   └── model_config.py
└── utils/                 # Utilitaires
    ├── constants.py
    └── recommendations.py
```

#### **email_detector.py**
**Classe:** `EmailDetector`

**Méthode:** `analyze(content: str)`
- Nettoie le contenu
- Extrait features (mots-clés suspects, urgence, etc.)
- Vectorise avec TF-IDF
- Prédit avec modèle SVM
- Calcule score de confiance
- Génère recommandations
- Retourne: (threat_level, confidence, features, recommendations)

**Features Détectées:**
- Mots-clés de phishing (urgent, verify, suspended)
- Demandes d'informations personnelles
- Liens suspects
- Fautes d'orthographe
- Ton urgent/menaçant

#### **url_detector.py**
**Classe:** `URLDetector`

**Méthode:** `analyze(url: str)`
- Parse l'URL
- Extrait 12 features:
  1. Utilise adresse IP
  2. Longueur URL
  3. URL shortener
  4. Symbole @
  5. Double slash
  6. Tiret dans domaine
  7. Nombre de sous-domaines
  8. HTTPS
  9. Port non-standard
  10. Mots-clés suspects
  11. Parties de sous-domaine
  12. TLD suspect
- Prédit avec modèle SVM
- Génère recommandations
- Retourne: (threat_level, confidence, features, recommendations)

#### **feature_extractors/email_features.py**
**Fonctions:**

1. **`extract_email_features(content: str)`**
   - Extrait features textuelles
   - Compte mots-clés suspects
   - Détecte patterns de phishing
   - Retourne: dict de features

2. **`calculate_rule_based_threat_score(content: str)`**
   - Score basé sur règles
   - Complément au ML
   - Retourne: score 0-1

#### **feature_extractors/url_features.py**
**Fonction:** `extract_url_features(url: str)`
- Extrait les 12 features d'URL
- Retourne: liste de valeurs [-1, 0, 1]

#### **models/model_loader.py**
**Classe:** `ModelLoader`

**Méthodes:**
- `load_email_model()` - Charge modèle email
- `load_url_model()` - Charge modèle URL
- `load_vectorizer()` - Charge vectorizer

**Lazy Loading:**
- Modèles chargés à la première utilisation
- Économise mémoire au démarrage

#### **utils/recommendations.py**
**Fonction:** `generate_recommendations(threat_level, features)`
- Génère recommandations personnalisées
- Basé sur threat_level et features détectées
- Retourne: liste de strings

**Exemples:**
- "Ne cliquez pas sur les liens"
- "Vérifiez l'expéditeur"
- "Contactez directement l'organisation"

---

### **gmail_service.py**
**Rôle:** Interaction avec Gmail API.

**Fonctions:**

1. **`get_gmail_auth_url(user_id: str)`**
   - Génère URL OAuth2 Google
   - State parameter pour sécurité
   - Scopes: gmail.readonly
   - Retourne: auth_url

2. **`exchange_code_for_tokens(code: str)`**
   - Échange code OAuth contre tokens
   - Récupère access_token et refresh_token
   - Retourne: tokens dict

3. **`get_user_email(access_token: str)`**
   - Récupère adresse email Gmail
   - Utilise Gmail API
   - Retourne: email string

4. **`fetch_emails(access_token: str, max_results: int)`**
   - Récupère emails Gmail
   - Parse et formate
   - Retourne: liste d'emails

5. **`refresh_access_token(refresh_token: str)`**
   - Rafraîchit access_token expiré
   - Utilise refresh_token
   - Retourne: nouveau access_token

**Configuration:**
- Client ID et Secret depuis .env
- Redirect URI: http://localhost:8000/api/gmail/callback

---

### **outlook_service.py**
**Rôle:** Interaction avec Microsoft Graph API.

**Fonctions:**

1. **`get_outlook_auth_url(user_id: str)`**
   - Génère URL OAuth2 Microsoft
   - Scopes: Mail.Read
   - Retourne: auth_url

2. **`exchange_code_for_tokens(code: str)`**
   - Échange code contre tokens
   - Microsoft Identity Platform
   - Retourne: tokens dict

3. **`get_user_email(access_token: str)`**
   - Récupère adresse email Outlook
   - Microsoft Graph API
   - Retourne: email string

4. **`fetch_emails(access_token: str, max_results: int)`**
   - Récupère emails Outlook
   - Graph API endpoint: /me/messages
   - Retourne: liste d'emails

5. **`refresh_access_token(refresh_token: str)`**
   - Rafraîchit token expiré
   - Retourne: nouveau token

---

### **unified_email_service.py**
**Rôle:** Service unifié pour tous les providers.

**Classe:** `UnifiedEmailService`

**Méthodes:**

1. **`get_provider_service(provider: str)`**
   - Retourne service approprié (Gmail/Outlook)
   - Factory pattern

2. **`fetch_emails_from_provider(user_id, provider, max_results)`**
   - Récupère emails du provider
   - Gère refresh token automatique
   - Unifie le format de retour

3. **`disconnect_provider(user_id, provider, db)`**
   - Déconnecte provider
   - Supprime credentials DB
   - Révoque tokens

---

### **email_service.py**
**Rôle:** Envoi d'emails (notifications, vérification, etc.).

**Configuration SMTP:**
```python
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
```

**Fonctions:**

1. **`send_email(to: str, subject: str, html_content: str)`**
   - Envoie email HTML
   - Utilise SMTP
   - Gère erreurs

2. **`send_verification_email(to: str, token: str)`**
   - Email de vérification
   - Lien avec token
   - Template HTML

3. **`send_password_reset_email(to: str, token: str)`**
   - Email reset mot de passe
   - Lien avec token
   - Expiration 1h

4. **`send_security_alert(to: str, alert_type: str, details: dict)`**
   - Alertes de sécurité
   - Nouvelle connexion
   - Changement mot de passe
   - Template personnalisé

**Templates HTML:**
Situés dans `services/email_templates/`:
- `new_login_alert.html`
- `password_changed_alert.html`
- `two_factor_changed_alert.html`
- `brute_force_alert.html`
- `dangerous_email_alert.html`
- `database_error_alert.html`

---

### **notification_service.py**
**Rôle:** Gestion des notifications in-app.

**Fonctions:**

1. **`create_notification(user_id, type, title, message, severity, db)`**
   - Crée notification en DB
   - Types: security_alert, threat_detected, system_update
   - Severities: info, warning, critical

2. **`get_user_notifications(user_id, unread_only, db)`**
   - Récupère notifications utilisateur
   - Filtre lu/non-lu
   - Tri par date

3. **`mark_as_read(notification_id, db)`**
   - Marque notification lue
   - Met à jour read_at

4. **`delete_notification(notification_id, db)`**
   - Supprime notification

5. **`send_security_notification(user_id, event_type, details, db)`**
   - Notification + Email
   - Double canal de communication

---

### **session_service.py**
**Rôle:** Gestion des sessions utilisateur.

**Fonctions:**

1. **`create_session(user_id, jti, request, db)`**
   - Crée nouvelle session
   - Extrait device info
   - Géolocalise IP
   - Stocke en DB

2. **`get_user_sessions(user_id, db)`**
   - Liste sessions actives
   - Tri par last_activity

3. **`revoke_session(session_id, db)`**
   - Révoque session
   - Marque inactive

4. **`revoke_all_sessions(user_id, except_jti, db)`**
   - Révoque toutes sauf actuelle
   - Déconnexion massive

5. **`update_session_activity(jti, db)`**
   - Met à jour last_activity
   - Appelé à chaque requête

6. **`cleanup_expired_sessions(db)`**
   - Supprime sessions expirées
   - Tâche de maintenance

---

### **two_factor_service.py**
**Rôle:** Authentification à deux facteurs.

**Fonctions:**

1. **`generate_totp_secret()`**
   - Génère secret TOTP
   - Base32 encoded
   - Retourne: secret string

2. **`generate_qr_code(secret, email)`**
   - Génère QR code
   - Format: otpauth://totp/...
   - Retourne: image base64

3. **`verify_totp_code(secret, code)`**
   - Vérifie code 6 chiffres
   - Fenêtre de tolérance: ±1 période
   - Retourne: bool

4. **`generate_backup_codes(count=10)`**
   - Génère codes de secours
   - 10 codes aléatoires
   - Retourne: liste de codes

5. **`enable_2fa(user_id, password, db)`**
   - Active 2FA pour user
   - Vérifie mot de passe
   - Génère secret + QR
   - Retourne: {secret, qr_code}

6. **`disable_2fa(user_id, password, code, db)`**
   - Désactive 2FA
   - Vérifie mot de passe + code
   - Supprime secret

---

### **password_reset_service.py**
**Rôle:** Réinitialisation mot de passe.

**Fonctions:**

1. **`create_reset_token(user_id, db)`**
   - Génère token unique
   - Expiration 1h
   - Stocke en DB
   - Retourne: token

2. **`verify_reset_token(token, db)`**
   - Vérifie validité token
   - Vérifie expiration
   - Vérifie non utilisé
   - Retourne: user ou None

3. **`reset_password(token, new_password, db)`**
   - Réinitialise mot de passe
   - Hash nouveau password
   - Marque token utilisé
   - Révoque sessions

4. **`send_reset_email(email, token)`**
   - Envoie email avec lien
   - Lien: /reset-password?token=...

---

### **email_verification_service.py**
**Rôle:** Vérification des emails.

**Fonctions:**

1. **`create_verification_token(user_id, db)`**
   - Génère token unique
   - Expiration 24h
   - Stocke en DB

2. **`verify_email_token(token, db)`**
   - Vérifie token
   - Marque email vérifié
   - Marque token utilisé

3. **`send_verification_email(email, token)`**
   - Envoie email de vérification
   - Lien: /verify-email?token=...

4. **`resend_verification_email(user_id, db)`**
   - Renvoie email
   - Rate limit: 3/heure

---

### **stats_service.py**
**Rôle:** Calcul et agrégation des statistiques.

**Fonctions:**

1. **`get_user_statistics(user_id, db)`**
   - Statistiques utilisateur
   - Total analyses
   - Distribution menaces
   - Graphiques

2. **`update_statistics(user_id, threat_level, db)`**
   - Met à jour stats après analyse
   - Incrémente compteurs

3. **`get_admin_statistics(db)`**
   - Statistiques globales
   - Total utilisateurs
   - Analyses par jour
   - Menaces détectées

4. **`get_analysis_trends(user_id, days, db)`**
   - Tendances sur X jours
   - Graphique temporel

---

### **audit_service.py**
**Rôle:** Logging des actions pour audit.

**Fonctions:**

1. **`log_action(user_id, action, resource, details, request, status, db)`**
   - Crée log d'audit
   - Capture IP, user_agent
   - Stocke en DB

2. **`get_user_audit_logs(user_id, db)`**
   - Logs personnels
   - Historique actions

3. **`get_admin_audit_logs(filters, db)`**
   - Tous les logs (admin)
   - Filtres multiples

**Actions Loggées:**
- login/logout
- register
- password_change
- 2fa_enable/disable
- analysis
- admin_action
- profile_update

---

Cette partie couvre tous les services du backend PhishGuard.
