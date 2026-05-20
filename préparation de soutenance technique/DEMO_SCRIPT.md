# 🎬 Script de Démo — Soutenance PhishGuard

> **Objectif** : enchaîner une démo de **5-7 minutes** qui montre les fonctionnalités clés sans bug, avec un plan B en cas de problème.
> **Règle d'or** : ne JAMAIS improviser une démo non répétée. Tout ce qui est ici doit être testé **au moins 3 fois** avant le jour J.

---

## 🛠️ Préparation pré-démo (la veille au soir)

### Checklist matériel
- [ ] Laptop branché secteur (pas sur batterie)
- [ ] Adaptateur HDMI / USB-C selon la salle
- [ ] Connexion Internet stable testée (utiliser le partage 4G du téléphone en backup)
- [ ] Backup vidéo de la démo enregistré (Loom / OBS) au cas où le live plante
- [ ] Slides PDF copiées sur clé USB

### Checklist environnement technique
- [ ] Backend démarré : `python run.py` → http://localhost:8000/docs accessible
- [ ] Frontend démarré : `npm run dev` → http://localhost:5173 accessible
- [ ] Base de données accessible (Supabase ou local PostgreSQL ping OK)
- [ ] Compte de démo créé : `demo@phishguard.com` / `Demo1234!`
- [ ] Compte admin créé et email vérifié
- [ ] 2FA configuré sur le compte demo (avec backup codes notés)
- [ ] Au moins **5 analyses** déjà dans l'historique (pour que le dashboard ait du contenu)
- [ ] Compte Gmail connecté en OAuth (avec quelques emails de test)
- [ ] Rate limiter reset (sinon la démo peut bloquer)
- [ ] **Tous les onglets fermés sauf** ceux nécessaires à la démo

### Checklist du contenu de démo
- [ ] **2 emails de phishing** copiés dans un fichier `.txt` accessible (cmd+C facile)
- [ ] **2 emails légitimes** copiés (newsletter, confirmation Amazon)
- [ ] **3 URLs phishing** notées (ex: `http://paypa1-verify.tk/login`, `http://192.168.10.55/admin`, `http://amaz0n-account.xyz`)
- [ ] **3 URLs safe** notées (ex: `https://google.com`, `https://github.com/torvalds/linux`)
- [ ] Fichier CSV pour la démo bulk préparé (~10 lignes)

---

## 🎯 Plan de la démo (7 minutes)

| # | Étape | Durée | Objectif |
|---|---|---|---|
| 1 | Page d'accueil + connexion | 30 s | Montrer l'UI, le branding |
| 2 | Analyse manuelle d'une URL | 1 min | Démontrer la détection ML rapide |
| 3 | Analyse d'un email phishing | 1 min | Montrer l'approche hybride + features expliquées |
| 4 | Analyse en masse | 1 min | Démontrer la scalabilité |
| 5 | Connexion Gmail OAuth | 1 min | Montrer l'intégration provider |
| 6 | Dashboard + historique | 30 s | Montrer la persistance et les stats |
| 7 | 2FA + backup codes + sessions | 30 s | Montrer la sécurité |
| 8 | Désactivation/Réactivation | 45 s | Montrer la gestion réversible du compte |
| 9 | Panneau admin (rapide) | 1 min | Montrer la dimension multi-rôle |

---

## 📝 Script détaillé

### Étape 0 — Avant de cliquer sur "Connexion" (30 s)

> **À dire** : *« Voici PhishGuard, l'application web que nous avons développée. La page d'accueil présente le service, ses fonctionnalités principales, et l'intégration avec les fournisseurs email. Je vais me connecter avec un compte de démo. »*

**Actions** :
1. Ouvrir http://localhost:5173
2. Scroller rapidement la home (montrer Hero → Features → How it works)
3. Cliquer **Connexion**

---

### Étape 1 — Connexion (30 s)

> **À dire** : *« L'authentification est sécurisée avec JWT et bcrypt côté backend, avec rate limiting de 5 tentatives par minute pour bloquer le brute force. »*

**Actions** :
1. Saisir `demo@phishguard.com` / `Demo1234!`
2. Si 2FA → saisir le code TOTP depuis l'app authenticator
3. Arrivée sur le dashboard

---

### Étape 2 — Analyse manuelle d'une URL (1 min)

> **À dire** : *« Premier cas d'usage : analyser une URL suspecte. Je colle ici une URL qui ressemble à du phishing PayPal. »*

**Actions** :
1. Onglet **Analyser** → choix **URL**
2. Coller : `http://paypa1-verify-account.tk/login.php?secure=1&token=abc123`
3. Cliquer **Analyser**
4. Attendre la réponse (~500 ms)
5. **Pointer du doigt** :
   - Le badge rouge **DANGEREUX** + score de confiance
   - La liste des features détectées : "TLD risqué (.tk)", "Typosquatting paypa1", "Mots-clés suspects (verify, account, secure, login)", "URL longue avec paramètres"
   - Les recommandations affichées

> **À dire** : *« Vous voyez que le modèle Random Forest, qui utilise 23 features extraites de l'URL, a détecté plusieurs indicateurs : le TLD .tk qui est risqué, le typosquatting "paypa1" au lieu de "paypal", et la présence de mots-clés sensibles. La confiance est de 9X %. »*

**Démo bonus** : analyser ensuite `https://github.com` → **SÛR** à 98 % (whitelist de domaine). Mentionner :

> *« Pour éviter les faux positifs sur les grands sites, on a une whitelist qui court-circuite le ML. »*

---

### Étape 3 — Analyse d'un email phishing (1 min)

> **À dire** : *« Maintenant un email entier. PhishGuard utilise une approche hybride : il analyse le texte avec un modèle LinearSVC entraîné sur 19 741 emails, puis chaque URL séparément. »*

**Actions** :
1. Onglet **Analyser** → choix **Email**
2. Coller un faux email (préparé à l'avance, type "Your PayPal account has been suspended..." avec une URL piégée)
3. Cliquer **Analyser**
4. Pointer :
   - Threat level **DANGEREUX**
   - Features détectées (urgence, demande de credentials, URL suspecte)
   - **Decision trace** : ce que le ML a prédit + ce que les règles ont ajouté
   - Liste des URLs analysées séparément

> **À dire** : *« Le decision trace est important pour l'explicabilité : le jury peut voir que le modèle ML a bien classé l'email, et que la règle métier a confirmé. »*

---

### Étape 4 — Analyse en masse (1 min)

> **À dire** : *« Pour les utilisateurs avancés, on peut analyser jusqu'à 100 URLs ou emails en parallèle. »*

**Actions** :
1. Onglet **Analyse en masse**
2. Coller 10 URLs (mélange phishing + safe préparé à l'avance)
3. Cliquer **Lancer**
4. Montrer la barre de progression
5. Tableau de résultats avec tri par niveau de menace

---

### Étape 5 — Connexion Gmail OAuth (1 min)

> ⚠️ **Si la démo OAuth Gmail est risquée** (validation Google, popups bloqués…) → SAUTER cette étape et passer directement à l'étape 6 où on montre les emails déjà chargés (s'ils l'ont été avant).

> **À dire** : *« On peut se connecter directement à Gmail via OAuth 2.0. Aucune mot de passe n'est jamais transmis à PhishGuard, seulement un token d'accès chiffré stocké en base. »*

**Actions** :
1. Onglet **Email** → **Connecter Gmail**
2. Popup OAuth Google → autoriser
3. Retour sur l'app → emails affichés
4. Sélectionner 2-3 emails → **Analyser la sélection**

---

### Étape 6 — Dashboard et historique (30 s)

> **À dire** : *« Le tableau de bord affiche les statistiques personnelles : total d'analyses, distribution des menaces, tendances. Tout est sauvegardé en base avec un historique consultable. »*

**Actions** :
1. Onglet **Tableau de bord**
2. Pointer :
   - Cards : Total analyses, Menaces détectées, % sécurité
   - Graphique camembert : distribution safe/suspicious/dangerous
   - Graphique ligne : analyses par jour
3. Onglet **Historique** : montrer la liste des analyses passées

---

### Étape 7 — 2FA, backup codes et sessions (30 s)

> **À dire** : *« Côté sécurité utilisateur : 2FA TOTP optionnel compatible Google Authenticator, avec 8 codes de secours au format XXXX-XXXX utilisables en cas de perte du téléphone. Et gestion des sessions actives avec géolocalisation IP. »*

**Actions** :
1. Onglet **Paramètres**
2. Section **2FA** : montrer que c'est activé + nombre de codes de secours restants
3. Mentionner : *« Chaque code de secours est à usage unique, et on peut les régénérer si besoin »*
4. Section **Sessions actives** : montrer les sessions avec device, IP, localisation, dernière activité
5. Démontrer **Révoquer toutes les sessions sauf l'actuelle** (sans cliquer si on ne veut pas se déconnecter)

---

### Étape 8 — Désactivation / Réactivation de compte (45 s) *(optionnel)*

> **À dire** : *« Le compte peut être désactivé de manière réversible. Si l'utilisateur se reconnecte, une modal lui propose de réactiver son compte immédiatement. »*

**Actions** :
1. Onglet **Paramètres** → onglet **Désactivation**
2. Montrer l'UI ambre/orange et les avertissements
3. *(Si on veut démontrer live)* : saisir le mot de passe → confirmer → déconnecté
4. Se reconnecter → modal de réactivation s'affiche → confirmer → retour au dashboard
5. Mentionner : *« Aucune donnée n'est supprimée, c'est un choix professionnel pour éviter les pertes accidentelles »*

> ⚠️ **Si le temps est court** : montrer seulement l'UI de désactivation sans exécuter, et passer au panel admin.

---

### Étape 9 — Panneau admin (1 min)

> **À dire** : *« Enfin, le projet inclut un panneau d'administration accessible aux superadmins. »*

**Actions** :
1. Se déconnecter
2. Se connecter avec un compte admin (`admin@phishguard.com` / mot de passe admin)
3. Onglet **Admin Panel**
4. Pointer :
   - **Gestion utilisateurs** : liste, recherche, filtres, bouton bannir/débannir
   - **Audit logs** : toutes les actions critiques tracées
   - **Stats globales** : nombre total d'utilisateurs, analyses, menaces
   - **Rate limits** : monitoring des IP qui spamment
   - **Brute force** : IP bloquées automatiquement

---

## 🚨 Plans B (si quelque chose plante)

| Problème | Plan B |
|---|---|
| Backend down | `python run.py` dans un autre terminal pré-ouvert |
| Frontend down | `npm run dev` dans un autre terminal pré-ouvert |
| Connexion DB échoue | Mentionner la connexion Supabase et basculer sur la **vidéo backup** |
| OAuth Gmail bloqué | Sauter l'étape 5 et dire « cette feature fonctionne, voici une vidéo enregistrée » |
| Modèle ML non chargé | Mentionner le **fallback rule-based** : « le modèle n'est pas chargé mais l'app continue à fonctionner avec les règles, c'est exactement ce qu'on a prévu » |
| Bug imprévu | **Garder son calme**, dire « voici un comportement inattendu que je n'avais pas vu, voilà comment je le corrigerais en prod » → montre la maturité |
| Tout est cassé | Sortir la **vidéo enregistrée la veille** : *« Je préfère vous montrer l'enregistrement plutôt que de gâcher du temps sur un debug live »* |

---

## 🎤 Phrases-clés à placer pendant la démo

- *« On utilise une **approche hybride** : ML + règles métier. Le ML donne le score, les règles évitent les faux positifs. »*
- *« Le modèle email est un **LinearSVC à 97,5 % d'accuracy**, entraîné sur 19 741 emails. »*
- *« Le modèle URL est un **Random Forest à 94,6 % d'accuracy** sur 23 features et 822 000 URLs. »*
- *« Tous les tokens OAuth sont **stockés chiffrés** en base, jamais en clair. »*
- *« Le **rate limiting** protège l'API : 100 requêtes par minute par IP. »*
- *« Chaque action sensible est **tracée dans les audit logs** pour la traçabilité. »*
- *« On a une approche **fallback** : si le modèle ML ne se charge pas, l'app continue avec les règles seules. »*

---

## ⏱️ Timing rapide (à coller en pense-bête)

```
00:00 → page d'accueil + connexion
00:30 → analyse URL phishing
01:30 → analyse email phishing
02:30 → analyse en masse
03:30 → connexion Gmail OAuth
04:30 → dashboard + historique
05:00 → 2FA + sessions
05:30 → panneau admin
06:30 → conclusion (transition vers Q&A)
```

---

## 🎬 Plus important que tout

1. **Répéter au moins 3 fois** la démo complète avant le jour J (chrono en main).
2. **Filmer la démo réussie** la veille → backup en cas de plantage.
3. **Avoir TOUS les onglets et fichiers nécessaires déjà ouverts** avant de commencer.
4. **Parler à voix haute** pendant les actions, ne jamais laisser un silence > 3 s.
5. **Si bug** → garder le sourire, expliquer ce qui aurait dû se passer, montrer le code derrière si pertinent.
