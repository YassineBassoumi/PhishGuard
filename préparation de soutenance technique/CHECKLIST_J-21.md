# 📅 Checklist J-21 — Préparation Soutenance PhishGuard

> Plan de préparation **sur 3 semaines** avant la soutenance technique.
> Coche au fur et à mesure ✅ — l'objectif est d'arriver le jour J **serein, préparé, et confiant**.

---

## 🗓️ Semaine 1 (J-21 → J-15) — **Maîtrise du projet**

### Objectif de la semaine
À la fin de la semaine, tu dois être capable de **réexpliquer ton projet** à quelqu'un d'extérieur sans regarder tes notes.

### J-21 (Jour 1) — Audit du projet
- [ ] Relire intégralement le **README** du projet
- [ ] Relire les 6 documents `BACKEND_PART*.md` et `DOCUMENTATION_*.md` du dossier de soutenance
- [ ] Lire `INDEX.md`, `PRESENTATION_PROJET.md`, `ARCHITECTURE_DIAGRAMS.md`, `ML_DETECTION_DETAILLEE.md`
- [ ] Faire la **liste des bugs/limitations** du projet pour les assumer devant le jury
- [ ] Noter tes **3 fiertés techniques** (les choses dont tu es le plus fier)

### J-20 — Re-prise en main du code (backend)
- [ ] Démarrer le backend en local : `python run.py`
- [ ] Tester chaque endpoint via Swagger : http://localhost:8000/docs
- [ ] Lire chaque fichier dans `backend/app/routes/` (au moins en survol)
- [ ] Lire chaque fichier dans `backend/app/services/` (au moins en survol)
- [ ] **Comprendre** le fichier `backend/app/services/detector.py`

### J-19 — Re-prise en main du code (frontend)
- [ ] Démarrer le frontend : `npm run dev`
- [ ] Naviguer dans toutes les pages
- [ ] Lire le fichier `frontend/src/App.jsx`
- [ ] Lire les contextes : `AuthContext.jsx`, `EmailProviderContext.jsx`
- [ ] Lire 5-10 composants principaux (Sidebar, MainContent, AdminPanel, AnalysisForm…)

### J-18 — Re-prise en main de la partie ML
- [ ] Lire `backend/app/services/detector.py`
- [ ] Lire `backend/app/services/detection/email_detector.py`
- [ ] Lire `backend/app/services/detection/url_detector.py`
- [ ] Lire `backend/app/services/detection/hybrid_email_detector.py`
- [ ] Lire `backend/app/services/detection/feature_extractors/url_features.py`
- [ ] **Connaître les 23 features URL** par cœur (ou au moins 15)
- [ ] **Mémoriser les chiffres-clés** : 97,5 %, 94,6 %, 19 741, 822 000, 23 features

### J-17 — Architecture & sécurité
- [ ] Dessiner le **diagramme d'architecture** sur papier sans regarder ARCHITECTURE_DIAGRAMS.md
- [ ] Comprendre le **flux d'authentification** (JWT + 2FA)
- [ ] Comprendre le **flux OAuth Gmail/Outlook**
- [ ] Lister **5 mesures de sécurité** présentes dans le projet

### J-16 — Connaissance des outils & dépendances
- [ ] Pourquoi FastAPI ? (savoir le justifier en 30 s)
- [ ] Pourquoi React 19 + Vite ? (savoir le justifier)
- [ ] Pourquoi PostgreSQL ? (savoir le justifier)
- [ ] Pourquoi LinearSVC ? (savoir le justifier)
- [ ] Pourquoi Random Forest ? (savoir le justifier)
- [ ] Connaître les versions principales (cf. `requirements.txt` et `package.json`)

### J-15 (Bilan semaine 1)
- [ ] **Test à blanc** : explique ton projet à un proche (parent, ami) en 5 minutes
- [ ] Note les questions qu'il/elle te pose → ajoute-les à `QUESTIONS_REPONSES.md`
- [ ] Repos !

---

## 🗓️ Semaine 2 (J-14 → J-8) — **Présentation & démo**

### Objectif de la semaine
À la fin de la semaine, tes **slides sont finalisées** et tu as **répété la démo** au moins 3 fois.

### J-14 — Création des slides (1/2)
- [ ] Choisir un template de slides (Google Slides, Keynote, PowerPoint, Reveal.js…)
- [ ] Créer les **slides 1 à 10** (intro, problématique, solution, architecture)
- [ ] Pour chaque slide, écrire les **notes de présentation** (cf. PLAN_SOUTENANCE.md)

### J-13 — Création des slides (2/2)
- [ ] Créer les **slides 11 à 20** (focus ML, démo, perspectives, conclusion)
- [ ] Créer les **slides backup** (cf. PLAN_SOUTENANCE.md "Slides bonus")
- [ ] Vérifier la cohérence visuelle (police, couleurs, alignements)

### J-12 — Préparation environnement de démo
- [ ] Créer le compte de démo : `demo@phishguard.com` / mot de passe stable
- [ ] Activer la 2FA sur le compte de démo (sauvegarder le secret + backup codes)
- [ ] Créer le compte admin pour la démo
- [ ] Faire **5-10 analyses préalables** dans l'historique pour qu'il y ait du contenu
- [ ] Connecter Gmail au compte de démo (OAuth)
- [ ] Préparer le fichier `.txt` avec **3 emails phishing + 3 emails safe + 3 URLs phishing + 3 URLs safe**

### J-11 — Première répétition à blanc
- [ ] Suivre le DEMO_SCRIPT.md de bout en bout
- [ ] **Chronométrer** chaque étape
- [ ] Noter les bugs, lenteurs, transitions ratées
- [ ] Corriger les problèmes identifiés
- [ ] Refaire le tour si bugs critiques

### J-10 — Deuxième répétition + enregistrement
- [ ] Refaire la démo complète
- [ ] **Enregistrer la démo réussie** (Loom, OBS, QuickTime…) → backup vidéo pour le jour J
- [ ] Mettre la vidéo sur clé USB **et** Google Drive (deux backups)

### J-9 — Répétition orale
- [ ] Présenter la soutenance complète à voix haute (slides + démo)
- [ ] **Chronométrer la présentation entière** : objectif 20 min ± 1 min
- [ ] Si trop long : couper du contenu (jamais plus que la conclusion)
- [ ] Si trop court : préparer 1-2 backup slides

### J-8 (Bilan semaine 2)
- [ ] Repos
- [ ] Si possible, présenter à un ami / un enseignant pour avoir un feedback

---

## 🗓️ Semaine 3 (J-7 → J-1) — **Polissage & Q&A**

### Objectif de la semaine
À la fin de la semaine, tu as **mémorisé les réponses aux 20 questions probables** et tu es prêt mentalement.

### J-7 — Q&A (1/3)
- [ ] Lire intégralement `QUESTIONS_REPONSES.md`
- [ ] Choisir les **10 questions les plus probables** dans ton contexte
- [ ] Mémoriser les réponses (1ère répétition)

### J-6 — Q&A (2/3)
- [ ] Refaire les 10 questions à voix haute, sans notes
- [ ] Ajouter 5 questions plus pointues (ML, scaling, sécurité)
- [ ] Demander à un proche de te poser des questions au hasard

### J-5 — Mise en condition réelle
- [ ] **Soutenance complète à blanc** : slides + démo + Q&A
- [ ] Si possible, devant un public (camarade, prof)
- [ ] Filmer la prestation pour t'auto-évaluer
- [ ] Identifier les tics de langage, hésitations, transitions floues

### J-4 — Corrections finales
- [ ] Corriger les défauts identifiés J-5
- [ ] Affiner les slides (typos, alignements)
- [ ] Préparer une **version PDF** des slides (au cas où)
- [ ] Préparer une **version PowerPoint** (au cas où)

### J-3 — Préparation logistique
- [ ] Vérifier la salle de soutenance (vidéoprojecteur, prises, wifi)
- [ ] Tester les **adaptateurs** (HDMI, USB-C, VGA…) sur ta machine
- [ ] Préparer une **tenue** (chemise / blazer)
- [ ] Préparer le **support papier** : plan de présentation + pense-bête timing

### J-2 — Dernière répétition
- [ ] Soutenance complète à blanc une dernière fois
- [ ] **Couper court** dès que ça roule (ne pas s'épuiser)
- [ ] Préparer le sac : laptop, chargeur, adaptateur, clé USB, eau

### J-1 — Repos
- [ ] **PAS de répétition** (on ne fait que stresser)
- [ ] Relire **uniquement** : INDEX.md, PRESENTATION_PROJET.md, et top 10 Q&A
- [ ] Coucher tôt
- [ ] Hydratation, alimentation correcte

### J-0 — Le jour J
- [ ] Petit-déjeuner correct
- [ ] Arriver **30 min en avance** sur place
- [ ] Tester le matériel **avant** le jury
- [ ] Boire un verre d'eau juste avant
- [ ] **Respirer profondément** 30 secondes avant de commencer
- [ ] **Tout va bien se passer** 💪

---

## ✅ Checklists transverses

### Checklist "Code & déploiement"
- [ ] Tous les bugs critiques corrigés
- [ ] Le backend démarre sans erreur
- [ ] Le frontend démarre sans erreur
- [ ] Les modèles ML se chargent sans erreur
- [ ] La base de données est accessible
- [ ] Les comptes de démo existent et fonctionnent
- [ ] Le 2FA est testé sur le compte demo
- [ ] Au moins 5 analyses dans l'historique
- [ ] Gmail connecté en OAuth (avec emails de test)

### Checklist "Documentation"
- [x] INDEX.md créé
- [x] PRESENTATION_PROJET.md créé
- [x] ARCHITECTURE_DIAGRAMS.md créé
- [x] ML_DETECTION_DETAILLEE.md créé
- [x] DEMO_SCRIPT.md créé
- [x] QUESTIONS_REPONSES.md créé
- [x] PLAN_SOUTENANCE.md créé
- [x] CHECKLIST_J-21.md créé
- [x] Inexactitudes ML corrigées dans BACKEND_PART4 et BACKEND_PART5
- [ ] README à jour avec les bonnes infos (à vérifier)

### Checklist "Slides"
- [ ] 20 slides minimum créées
- [ ] Slides backup préparées
- [ ] Notes de présentation rédigées sur chaque slide
- [ ] Slides exportées en PDF
- [ ] Slides exportées en PowerPoint
- [ ] Slides sur clé USB
- [ ] Slides sur Google Drive

### Checklist "Démo"
- [ ] Démo répétée 3 fois minimum
- [ ] Démo chronométrée < 5 min
- [ ] Vidéo backup de la démo enregistrée
- [ ] Plan B identifié pour chaque étape
- [ ] Tous les contenus de démo dans un fichier `.txt` accessible
- [ ] Tous les onglets nécessaires identifiés

### Checklist "Q&A"
- [ ] Top 10 questions mémorisées
- [ ] 5 questions techniques pointues préparées
- [ ] 3 questions pièges anticipées (limites, contribution, evolutions)
- [ ] Réponses concises (30-60s) répétées à voix haute

### Checklist "Logistique jour J"
- [ ] Laptop chargé à 100 %
- [ ] Chargeur dans le sac
- [ ] Adaptateur HDMI / USB-C
- [ ] Clé USB avec slides + vidéo backup
- [ ] Slides accessibles en cloud (Drive/OneDrive)
- [ ] Tenue prête
- [ ] Bouteille d'eau
- [ ] Connexion 4G de secours sur le téléphone (partage)
- [ ] Plan de présentation imprimé en pense-bête

---

## 🎯 Indicateurs de "prêt à soutenir"

À J-1, tu dois pouvoir cocher chacun de ces points **honnêtement** :

- [ ] Je peux expliquer le projet en 1 minute
- [ ] Je peux expliquer le projet en 5 minutes
- [ ] Je peux ouvrir n'importe quel fichier du repo et expliquer son rôle
- [ ] Je connais les chiffres clés par cœur (97,5 %, 94,6 %, 19 741, 822 000, 23 features)
- [ ] Je sais justifier chaque choix technique (FastAPI, React, PostgreSQL, LinearSVC, RF)
- [ ] Je sais expliquer les limites du projet sans m'effondrer
- [ ] J'ai un plan B pour chaque étape de la démo
- [ ] J'ai une vidéo backup de la démo
- [ ] J'ai relu le top 10 Q&A
- [ ] **Je suis confiant** 💪

---

## 💡 Astuces psychologiques

- **Le stress est normal** → respiration profonde, eau, sourire (même forcé, ça marche).
- **Le jury n'est pas ton ennemi** → ils veulent que ça se passe bien, ils sont juste là pour évaluer.
- **Si tu bug** → reprends ton souffle, dis "pardonnez-moi, je reformule", continue.
- **Si tu ne sais pas** → "Je n'ai pas la réponse exacte, mais voici comment j'aborderais le problème : [raisonnement]". C'est mille fois mieux qu'inventer.
- **Garde le sourire** même quand un bug arrive en démo. Le jury va surtout regarder **comment tu réagis** au bug.

---

## 🔥 Mantra du jour J

> *« J'ai bossé 6 mois sur ce projet. Le jury va me poser des questions sur mon travail. Personne au monde ne connaît mon projet aussi bien que moi. Je vais leur montrer ce que j'ai fait. »*

Bonne chance ! 🚀
