# Documentation Complète du Frontend PhishGuard

## 📋 Vue d'Ensemble

PhishGuard est une application web de détection de phishing construite avec React. Le frontend communique avec une API backend FastAPI pour analyser les emails et URLs suspects.

---

## 🏗️ Architecture Générale

### Technologies Principales
- **React 18** - Bibliothèque UI avec hooks modernes
- **Vite** - Build tool ultra-rapide pour le développement
- **React Router DOM** - Navigation entre les pages
- **Axios** - Client HTTP pour les appels API
- **Tailwind CSS** - Framework CSS utility-first
- **Recharts** - Bibliothèque de graphiques pour les statistiques
- **date-fns** - Manipulation des dates

---

## 📁 Structure des Dossiers

```
frontend/
├── public/              # Fichiers statiques
├── src/                 # Code source principal
│   ├── assets/         # Images et ressources
│   ├── components/     # Composants React réutilisables
│   ├── contexts/       # Contextes React (état global)
│   ├── lib/            # Utilitaires et helpers
│   ├── pages/          # Pages complètes de l'application
│   ├── services/       # Services API
│   ├── App.jsx         # Composant racine
│   ├── main.jsx        # Point d'entrée
│   └── index.css       # Styles globaux
├── dist/               # Build de production (généré)
├── node_modules/       # Dépendances npm
└── Configuration files
```

---

## 🎯 Fichiers de Configuration

### 1. **package.json**
Définit les dépendances et scripts du projet.

**Dépendances principales:**
- `react`, `react-dom` - Framework UI
- `react-router-dom` - Routing
- `axios` - Requêtes HTTP
- `recharts` - Graphiques
- `tailwindcss` - Styling
- `date-fns` - Gestion des dates

**Scripts:**
- `npm run dev` - Lance le serveur de développement
- `npm run build` - Crée le build de production
- `npm run preview` - Prévisualise le build

### 2. **vite.config.js**
Configuration de Vite (build tool).
- Configure le plugin React
- Définit le port de développement (5173)
- Optimise les builds

### 3. **tailwind.config.js**
Configuration de Tailwind CSS.
- Définit les chemins des fichiers à scanner
- Configure le thème personnalisé
- Active les plugins nécessaires

### 4. **index.html**
Point d'entrée HTML de l'application.
- Charge le script principal (`main.jsx`)
- Définit les métadonnées de la page

---

## 🔧 Fichiers Principaux

### **src/main.jsx**
**Rôle:** Point d'entrée de l'application React.

**Fonctionnalité:**
```javascript
- Importe React et ReactDOM
- Importe le composant App
- Importe les styles globaux
- Monte l'application sur le DOM (#root)
```

**Utilisation:**
C'est le premier fichier exécuté. Il initialise React et rend le composant App dans le DOM.

---

### **src/App.jsx**
**Rôle:** Composant racine qui gère le routing et la structure globale.

**Fonctionnalité:**
- Configure React Router pour la navigation
- Enveloppe l'app avec les Providers (AuthContext, EmailProviderContext)
- Définit toutes les routes de l'application
- Gère les routes protégées (nécessitant authentification)

**Routes principales:**
- `/` - Page d'accueil
- `/login` - Connexion
- `/register` - Inscription
- `/dashboard` - Tableau de bord (protégé)
- `/admin` - Panel administrateur (protégé)
- `/verify-email` - Vérification email
- `/reset-password` - Réinitialisation mot de passe

---

## 📦 Contextes (Gestion d'État Global)

### **src/contexts/AuthContext.jsx**
**Rôle:** Gère l'authentification utilisateur dans toute l'application.

**État géré:**
- `currentUser` - Informations de l'utilisateur connecté
- `token` - Token JWT d'authentification
- `loading` - État de chargement

**Fonctions fournies:**
- `login(email, password)` - Connexion utilisateur
- `register(userData)` - Inscription
- `logout()` - Déconnexion
- `updateUser(userData)` - Mise à jour profil

**Utilisation:**
```javascript
const { currentUser, login, logout } = useAuth();
```

**Stockage:**
- Token stocké dans `localStorage` sous la clé `'auth_token'`
- Persiste entre les sessions

---

### **src/contexts/EmailProviderContext.jsx**
**Rôle:** Gère la connexion aux fournisseurs d'email (Gmail, Outlook).

**État géré:**
- `connectedProviders` - Liste des fournisseurs connectés
- `emails` - Emails récupérés
- `loading` - État de chargement

**Fonctions fournies:**
- `connectProvider(provider)` - Connecte un fournisseur
- `fetchEmails(provider)` - Récupère les emails
- `disconnectProvider(provider)` - Déconnecte un fournisseur

**Utilisation:**
```javascript
const { connectedProviders, fetchEmails } = useEmailProvider();
```

---

## 🧩 Composants Principaux

### **Composants d'Authentification**

#### **Login.jsx**
**Rôle:** Formulaire de connexion.

**Fonctionnalités:**
- Champs email et mot de passe
- Validation des entrées
- Gestion des erreurs
- Lien vers inscription et mot de passe oublié
- Redirection après connexion réussie

**Utilisation:** Accessible via `/login`

---

#### **Register.jsx**
**Rôle:** Formulaire d'inscription.

**Fonctionnalités:**
- Champs: nom d'utilisateur, email, mot de passe, confirmation
- Indicateur de force du mot de passe
- Validation en temps réel
- Envoi email de vérification après inscription
- Détection automatique du fournisseur email

**Utilisation:** Accessible via `/register`

---

#### **ForgotPassword.jsx**
**Rôle:** Demande de réinitialisation de mot de passe.

**Fonctionnalités:**
- Saisie de l'email
- Envoi d'un lien de réinitialisation
- Feedback utilisateur

**Utilisation:** Accessible via `/forgot-password`

---

#### **ResetPassword.jsx**
**Rôle:** Réinitialisation du mot de passe via token.

**Fonctionnalités:**
- Récupère le token depuis l'URL
- Formulaire nouveau mot de passe
- Validation et confirmation
- Redirection vers login après succès

**Utilisation:** Accessible via `/reset-password?token=...`

---

#### **VerifyEmail.jsx**
**Rôle:** Vérification de l'email utilisateur.

**Fonctionnalités:**
- Récupère le token depuis l'URL
- Vérifie automatiquement l'email
- Affiche le statut (succès/erreur)
- Redirection automatique

**Utilisation:** Accessible via `/verify-email?token=...`

---

### **Composants de Navigation**

#### **Navbar.jsx**
**Rôle:** Barre de navigation principale (page d'accueil).

**Fonctionnalités:**
- Logo PhishGuard
- Liens de navigation (Accueil, Fonctionnalités, Comment ça marche)
- Boutons Connexion/Inscription
- Responsive (menu burger sur mobile)

**Utilisation:** Affiché sur la page d'accueil uniquement

---

#### **Sidebar.jsx**
**Rôle:** Menu latéral de navigation (dashboard).

**Fonctionnalités:**
- Logo et nom d'utilisateur
- Photo de profil
- Menu de navigation:
  - Analyser (analyse simple)
  - Analyse en Masse
  - Tableau de Bord
  - Email (connexion fournisseurs)
  - Paramètres
  - Admin Panel (si admin)
- Bouton de déconnexion

**Utilisation:** Affiché dans toutes les pages authentifiées

---

### **Composants de la Page d'Accueil**

#### **HomePage.jsx**
**Rôle:** Page d'accueil principale du site.

**Structure:**
```
- Navbar
- Hero (section héro)
- FeaturesSection (fonctionnalités)
- HowItWorks (comment ça marche)
- Integrations (intégrations email)
- SignupCTA (appel à l'action)
- Footer
```

**Utilisation:** Route `/`

---

#### **Hero.jsx**
**Rôle:** Section héro de la page d'accueil.

**Fonctionnalités:**
- Titre accrocheur
- Description du service
- Bouton "Commencer"
- Illustration/animation
- Design moderne avec gradients

---

#### **FeaturesSection.jsx**
**Rôle:** Présente les fonctionnalités principales.

**Fonctionnalités affichées:**
- Détection IA avancée
- Analyse en temps réel
- Protection multi-couches
- Rapports détaillés
- Interface intuitive

**Design:** Cartes avec icônes et descriptions

---

#### **HowItWorks.jsx**
**Rôle:** Explique le fonctionnement en 3 étapes.

**Étapes:**
1. Connectez vos emails (Gmail/Outlook)
2. Analysez vos messages
3. Recevez des alertes

**Design:** Timeline avec numéros et descriptions

---

#### **Integrations.jsx**
**Rôle:** Montre les intégrations disponibles.

**Fournisseurs:**
- Gmail (disponible)
- Outlook (disponible)

**Design:** Cartes avec logos et statistiques d'utilisateurs

---

#### **SignupCTA.jsx**
**Rôle:** Appel à l'action pour l'inscription.

**Fonctionnalités:**
- Message persuasif
- Bouton "Créer un compte gratuit"
- Design attractif

---

### **Composants d'Analyse**

#### **AnalysisForm.jsx**
**Rôle:** Formulaire d'analyse d'URL ou email.

**Fonctionnalités:**
- Onglets: URL / Email / Texte
- Zone de saisie
- Bouton "Analyser"
- Validation des entrées
- Appel API backend
- Affichage des résultats

**Utilisation:** Page "Analyser" du dashboard

---

#### **ResultsDisplay.jsx**
**Rôle:** Affiche les résultats d'analyse.

**Informations affichées:**
- Niveau de menace (Sûr/Suspect/Dangereux)
- Score de confiance
- Indicateurs détectés
- Recommandations
- Visualisation graphique

**Design:** Cartes colorées selon le niveau de risque

---

#### **BulkAnalysis/index.jsx**
**Rôle:** Analyse en masse d'URLs/emails.

**Fonctionnalités:**
- Upload de fichier CSV/TXT
- Analyse multiple simultanée
- Barre de progression
- Tableau de résultats
- Export des résultats
- Statistiques globales

**Utilisation:** Page "Analyse en Masse"

---

### **Composants Email**

#### **EmailProviderSelector.jsx**
**Rôle:** Sélection et connexion des fournisseurs email.

**Fonctionnalités:**
- Cartes Gmail et Outlook
- Bouton "Connecter"
- OAuth2 flow
- Indication des fournisseurs connectés
- Suggestion basée sur l'email d'inscription

**Utilisation:** Page "Email" du dashboard

---

#### **MultiProviderEmailList.jsx**
**Rôle:** Liste unifiée des emails de tous les fournisseurs.

**Fonctionnalités:**
- Affichage des emails Gmail + Outlook
- Filtres par fournisseur
- Recherche
- Sélection multiple
- Analyse d'emails sélectionnés
- Pagination

**Design:** Liste avec icônes de fournisseur

---

#### **EmailSearchBar.jsx**
**Rôle:** Barre de recherche pour les emails.

**Fonctionnalités:**
- Recherche par expéditeur
- Recherche par sujet
- Recherche par contenu
- Filtres avancés
- Suggestions en temps réel

---

### **Composants Dashboard**

#### **Dashboard.jsx**
**Rôle:** Tableau de bord principal avec statistiques.

**Sections:**
- Statistiques globales (cartes)
  - Total analyses
  - Menaces détectées
  - Taux de sécurité
- Graphiques:
  - Analyses par jour (ligne)
  - Distribution des menaces (camembert)
  - Tendances mensuelles (barres)
- Historique récent
- Activité récente

**Utilisation:** Page principale après connexion

---

### **Composants Profil Utilisateur**

#### **UserProfile.jsx**
**Rôle:** Page de profil et paramètres utilisateur.

**Sections:**
- Informations personnelles
  - Nom d'utilisateur
  - Email
  - Photo de profil
- Sécurité
  - Changement de mot de passe
  - Authentification 2FA
  - Sessions actives
- Suppression de compte

**Utilisation:** Page "Paramètres"

---

#### **ProfilePictureUpload.jsx**
**Rôle:** Upload et gestion de la photo de profil.

**Fonctionnalités:**
- Prévisualisation de l'image
- Upload (drag & drop ou clic)
- Validation (format, taille max 5MB)
- Crop/redimensionnement
- Suppression
- Formats acceptés: JPG, PNG, GIF, WebP

---

#### **TwoFactorSettings.jsx**
**Rôle:** Configuration de l'authentification à deux facteurs.

**Fonctionnalités:**
- Activation/désactivation 2FA
- Génération QR code
- Saisie code de vérification
- Codes de secours
- Instructions détaillées

---

#### **SessionManagement.jsx**
**Rôle:** Gestion des sessions actives.

**Fonctionnalités:**
- Liste des sessions actives
- Informations par session:
  - Appareil
  - Localisation
  - Date de connexion
  - IP
- Déconnexion d'une session
- Déconnexion de toutes les sessions

---

#### **AccountDeletion.jsx**
**Rôle:** Suppression du compte utilisateur.

**Fonctionnalités:**
- Avertissements
- Confirmation par mot de passe
- Double confirmation
- Suppression définitive
- Feedback utilisateur

---

### **Composants Admin**

#### **admin/AdminLayout.jsx**
**Rôle:** Layout du panel administrateur.

**Structure:**
- Header avec photo de profil admin
- Navigation admin
- Zone de contenu
- Statistiques globales

---

#### **admin/AdminDashboard.jsx**
**Rôle:** Dashboard administrateur.

**Fonctionnalités:**
- Statistiques système
- Gestion utilisateurs
- Logs d'activité
- Métriques de performance
- Graphiques avancés

---

#### **admin/UserManagement.jsx**
**Rôle:** Gestion des utilisateurs.

**Fonctionnalités:**
- Liste de tous les utilisateurs
- Recherche et filtres
- Actions:
  - Bannir/débannir
  - Promouvoir admin
  - Supprimer compte
  - Voir détails
- Statistiques utilisateurs

---

### **Composants Utilitaires**

#### **Toast.jsx**
**Rôle:** Notifications toast (messages temporaires).

**Types:**
- Success (vert)
- Error (rouge)
- Warning (orange)
- Info (bleu)

**Fonctionnalités:**
- Auto-dismiss après 3-5 secondes
- Animation d'entrée/sortie
- Empilable
- Position configurable

---

#### **LoadingScreen.jsx**
**Rôle:** Écran de chargement.

**Fonctionnalités:**
- Spinner animé
- Message de chargement
- Overlay semi-transparent
- Bloque les interactions

---

#### **NotificationCenter.jsx**
**Rôle:** Centre de notifications.

**Fonctionnalités:**
- Badge avec nombre de notifications
- Dropdown avec liste
- Types de notifications:
  - Alertes de sécurité
  - Nouvelles menaces
  - Mises à jour système
- Marquer comme lu
- Supprimer notification

---

#### **PasswordStrengthIndicator.jsx**
**Rôle:** Indicateur de force du mot de passe.

**Critères évalués:**
- Longueur (min 8 caractères)
- Majuscules
- Minuscules
- Chiffres
- Caractères spéciaux

**Affichage:**
- Barre de progression colorée
- Labels: Faible/Moyen/Fort/Très fort
- Liste des critères manquants

---

#### **WelcomeRedirect.jsx**
**Rôle:** Modal de bienvenue après inscription.

**Fonctionnalités:**
- Message de bienvenue
- Suggestion de fournisseur email
- Compte à rebours avant redirection
- Bouton "Passer"
- Animation

---

## 🔌 Services API

### **src/services/adminApi.js**
**Rôle:** Fonctions pour les appels API admin.

**Fonctions:**
- `getAllUsers()` - Liste tous les utilisateurs
- `banUser(userId)` - Bannir un utilisateur
- `unbanUser(userId)` - Débannir
- `promoteToAdmin(userId)` - Promouvoir admin
- `deleteUser(userId)` - Supprimer compte
- `getSystemStats()` - Statistiques système

**Configuration:**
- Base URL: `http://localhost:8000/api/admin`
- Headers: Authorization Bearer token

---

## 🎨 Styles

### **Approche CSS**
Le projet utilise une combinaison de:
1. **Tailwind CSS** - Classes utilitaires
2. **CSS Modules** - Fichiers .css par composant
3. **CSS Global** - index.css pour les styles de base

### **Thème**
- Couleurs principales:
  - Primary: Bleu (#3B82F6)
  - Success: Vert (#10B981)
  - Warning: Orange (#F59E0B)
  - Danger: Rouge (#EF4444)
- Typographie: Inter, system fonts
- Espacements: Système 4px (0.25rem)

---

## 🔐 Sécurité

### **Authentification**
- JWT tokens stockés dans localStorage
- Expiration automatique des tokens
- Refresh token mechanism
- Protection CSRF

### **Routes Protégées**
- Vérification du token avant accès
- Redirection vers login si non authentifié
- Rôles utilisateur (user/admin)

### **Validation**
- Validation côté client (formulaires)
- Sanitization des entrées
- Protection XSS
- Validation des uploads

---

## 📊 Flux de Données

### **Flux d'Authentification**
```
1. Utilisateur saisit credentials
2. Login.jsx → AuthContext.login()
3. AuthContext → API POST /auth/login
4. API retourne token + user data
5. Token stocké dans localStorage
6. User data dans AuthContext
7. Redirection vers dashboard
```

### **Flux d'Analyse**
```
1. Utilisateur saisit URL/email
2. AnalysisForm.jsx → API POST /analysis
3. API analyse avec ML model
4. Résultats retournés
5. ResultsDisplay.jsx affiche résultats
6. Sauvegarde dans historique
```

### **Flux Email**
```
1. Utilisateur clique "Connecter Gmail"
2. EmailProviderSelector → API /gmail/auth
3. Redirection OAuth Google
4. Callback avec code
5. API échange code contre tokens
6. Tokens stockés backend
7. Fetch emails via API
8. Affichage dans MultiProviderEmailList
```

---

## 🚀 Déploiement

### **Build de Production**
```bash
npm run build
```
Génère le dossier `dist/` avec:
- HTML minifié
- CSS optimisé et minifié
- JavaScript bundlé et minifié
- Assets optimisés

### **Variables d'Environnement**
Créer `.env` à la racine:
```
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=PhishGuard
```

### **Serveur de Production**
Le dossier `dist/` peut être servi par:
- Nginx
- Apache
- Vercel
- Netlify
- AWS S3 + CloudFront

---

## 🧪 Tests

### **Structure de Tests** (à implémenter)
```
src/
├── components/
│   ├── Login.jsx
│   └── Login.test.jsx
```

### **Outils Recommandés**
- Jest - Framework de test
- React Testing Library - Tests composants
- Cypress - Tests E2E

---

## 📱 Responsive Design

### **Breakpoints**
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

### **Adaptations**
- Menu burger sur mobile
- Grilles adaptatives
- Sidebar collapsible
- Touch-friendly sur mobile

---

## ⚡ Performance

### **Optimisations**
- Code splitting (React.lazy)
- Lazy loading des images
- Memoization (useMemo, useCallback)
- Debouncing des recherches
- Pagination des listes
- Compression des assets

### **Métriques Cibles**
- First Contentful Paint: < 1.5s
- Time to Interactive: < 3s
- Lighthouse Score: > 90

---

## 🔄 Gestion d'État

### **État Local**
- useState pour état composant
- useReducer pour logique complexe

### **État Global**
- Context API (Auth, EmailProvider)
- Pas de Redux (simplicité)

### **État Serveur**
- Pas de cache côté client
- Fetch à la demande
- Refresh manuel

---

## 🌐 Internationalisation

### **Langue Actuelle**
- Français uniquement
- Textes hardcodés dans les composants

### **Extension Future**
- react-i18next pour multi-langue
- Fichiers de traduction JSON
- Détection langue navigateur

---

## 📝 Conventions de Code

### **Nommage**
- Composants: PascalCase (UserProfile.jsx)
- Fonctions: camelCase (fetchEmails)
- Constantes: UPPER_SNAKE_CASE (API_URL)
- CSS classes: kebab-case (user-profile)

### **Structure Fichier**
```javascript
// 1. Imports
import React from 'react';

// 2. Constantes
const API_URL = '...';

// 3. Composant
const MyComponent = () => {
  // Hooks
  // Fonctions
  // Render
};

// 4. Export
export default MyComponent;
```

---

## 🐛 Debugging

### **Outils**
- React DevTools (extension navigateur)
- Console.log stratégique
- Network tab (requêtes API)
- Redux DevTools (si Redux ajouté)

### **Erreurs Communes**
- Token expiré → Redirection login
- CORS errors → Vérifier backend
- 404 routes → Vérifier React Router
- State not updating → Vérifier immutabilité

---

## 📚 Ressources

### **Documentation**
- React: https://react.dev
- Vite: https://vitejs.dev
- Tailwind: https://tailwindcss.com
- React Router: https://reactrouter.com

### **Tutoriels**
- React Hooks
- Context API
- OAuth2 flow
- JWT authentication

---

## 🎓 Points Clés pour Votre Superviseur

### **Architecture Moderne**
- React 18 avec hooks (pas de classes)
- Vite pour build ultra-rapide
- Context API pour état global simple
- Composants fonctionnels réutilisables

### **Sécurité**
- JWT authentication
- OAuth2 pour email providers
- Protection des routes
- Validation des entrées
- 2FA disponible

### **UX/UI**
- Design moderne et épuré
- Responsive (mobile-first)
- Animations fluides
- Feedback utilisateur constant
- Accessibilité considérée

### **Performance**
- Code splitting
- Lazy loading
- Optimisation des re-renders
- Bundle size optimisé

### **Maintenabilité**
- Code organisé et modulaire
- Composants réutilisables
- Séparation des responsabilités
- Documentation inline
- Conventions de nommage claires

### **Fonctionnalités Principales**
1. Analyse d'URLs/emails en temps réel
2. Analyse en masse (bulk)
3. Intégration Gmail/Outlook
4. Dashboard avec statistiques
5. Gestion de profil complète
6. Panel administrateur
7. Système de notifications
8. Authentification 2FA
9. Gestion des sessions
10. Historique des analyses

---

## 🔮 Améliorations Futures

### **Court Terme**
- Tests unitaires et E2E
- Internationalisation (i18n)
- Mode sombre
- PWA (Progressive Web App)

### **Moyen Terme**
- Notifications push
- Export PDF des rapports
- Intégration plus de providers
- Chat support en direct

### **Long Terme**
- Application mobile (React Native)
- Extension navigateur
- API publique
- Marketplace de plugins

---

Cette documentation couvre l'ensemble du frontend PhishGuard. Chaque composant a un rôle précis et contribue à l'expérience utilisateur globale. L'architecture est scalable et maintenable pour les évolutions futures.
