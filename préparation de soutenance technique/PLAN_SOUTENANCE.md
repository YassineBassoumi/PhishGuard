# 🎤 Plan de Soutenance — PhishGuard

> Déroulé minute par minute d'une soutenance de **20 minutes de présentation + 10-15 minutes de Q&A** (à adapter selon le format imposé par votre école).

---

## 🧭 Structure globale

| Phase | Durée | Objectif |
|---|---|---|
| **0. Introduction** | 1 min 30 | Se présenter, contexte |
| **1. Problématique** | 2 min | Le phishing, le besoin |
| **2. Solution proposée** | 2 min | Vision PhishGuard, fonctionnalités |
| **3. Architecture technique** | 4 min | Stack, schémas, choix |
| **4. Focus Machine Learning** | 4 min | Modèles, datasets, métriques |
| **5. Démo live** | 5 min | 7 étapes-clés (cf. DEMO_SCRIPT.md) |
| **6. Bilan & perspectives** | 1 min 30 | Bilan, améliorations futures |
| **7. Conclusion** | 1 min | Take-away |
| **8. Questions / Réponses** | 10-15 min | (cf. QUESTIONS_REPONSES.md) |

---

## ⏱️ Slide par slide (suggéré)

### Slide 1 — Page de garde (15 s)
- Logo PhishGuard
- Titre : *« PhishGuard : Détection de Phishing par Intelligence Artificielle »*
- Votre nom, école, encadrant, date
- *« Bonjour, je m'appelle [X], et je vais vous présenter PhishGuard, mon projet de fin d'études sur la détection de phishing par IA. »*

### Slide 2 — Sommaire (15 s)
- Lister les 7 sections de la présentation
- *« Voici comment je vais structurer cette présentation : contexte, problématique, solution, architecture, machine learning, démo, et perspectives. »*

---

### **PHASE 0 — Introduction (1 min)**

#### Slide 3 — Contexte personnel (30 s)
- Pourquoi ce sujet ? (intérêt pour la cybersécurité + IA)
- Durée du projet, encadrement

> *« J'ai choisi ce sujet pour l'intersection entre cybersécurité et machine learning, deux domaines en pleine expansion. »*

---

### **PHASE 1 — Problématique (2 min)**

#### Slide 4 — Le phishing en chiffres (1 min)
- 90 % des cyberattaques commencent par du phishing (Verizon DBIR 2023)
- 3,4 milliards d'emails de phishing/jour
- Coût moyen d'une compromission : 4,76 M$ (IBM 2023)
- Image marquante : capture d'écran d'un faux email PayPal

> *« Le phishing reste, en 2024, la principale porte d'entrée des cyberattaques. Les filtres natifs de Gmail ou Outlook ne sont pas suffisants : les attaquants évoluent, utilisent du typosquatting, des URLs raccourcies, des certificats valides... L'utilisateur final n'a aucun outil simple pour analyser un email ou une URL suspecte avant de cliquer. »*

#### Slide 5 — Problématique (1 min)
- **Question centrale** : *« Comment fournir un outil simple, transparent et précis pour détecter les emails et les URLs de phishing ? »*
- Sous-questions : minimiser les faux positifs ? expliquer la décision ? intégrer Gmail/Outlook ?

---

### **PHASE 2 — Solution proposée (2 min)**

#### Slide 6 — Vision PhishGuard (45 s)
- Plateforme web full-stack
- 3 axes : analyse manuelle / analyse en masse / intégration boîte mail
- Schéma haut niveau (cf. ARCHITECTURE_DIAGRAMS.md § 1)

#### Slide 7 — Fonctionnalités-clés (1 min 15 s)
7 fonctionnalités majeures en cards :
1. 🔍 Analyse instantanée d'emails et URLs
2. 📧 Connexion Gmail / Outlook (OAuth 2.0)
3. 📊 Tableau de bord + historique
4. 🔐 Authentification + 2FA TOTP + codes de secours
5. 👤 Gestion de profil, sessions et désactivation réversible
6. 👑 Panneau d'administration
7. 🔄 Désactivation/réactivation de compte (style Facebook)

> *« PhishGuard couvre l'ensemble du parcours utilisateur, de l'inscription au panel admin, en passant par la connexion à sa boîte Gmail. »*

---

### **PHASE 3 — Architecture technique (4 min)**

#### Slide 8 — Stack globale (1 min)
- Diagramme architecture globale (cf. ARCHITECTURE_DIAGRAMS.md § 1)
- Liste des techno : React 19 / FastAPI / PostgreSQL / scikit-learn / OAuth

> *« On a une architecture trois-tiers classique : un frontend React qui parle en REST à un backend FastAPI, qui interroge une base PostgreSQL et expose des modèles ML. »*

#### Slide 9 — Choix technologiques (1 min 30 s)
Tableau de justification :
| Choix | Pourquoi |
|---|---|
| **FastAPI** | Async natif, Swagger auto, performance proche de Go |
| **React 19 + Vite** | Standard moderne, build rapide, large écosystème |
| **PostgreSQL (Supabase)** | Relationnel, JSON natif, hosted gratuit |
| **scikit-learn** | Industrie standard, modèles classiques performants |
| **JWT + bcrypt** | Standard de sécurité éprouvé |

#### Slide 10 — Architecture en couches du backend (1 min)
- Diagramme en couches (cf. ARCHITECTURE_DIAGRAMS.md § 2)
- 5 couches : Routes → Middlewares → Services → Models → DB

#### Slide 11 — Modèle de données (30 s)
- Diagramme ER simplifié (cf. ARCHITECTURE_DIAGRAMS.md § 3)
- ~10 tables, relations principales
- Mentionner : cascade delete, index, constraint singleton

---

### **PHASE 4 — Focus Machine Learning (4 min)**

#### Slide 12 — Approche hybride (1 min)
Schéma : *Email → texte + URLs → 2 modèles distincts → combinaison*

> *« Au lieu d'un seul modèle, on combine un modèle de texte (LinearSVC) et un modèle d'URL (Random Forest), parce qu'un email avec un texte anodin peut cacher une URL très dangereuse. »*

#### Slide 13 — Modèle Email — LinearSVC + TF-IDF (1 min)
- Algorithme LinearSVC (SVM linéaire)
- Vectorisation TF-IDF (mots + bigrammes, max 5000 features)
- Dataset : ~19 741 emails
- **Accuracy : 97,5 %**
- Schéma : texte → TF-IDF → LinearSVC → décision

> *« Le modèle email est rapide (<5 ms d'inférence), interprétable via la distance à l'hyperplan, et atteint 97,5 % d'accuracy. »*

#### Slide 14 — Modèle URL — Random Forest 23 features (1 min 30 s)
- Algorithme Random Forest binaire
- 23 features structurelles (longueur, sous-domaines, entropie, TLD risqué…)
- Dataset : ~822 000 URLs
- **Accuracy : 94,6 %**
- Schéma : URL → 23 features → RandomForest → décision

Mentionner les **court-circuits** :
- IP privée → safe direct
- Whitelist (google.com, microsoft.com…) → safe direct

#### Slide 15 — Stratégie anti-faux-positifs (30 s)
4 mesures :
1. Whitelist domaines connus
2. IP privées safe
3. Approche hybride (texte safe + URL douteuse → suspicious, pas dangerous)
4. Fallback rule-based si modèle absent

> *« Les faux positifs sont l'ennemi numéro 1 : si on alerte sur des emails légitimes, l'utilisateur perd confiance. C'est pourquoi on a 4 garde-fous. »*

---

### **PHASE 5 — Démo live (5 min)**

#### Slide 16 — Démo (15 s)
- *« Je vais maintenant vous montrer PhishGuard en action en 5 minutes. »*
- Basculer sur la fenêtre du navigateur

⚠️ **Suivre exactement le DEMO_SCRIPT.md** :
1. Connexion (30 s)
2. Analyse URL phishing (1 min)
3. Analyse email phishing (1 min)
4. Analyse en masse (45 s)
5. Connexion Gmail OAuth (45 s)
6. Dashboard + historique (30 s)
7. Panneau admin (30 s)

> 💡 Avoir **TOUS les onglets ouverts** avant de basculer. Avoir le DEMO_SCRIPT en miroir sur 2e écran ou imprimé.

---

### **PHASE 6 — Bilan et perspectives (1 min 30 s)**

#### Slide 17 — Résultats obtenus (45 s)
Tableau objectifs / réalisé :
| Objectif | Cible | Réalisé |
|---|---|---|
| Accuracy modèle email | ≥ 95 % | **97,5 %** ✅ |
| Accuracy modèle URL | ≥ 90 % | **94,6 %** ✅ |
| Endpoints REST | — | 70+ ✅ |
| Couverture fonctionnelle | 6 | **6/6** ✅ |
| Authentification + sécurité | JWT+2FA | ✅ |

#### Slide 18 — Perspectives (45 s)
Roadmap court / moyen / long terme :
- **Court** : tests automatisés, CI/CD, mode sombre, i18n
- **Moyen** : extension navigateur, app mobile, ré-entraînement automatique
- **Long** : multilingue (DistilBERT), API publique, threat intelligence partagée

---

### **PHASE 7 — Conclusion (1 min)**

#### Slide 19 — Conclusion / Take-away (1 min)
- Récap en 3 points :
  1. **Solution complète** : ML + règles + intégration providers + admin
  2. **Performance prouvée** : 97,5 % et 94,6 % d'accuracy
  3. **Approche professionnelle** : architecture moderne, sécurité, documentation
- Phrase de fin : *« Merci de votre attention, je suis prêt à répondre à vos questions. »*

#### Slide 20 — Slide finale "Questions ?"
- Garder cette slide affichée pendant tout le Q&A
- Mentions à droite : URL du repo GitHub, votre nom

---

## 📊 Slide bonus (à garder en backup)

Slides à ne PAS montrer par défaut, mais à pouvoir afficher en réponse à une question :

| Slide backup | Pour répondre à |
|---|---|
| **Diagramme de séquence Login + 2FA** | "Comment fonctionne votre auth ?" |
| **Liste des 23 features URL** | "Quelles features pour le modèle URL ?" |
| **Pipeline ML détaillé** | "Comment se déroule une analyse ?" |
| **Comparaison vs VirusTotal/PhishTank** | "Différenciation ?" |
| **Architecture de déploiement prod** | "Comment scaler ?" |
| **Code snippet : `_sigmoid_confidence`** | "Comment sortir une probabilité ?" |
| **Dashboard admin (zoom)** | "Et le côté admin ?" |
| **Code de l'EmailPreprocessor** | "Comment gérez-vous les emails RFC822 ?" |

---

## 🎯 Tips spécifiques pour la présentation

### Avant
- [ ] Slides exportées en PDF + .pptx
- [ ] Slides copiées sur clé USB
- [ ] Slides accessibles depuis Google Drive / OneDrive
- [ ] Démo répétée 3 fois
- [ ] Vidéo de backup de la démo enregistrée
- [ ] Chrono lancé pendant les répétitions (objectif : 20 min ± 1 min)

### Pendant
- [ ] **Parler lentement** (stress = parle vite = on perd le jury)
- [ ] **Regarder le jury**, pas l'écran
- [ ] **Pointer du doigt** ce qu'on montre
- [ ] **Ne pas lire les slides** — les commenter, raconter
- [ ] **Garder un sourire** même quand un bug arrive
- [ ] **Respirer** entre les phrases (silence court = bon, silence long = stress)

### Après (Q&A)
- [ ] **Écouter la question entière** avant de répondre
- [ ] **Reformuler** si nécessaire (« Si je comprends bien, vous demandez… »)
- [ ] **Réponse concise** : 30-60 secondes max par question
- [ ] **Ne pas inventer** : si tu ne sais pas, dis-le et propose un raisonnement
- [ ] **Cf. QUESTIONS_REPONSES.md** pour les réponses préparées

---

## 🗣️ Phrases de transition entre slides

Pour fluidifier l'oral :
- *« Maintenant que nous avons vu X, passons à Y... »*
- *« Cela m'amène à... »*
- *« Concrètement, voici comment cela fonctionne dans PhishGuard... »*
- *« Pour répondre à cette question, j'ai mis en place... »*
- *« Le résultat de ce choix, c'est que... »*
- *« Avant de passer à la démo, un dernier point sur... »*
- *« Pour conclure cette première partie... »*

---

## ⏱️ Pense-bête de timing pendant la soutenance

À garder dans ton champ de vision pendant la présentation :

```
T+1:30  → Fin intro / contexte
T+3:30  → Fin problématique
T+5:30  → Fin solution
T+9:30  → Fin architecture technique
T+13:30 → Fin focus ML
T+18:30 → Fin démo
T+20:00 → Fin bilan / conclusion
T+20:30 → "Merci, je suis prêt aux questions"
```

Si tu prends du retard à un moment, **réduis la démo** (sauter Gmail OAuth ou panneau admin).
Ne **JAMAIS** réduire la conclusion (c'est ce que le jury retient en dernier).

---

## 🎬 Et après la soutenance ?

- Remercier le jury et l'encadrant
- Demander un feedback à chaud (si possible)
- Noter les questions auxquelles tu as eu du mal à répondre → utile pour la suite
- Profiter ! 🎉
