# 🔐 Guide de Configuration Google OAuth pour PhishGuard AI

Ce guide vous explique comment obtenir vos identifiants Google OAuth pour activer l'intégration Gmail dans PhishGuard AI.

## 📋 Prérequis

- Un compte Google (Gmail)
- Accès à Google Cloud Console
- 10-15 minutes

---

## 🚀 Étapes de Configuration

### Étape 1: Accéder à Google Cloud Console

1. Ouvrez votre navigateur et allez sur: **https://console.cloud.google.com/**
2. Connectez-vous avec votre compte Google
3. Acceptez les conditions d'utilisation si demandé

---

### Étape 2: Créer un Nouveau Projet

1. **Cliquez sur le sélecteur de projet** en haut de la page (à côté de "Google Cloud")
   
2. **Cliquez sur "NOUVEAU PROJET"** (NEW PROJECT)

3. **Remplissez les informations:**
   - **Nom du projet**: `PhishGuard-AI` (ou un nom de votre choix)
   - **Organisation**: Laissez par défaut (No organization)
   - **Emplacement**: Laissez par défaut

4. **Cliquez sur "CRÉER"** (CREATE)

5. **Attendez quelques secondes** que le projet soit créé

6. **Sélectionnez votre nouveau projet** dans le sélecteur de projet

---

### Étape 3: Activer l'API Gmail

1. Dans le menu de gauche, cliquez sur **"APIs & Services"** > **"Library"**
   - Ou utilisez la barre de recherche en haut et tapez "API Library"

2. Dans la bibliothèque d'API, **recherchez "Gmail API"**

3. **Cliquez sur "Gmail API"** dans les résultats

4. **Cliquez sur le bouton "ENABLE"** (ACTIVER)

5. Attendez que l'API soit activée (quelques secondes)

---

### Étape 4: Configurer l'Écran de Consentement OAuth

1. Dans le menu de gauche, allez à **"APIs & Services"** > **"OAuth consent screen"**

2. **Sélectionnez le type d'utilisateur:**
   - Choisissez **"External"** (Externe)
   - Cliquez sur **"CREATE"** (CRÉER)

3. **Remplissez les informations de l'application (Page 1/4):**
   
   **Informations sur l'application:**
   - **App name**: `PhishGuard AI`
   - **User support email**: Votre email Gmail
   - **App logo**: (Optionnel - vous pouvez le laisser vide)
   
   **Domaine de l'application:**
   - Laissez vide pour le développement local
   
   **Coordonnées du développeur:**
   - **Developer contact information**: Votre email Gmail
   
   - Cliquez sur **"SAVE AND CONTINUE"**

4. **Scopes (Page 2/4):**
   - Cliquez sur **"ADD OR REMOVE SCOPES"**
   - Recherchez et sélectionnez ces scopes:
     - `https://www.googleapis.com/auth/gmail.readonly` (Voir vos emails)
     - `https://www.googleapis.com/auth/userinfo.email` (Voir votre email)
     - `https://www.googleapis.com/auth/userinfo.profile` (Voir votre profil)
   - Cliquez sur **"UPDATE"**
   - Cliquez sur **"SAVE AND CONTINUE"**

5. **Test users (Page 3/4):**
   - Cliquez sur **"ADD USERS"**
   - Ajoutez votre email Gmail (et ceux des testeurs)
   - Cliquez sur **"ADD"**
   - Cliquez sur **"SAVE AND CONTINUE"**

6. **Summary (Page 4/4):**
   - Vérifiez les informations
   - Cliquez sur **"BACK TO DASHBOARD"**

---

### Étape 5: Créer les Identifiants OAuth 2.0

1. Dans le menu de gauche, allez à **"APIs & Services"** > **"Credentials"**

2. **Cliquez sur "+ CREATE CREDENTIALS"** en haut

3. **Sélectionnez "OAuth client ID"**

4. **Configurez le client OAuth:**
   
   - **Application type**: Sélectionnez **"Web application"**
   
   - **Name**: `PhishGuard AI Web Client`
   
   - **Authorized JavaScript origins**: Cliquez sur **"+ ADD URI"**
     ```
     http://localhost:5174
     ```
     Ajoutez aussi (cliquez à nouveau sur "+ ADD URI"):
     ```
     http://localhost:5173
     ```
   
   - **Authorized redirect URIs**: Cliquez sur **"+ ADD URI"**
     ```
     http://localhost:8000/api/gmail/callback
     ```
     Ajoutez aussi:
     ```
     http://localhost:8000/api/email-providers/gmail/callback
     ```

5. **Cliquez sur "CREATE"**

---

### Étape 6: Récupérer vos Identifiants

1. Une fenêtre popup s'affiche avec vos identifiants:
   - **Client ID**: Commence par quelque chose comme `123456789-abc...apps.googleusercontent.com`
   - **Client Secret**: Une chaîne de caractères aléatoire

2. **IMPORTANT**: 
   - ✅ **Copiez le Client ID**
   - ✅ **Copiez le Client Secret**
   - ⚠️ **Ne partagez JAMAIS ces identifiants publiquement**

3. Vous pouvez aussi télécharger le JSON en cliquant sur **"DOWNLOAD JSON"** (optionnel)

4. Cliquez sur **"OK"**

---

### Étape 7: Configurer PhishGuard AI

1. **Ouvrez le fichier `.env`** dans le dossier `backend/`

2. **Remplacez les valeurs** par vos identifiants:

```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=votre-client-id-ici.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=votre-client-secret-ici
GOOGLE_REDIRECT_URI=http://localhost:8000/api/gmail/callback
```

**Exemple:**
```env
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-AbCdEfGhIjKlMnOpQrStUvWxYz
GOOGLE_REDIRECT_URI=http://localhost:8000/api/gmail/callback
```

3. **Sauvegardez le fichier**

---

### Étape 8: Redémarrer le Backend

1. **Arrêtez le serveur backend** (Ctrl+C dans le terminal)

2. **Relancez le backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

3. Vous devriez voir dans les logs:
```
Gmail OAuth credentials loaded successfully
```

---

## ✅ Vérification

### Tester l'Intégration Gmail

1. **Ouvrez PhishGuard AI** dans votre navigateur: `http://localhost:5174`

2. **Connectez-vous** à votre compte PhishGuard

3. **Allez dans l'onglet "Email"** ou cliquez sur le bouton Gmail

4. **Cliquez sur "Connecter Gmail"**

5. **Vous serez redirigé vers Google** pour autoriser l'accès

6. **Sélectionnez votre compte Gmail**

7. **Autorisez les permissions** demandées

8. **Vous serez redirigé vers PhishGuard** avec vos emails Gmail

---

## 🔧 Dépannage

### Erreur: "redirect_uri_mismatch"

**Solution:**
- Vérifiez que l'URI de redirection dans Google Cloud Console correspond exactement à:
  ```
  http://localhost:8000/api/gmail/callback
  ```
- Pas d'espace, pas de slash à la fin
- Vérifiez aussi que le port est correct (8000)

### Erreur: "Access blocked: This app's request is invalid"

**Solution:**
- Vérifiez que vous avez bien configuré l'écran de consentement OAuth
- Ajoutez votre email dans les "Test users"
- Attendez quelques minutes que les changements se propagent

### Erreur: "Gmail OAuth credentials not found"

**Solution:**
- Vérifiez que le fichier `.env` est bien dans le dossier `backend/`
- Vérifiez qu'il n'y a pas d'espaces autour du `=`
- Redémarrez le serveur backend

### L'API Gmail n'est pas activée

**Solution:**
- Retournez dans Google Cloud Console
- Allez dans "APIs & Services" > "Library"
- Recherchez "Gmail API" et activez-la

---

## 📝 Notes Importantes

### Limites de Développement

- En mode "Testing", seuls les utilisateurs ajoutés dans "Test users" peuvent se connecter
- Limite de 100 utilisateurs test maximum
- Pour une utilisation en production, vous devrez publier l'application (vérification Google)

### Sécurité

- ⚠️ **Ne commitez JAMAIS le fichier `.env` sur Git**
- ⚠️ **Ne partagez JAMAIS vos identifiants OAuth**
- ✅ Le fichier `.env` est déjà dans `.gitignore`
- ✅ Utilisez des variables d'environnement en production

### Quotas

- Gmail API a des quotas gratuits généreux:
  - 1 milliard de requêtes par jour
  - 250 requêtes par seconde par utilisateur
- Largement suffisant pour un usage normal

---

## 🎯 Prochaines Étapes

Une fois l'intégration Gmail configurée, vous pouvez:

1. ✅ Scanner votre boîte Gmail directement
2. ✅ Analyser plusieurs emails en un clic
3. ✅ Recevoir des alertes sur les emails suspects
4. ✅ Voir l'historique de vos analyses

---

## 📚 Ressources Supplémentaires

- [Documentation Gmail API](https://developers.google.com/gmail/api)
- [Guide OAuth 2.0 Google](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com/)

---

## 💡 Besoin d'Aide?

Si vous rencontrez des problèmes:

1. Vérifiez que toutes les étapes ont été suivies
2. Consultez la section Dépannage ci-dessus
3. Vérifiez les logs du backend pour les erreurs
4. Ouvrez une issue sur GitHub avec les détails de l'erreur

---

**Créé par PhishGuard AI Team** 🛡️
