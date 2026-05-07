# 🎯 Présentation du Projet PhishGuard

> Document à utiliser pour la **partie introductive** de la soutenance (les 3-5 premières minutes).
> Il pose le contexte, le problème, la solution et les objectifs.

---

## 1. Contexte

Le **phishing** (hameçonnage) est aujourd'hui la **première cause de cyberattaques** dans le monde et la principale porte d'entrée des fuites de données.

Quelques chiffres marquants (sources : APWG, Verizon DBIR, ANSSI) :
- **+90 %** des attaques cyber commencent par un email de phishing.
- **3,4 milliards** d'emails de phishing envoyés chaque jour dans le monde.
- **Coût moyen** d'une compromission par phishing pour une entreprise : **4,76 M$** (rapport IBM Cost of a Data Breach 2023).
- Les attaques ciblent autant les **particuliers** (Gmail, Outlook personnels) que les **entreprises** (BEC, fraude au président).

### Problèmes spécifiques identifiés

1. **Les filtres natifs (Gmail, Outlook) ne détectent pas tout** — les attaquants utilisent des techniques de plus en plus sophistiquées (typosquatting, homoglyphes, raccourcisseurs d'URL, certificats valides, etc.).
2. **L'utilisateur final manque de feedback** — quand un email passe le filtre, rien n'indique pourquoi il est suspect ou non.
3. **Les outils existants sont opaques** — peu d'explications sur *pourquoi* un email/URL est classé malveillant.
4. **L'analyse en masse est rare** — la plupart des outils analysent un email à la fois.

---

## 2. Problématique

> **Comment fournir à un utilisateur un outil simple, transparent et précis pour détecter les emails et les URLs de phishing, en s'intégrant directement à sa boîte mail ?**

Sous-questions techniques :
- Comment combiner machine learning et règles métier pour minimiser les faux positifs ?
- Comment expliquer une décision « phishing » à l'utilisateur (et pas juste un score noir) ?
- Comment se connecter de façon sécurisée à Gmail / Outlook (OAuth 2.0) ?
- Comment garantir que les tokens d'accès aux boîtes mail ne fuient pas ?

---

## 3. Objectifs du projet

### Objectifs fonctionnels

| # | Objectif |
|---|---|
| O1 | Permettre à un utilisateur d'analyser un **email** ou une **URL** copiée-collée en moins de 1 seconde. |
| O2 | Permettre la **connexion à Gmail et Outlook** via OAuth 2.0 et l'analyse directe des emails reçus. |
| O3 | Fournir une **analyse en masse** (jusqu'à 100 items en parallèle). |
| O4 | Donner une **explication claire** de la décision (mots-clés détectés, features de l'URL…). |
| O5 | Tenir un **historique d'analyses** et un **tableau de bord** par utilisateur. |
| O6 | Offrir un **panneau d'administration** pour gérer utilisateurs, audits, brute-force. |

### Objectifs techniques / non fonctionnels

| # | Objectif | Métrique cible |
|---|---|---|
| ON1 | Précision du modèle email | ≥ 95 % d'accuracy |
| ON2 | Précision du modèle URL | ≥ 90 % d'accuracy |
| ON3 | Temps de réponse de l'API d'analyse | < 500 ms (p95) |
| ON4 | Sécurité de l'authentification | JWT + bcrypt + 2FA TOTP optionnel |
| ON5 | Rate limiting | 100 req/min/IP |
| ON6 | Stockage sécurisé des tokens OAuth | Tokens chiffrés en base |

### Résultats obtenus

| Indicateur | Cible | Réalisé |
|---|---|---|
| Accuracy modèle email | ≥ 95 % | ✅ **97,5 %** |
| Accuracy modèle URL | ≥ 90 % | ✅ **94,6 %** |
| Endpoints REST | — | 70+ |
| Couverture fonctionnelle | 6 objectifs O1-O6 | **6/6** atteints |

---

## 4. La solution PhishGuard

PhishGuard est une **plateforme web full-stack** composée de :

```
┌───────────────────────┐         ┌───────────────────────┐
│   Frontend React 19   │  ◄────► │  Backend FastAPI      │
│   (Vite, Tailwind)    │  HTTPS  │  (Python 3.11, async) │
└───────────────────────┘  REST   └──────────┬────────────┘
                                              │
                              ┌───────────────┼─────────────────┐
                              ▼               ▼                 ▼
                      ┌──────────────┐ ┌──────────────┐ ┌────────────────┐
                      │ PostgreSQL   │ │ ML Models    │ │ APIs externes  │
                      │ (Supabase)   │ │ (.pkl)       │ │ Gmail, Outlook │
                      └──────────────┘ └──────────────┘ └────────────────┘
```

### Approche de détection : **hybride ML + règles**

PhishGuard ne se contente pas d'un seul modèle de machine learning. Pour minimiser les faux positifs (un faux positif sur Gmail = un utilisateur frustré), on combine :

1. **Whitelist** des grands domaines connus (google.com, microsoft.com, paypal.com…) → renvoie `safe` directement.
2. **IP privées / loopback** → renvoie `safe` directement (pas de phishing sur 192.168.x.x).
3. **Modèles ML** :
   - Pour le texte : `LinearSVC + TF-IDF` (97,5 % d'accuracy)
   - Pour les URLs : `Random Forest` sur 23 features (94,6 % d'accuracy)
4. **Règles métier** complémentaires (urgence, demande de credentials, typosquatting de marques…).
5. **Approche hybride** pour les emails : on extrait les URLs du corps de l'email et on les analyse séparément avec le modèle URL, puis on combine les résultats.

### Public cible

- **Particuliers** soucieux de leur sécurité numérique.
- **Petites entreprises / freelances** sans service IT dédié.
- **Étudiants / chercheurs** qui veulent un outil pédagogique pour comprendre le phishing.

---

## 5. Démarche / Méthodologie

### Méthodologie de développement
- **Approche itérative** par fonctionnalités (auth → analyse → providers email → admin → 2FA…).
- **Git** pour le versionning (branches feature + PR).
- Documentation continue dans `/préparation de soutenance technique/`.

### Démarche pour la partie ML
1. **Collecte des datasets** publics (datasets de phishing emails + datasets d'URLs).
2. **Exploration & nettoyage** des données.
3. **Feature engineering** :
   - Email : TF-IDF (1-2 grammes, normalisation, stopwords).
   - URL : 23 features structurelles (longueur, sous-domaines, entropie, TLD risqués, etc.).
4. **Sélection d'algorithmes** :
   - LinearSVC pour le texte (rapide, performant sur du sparse, peu de risque d'overfitting).
   - Random Forest pour les URLs (gestion native des features hétérogènes, interprétable, robuste).
5. **Entraînement & évaluation** sur train/test split.
6. **Sérialisation** en `.pkl` (joblib) et intégration dans le backend en lazy loading.
7. **Itération** avec ajout de règles métier pour corriger les faux positifs constatés en démo.

> 📚 Détail complet : [ML_DETECTION_DETAILLEE.md](ML_DETECTION_DETAILLEE.md)

---

## 6. Différenciation par rapport à l'existant

| Outil | Limite | PhishGuard |
|---|---|---|
| **Filtres Gmail / Outlook natifs** | Boîte noire, pas d'explications, ne couvre pas tout | Explication claire des features détectées |
| **VirusTotal** | Orienté URL/fichier, pas de connexion Gmail/Outlook directe | Intégration native OAuth 2.0 |
| **PhishTank** | Base statique de phishing connus | Analyse ML temps réel (détecte aussi le zero-day) |
| **Outils enterprise (Proofpoint, Mimecast)** | Coûteux, complexes, B2B | Gratuit, open-source, simple |

---

## 7. Limites connues (à assumer devant le jury)

- Le modèle email a été entraîné sur un dataset majoritairement **en anglais** → moins performant sur le français.
- Les **faux positifs** restent possibles sur des emails légitimes contenant beaucoup d'urgence (newsletters commerciales agressives).
- L'**OAuth Gmail** nécessite une vérification Google pour passer en production grand public.
- Le **stockage en mémoire du rate limiter** ne survit pas à un redémarrage (Redis recommandé en prod).
- Pas encore de **tests automatisés** unitaires/E2E (mentionné dans les améliorations futures).

---

## 8. Évolutions possibles

### Court terme (1-3 mois)
- Tests unitaires (pytest) + tests E2E (Playwright/Cypress)
- Internationalisation (i18n) FR/EN
- Mode sombre
- Ré-entraînement périodique des modèles avec nouvelles données

### Moyen terme (3-6 mois)
- Extension navigateur (Chrome/Firefox) pour analyse en un clic
- Notifications push
- Export PDF des rapports
- Support de Yahoo Mail, ProtonMail

### Long terme (6-12 mois)
- Application mobile (React Native)
- API publique pour développeurs
- Détection multi-langue (modèle multilingue type DistilBERT)
- Détection de fichiers joints (PDF, .exe…)
- Threat intelligence partagée entre utilisateurs

---

## 9. Conclusion (à dire à l'oral)

> *« PhishGuard répond à un besoin concret de sécurité numérique en combinant machine learning, règles métier et intégration directe aux boîtes mail. La solution atteint et dépasse les objectifs fixés (97,5 % d'accuracy sur les emails, 94,6 % sur les URLs), couvre l'ensemble du cycle utilisateur (de l'inscription à l'administration) et s'appuie sur une architecture moderne, scalable et sécurisée. Le projet est fonctionnel, documenté, et prêt à évoluer vers une mise en production. »*
