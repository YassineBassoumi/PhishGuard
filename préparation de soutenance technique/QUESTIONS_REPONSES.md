# ❓ Questions / Réponses — Soutenance PhishGuard

> Recueil des questions les plus probables d'un jury de soutenance technique, avec des **éléments de réponse préparés**.
> Chaque question est classée par thème et niveau de difficulté.
> 🟢 Facile · 🟡 Moyen · 🔴 Difficile (questions pièges)

---

## 1. Questions sur le projet & son contexte

### 🟢 Q1.1 — Pourquoi avoir choisi ce sujet ?
**R** : *Le phishing est la première cause de cyberattaques (>90 % d'après le rapport Verizon DBIR), il touche autant les entreprises que les particuliers. Les outils existants sont soit trop opaques (filtres natifs Gmail), soit trop chers (solutions enterprise). Je voulais construire un outil pédagogique, transparent, qui explique ses décisions à l'utilisateur, et qui démontre l'application concrète de techniques ML.*

### 🟢 Q1.2 — À qui s'adresse PhishGuard ?
**R** : *Trois publics : (1) les particuliers soucieux de leur sécurité, (2) les TPE/freelances sans service IT, (3) les étudiants/curieux qui veulent comprendre comment fonctionne la détection de phishing.*

### 🟡 Q1.3 — Combien de temps avez-vous passé sur le projet ? Quelle organisation ?
**R** (à adapter à votre vraie réalité) : *X mois en travail régulier. Méthodologie itérative : développement par features (auth → analyse simple → providers email → admin → 2FA…). Versioning Git avec branches feature et PR. Documentation continue en parallèle (le dossier `préparation de soutenance technique` en est la preuve).*

### 🔴 Q1.4 — Quelle est la valeur ajoutée par rapport à VirusTotal ou PhishTank ?
**R** : *VirusTotal et PhishTank sont des **bases de données** : ils détectent ce qui est déjà connu. PhishGuard fait de la **détection ML temps réel**, ce qui permet de catch des phishing inconnus (zero-day) basés sur les caractéristiques structurelles. De plus, on s'intègre directement à Gmail/Outlook via OAuth, ce qu'aucun de ces deux outils ne fait. Enfin, on est **transparent** : on liste les features qui ont mené à la décision, alors que VirusTotal renvoie juste un agrégat de scores.*

---

## 2. Questions sur l'architecture

### 🟢 Q2.1 — Pourquoi FastAPI plutôt que Flask ou Django ?
**R** : *FastAPI offre :*
- *Asynchrone natif (`async def`) → parfait pour les I/O (DB, APIs externes)*
- *Validation automatique via Pydantic*
- *Documentation Swagger générée automatiquement*
- *Performance proche de Node.js / Go (basé sur Starlette + Uvicorn)*
- *Type hints Python natifs*

*Flask aurait nécessité d'ajouter manuellement Marshmallow + APISpec + Quart pour avoir l'équivalent. Django aurait été surdimensionné pour une API REST simple.*

### 🟢 Q2.2 — Pourquoi React 19 + Vite ?
**R** : *React est leader du marché, large écosystème, hooks modernes. Vite est ultra-rapide en dev (HMR < 50 ms) et produit un build optimisé. Vite remplace progressivement Create-React-App (qui n'est plus maintenu).*

### 🟡 Q2.3 — Pourquoi PostgreSQL plutôt que MySQL ou MongoDB ?
**R** : *PostgreSQL pour :*
- *Support natif du JSON (on stocke les `features` et `recommendations` en JSON)*
- *Index partiels (utilisé pour le singleton de Statistics)*
- *Foreign keys avec `ON DELETE CASCADE` natif*
- *SSL natif (important pour Supabase)*
- *Transactions ACID*

*MongoDB aurait été inadapté : on a beaucoup de relations (User → Sessions, Notifications, AuditLogs…), c'est un cas d'usage relationnel. MySQL aurait fonctionné mais Postgres a un meilleur support JSON et des features plus avancées.*

### 🟡 Q2.4 — Pourquoi avoir séparé le projet en `backend/` et `frontend/` ?
**R** : *Séparation des responsabilités, possibilité de déployer indépendamment (frontend sur Vercel/Netlify, backend sur un VPS), équipes potentiellement différentes, technologies différentes (Python vs JavaScript). Permet aussi d'avoir d'autres clients à terme (mobile, extension navigateur) sans toucher au backend.*

### 🔴 Q2.5 — Si vous deviez scaler PhishGuard à 10 000 utilisateurs / jour, qu'est-ce qui devrait changer ?
**R** :
1. *Remplacer le **rate limiter en mémoire par Redis** (sinon il ne marche pas en multi-instance)*
2. *Mettre l'API derrière un **load balancer + plusieurs instances** (gunicorn workers ou plusieurs containers)*
3. *Ajouter un **cache Redis** pour les analyses récentes (même URL/email analysés plusieurs fois)*
4. *Externaliser les uploads de photos sur **S3 + CDN**, pas en local*
5. *Déléguer l'envoi d'emails à un **service comme SendGrid** (au lieu de SMTP direct)*
6. *Ajouter **monitoring** : Prometheus + Grafana + Sentry pour le tracking d'erreurs*
7. *Migrer la base sur une **instance Postgres dédiée** avec read replicas si besoin*

---

## 3. Questions sur l'authentification & la sécurité

### 🟢 Q3.1 — Comment fonctionne l'authentification ?
**R** : *Authentification par JWT signé HS256 avec une clé secrète stockée dans `.env`. Token valable 30 minutes. Le password est hashé avec bcrypt (avec salt automatique) avant d'être stocké en base. À chaque requête, le middleware FastAPI vérifie le token, le décode, charge l'utilisateur en base et l'injecte dans la route.*

### 🟢 Q3.2 — Comment fonctionne la 2FA ?
**R** : *On utilise TOTP (Time-based One-Time Password, RFC 6238). Quand l'utilisateur active 2FA, on génère un secret base32 aléatoire, on construit l'URL `otpauth://totp/...` qui est encodée en QR code. L'utilisateur scanne avec Google Authenticator / Authy. Ensuite, à chaque login, on vérifie le code 6 chiffres avec une fenêtre de tolérance de ±1 période (30 s) avec la lib `pyotp`. On génère aussi 10 codes de secours en cas de perte du téléphone.*

### 🟡 Q3.3 — Comment stockez-vous les tokens OAuth Gmail/Outlook ?
**R** : *Les `access_token` et `refresh_token` sont stockés en base dans la table `user_email_credentials`. Pour la production, ils devraient être chiffrés au repos (idéalement avec une clé KMS / AWS Secrets Manager / HashiCorp Vault). Aujourd'hui ils sont stockés en clair en base — c'est une amélioration prévue. La connexion à la base utilise SSL (Supabase l'impose).*

### 🟡 Q3.4 — Comment gérez-vous les attaques par brute force ?
**R** : *Trois mécanismes :*
1. *Rate limiting global (100 req/min/IP) via le middleware `rate_limiter.py`*
2. *Rate limiting spécifique au login (5 tentatives / 15 minutes)*
3. *Détection brute force dans `audit_service` : si X tentatives échouées sur le même compte/IP, blocage temporaire et notification email à l'utilisateur*

### 🔴 Q3.5 — Que se passe-t-il si un attaquant vole un JWT ?
**R** : *C'est le risque inhérent au JWT stateless. Mitigations en place :*
- *Expiration courte (30 min)*
- *Stockage du `jti` (JWT ID) dans la table `user_sessions` → on peut **révoquer** une session précise (l'API vérifie en DB que la session est toujours active)*
- *L'utilisateur peut révoquer toutes ses sessions depuis le panel*
- *Détection d'anomalie : si la même session est utilisée depuis 2 IPs très différentes en peu de temps → notification de sécurité*

*Pour aller plus loin : on pourrait passer à des **refresh tokens** plus longs + access tokens très courts (~5 min).*

### 🔴 Q3.6 — Comment vous protégez-vous contre les injections SQL ?
**R** : *On n'écrit jamais de SQL brut. On utilise SQLAlchemy ORM avec des requêtes paramétrées : tout ce qui vient de l'utilisateur passe par `where()`, `filter()`, etc. qui paramètrent automatiquement. Pour les rares cas de SQL brut (ex : index partiel sur Statistics), on utilise `text()` SQLAlchemy avec des paramètres bind. **Aucune concaténation de strings utilisateur dans une requête SQL nulle part dans le projet.***

---

## 4. Questions sur le Machine Learning

### 🟢 Q4.1 — Quels algorithmes utilisez-vous ?
**R** :
- *Pour les emails : **LinearSVC** (SVM linéaire) avec vectorisation **TF-IDF**, accuracy **97,5 %** sur 19 741 emails.*
- *Pour les URLs : **Random Forest** (classification binaire) sur **23 features** structurelles, accuracy **94,6 %** sur 822 000 URLs.*
- *Une couche **hybride** combine les deux pour les emails contenant des URLs.*

### 🟢 Q4.2 — Pourquoi LinearSVC plutôt qu'un Logistic Regression ou Naive Bayes ?
**R** : *LinearSVC est plus performant que Logistic Regression sur des données sparse haute dimension (TF-IDF produit ~5000 features dont la plupart sont à 0). Naive Bayes fait l'hypothèse d'indépendance des features, qui est trop simpliste pour du texte. SVM trouve l'hyperplan qui maximise la marge entre les classes, ce qui généralise mieux. En pratique, sur ce dataset, LinearSVC donne ~3 % de mieux que Logistic Regression.*

### 🟡 Q4.3 — Comment générez-vous un score de confiance avec LinearSVC ?
**R** : *LinearSVC ne donne pas nativement de probabilités. On utilise `decision_function()` qui renvoie la **distance signée à l'hyperplan**. Plus c'est loin, plus on est sûr. On convertit cette distance en probabilité via une **sigmoïde** (calibration informelle de Platt simplifiée), puis on prend `max(p, 1-p) * 100` pour obtenir la confiance dans la classe prédite.*

```python
prob = 1.0 / (1.0 + math.exp(-decision_value))
confidence = max(prob, 1.0 - prob) * 100
```

### 🟡 Q4.4 — Pourquoi 23 features pour l'URL ? Comment les avez-vous choisies ?
**R** : *Inspirées de la littérature académique sur la détection d'URLs phishing (notamment le dataset de Mohammad et al.). Les features couvrent 4 catégories :*
1. *Structurelles : longueur, nombre de `/`, `.`, `@`, `?`, `=`...*
2. *Sémantiques : présence de mots-clés (login, verify, secure...), HTTPS, TLD risqué*
3. *Statistiques : entropie de Shannon du hostname (détecte les chaînes aléatoires), ratio de caractères spéciaux*
4. *Booléennes : utilisation d'IP, URL shortener, etc.*

*L'**importance des features** du Random Forest met en avant : `url_length`, `domain_entropy`, `count.`, `subdomain_count`, `tld_risk` comme les plus discriminantes.*

### 🟡 Q4.5 — Comment évitez-vous les faux positifs ?
**R** :
1. *Whitelist de ~30 grands domaines connus (google.com, microsoft.com, paypal.com, github.com…) qui court-circuitent le ML*
2. *IP privées/loopback marquées safe directement*
3. *Approche hybride : un texte safe ne devient dangereux que si une URL associée l'est*
4. *Seuils de confiance (on ne classe en `dangerous` qu'à partir de ~70 %)*

### 🔴 Q4.6 — Que se passe-t-il avec un email en français ? Le modèle est entraîné en anglais...
**R** : *Bonne question. Notre modèle email est principalement anglais, donc il est moins efficace sur le français — c'est une limite assumée. Mitigation : les **règles métier** (urgence, demande de credentials, typosquatting) sont multilingues car elles utilisent des listes de mots maintenues à la main. À terme, on aimerait fine-tuner un modèle multilingue type **DistilBERT-multilingual** ou **XLM-RoBERTa** pour combler cette lacune.*

### 🔴 Q4.7 — Comment savoir si votre modèle n'est pas en overfit ?
**R** : *Plusieurs garde-fous :*
1. *Split **train/test** classique (80/20) avec accuracy mesurée sur le test set seulement*
2. *LinearSVC est un modèle **simple, peu paramétré** → risque d'overfit faible vs. un deep learning*
3. *Le dataset est **assez large** (19K emails, 822K URLs) pour limiter ce risque*
4. *On pourrait améliorer avec une **cross-validation k-fold** (k=5) pour avoir une mesure plus robuste — c'est dans les améliorations possibles*

### 🔴 Q4.8 — Est-ce qu'un attaquant peut "tromper" votre modèle ? (adversarial attack)
**R** : *Oui, c'est un risque connu. Exemples :*
- *Un attaquant peut **paraphraser** son email pour éviter les mots-clés (TF-IDF est sensible aux mots exacts)*
- *Il peut utiliser un **TLD légitime** payant (.com plutôt que .tk) pour passer la règle TLD*
- *Il peut compromettre un site légitime pour héberger sa page de phishing → notre whitelist passerait à côté*

*Mitigations :*
- *Re-entraînement périodique avec nouvelles données*
- *Ajout potentiel de signaux externes (PhishTank, OpenPhish)*
- *Combination avec d'autres modèles (XGBoost, deep learning) pour un ensemble plus robuste*
- *Active learning : l'utilisateur peut marquer un faux positif/négatif → enrichit le dataset*

### 🔴 Q4.9 — Comment savez-vous que votre dataset est de bonne qualité ?
**R** : *Le dataset email vient de sources publiques connues (datasets de phishing académiques + Enron-like pour les emails légitimes). Limites :*
- *On ne contrôle pas à 100 % la qualité des labels*
- *Le dataset peut être **biaisé** (over-représentation de certains types de phishing)*
- *Pour aller plus loin : il faudrait constituer un dataset propre, labellisé manuellement, avec des emails récents et géographiquement variés*

---

## 5. Questions sur l'intégration Gmail/Outlook

### 🟢 Q5.1 — Comment se connecte-t-on à Gmail ?
**R** : *Via OAuth 2.0 standard. L'utilisateur clique "Connecter Gmail", on génère une URL d'autorisation Google avec les scopes minimaux (`gmail.readonly`), il autorise sur la page Google, et Google nous renvoie un `code` qu'on échange contre un `access_token` + `refresh_token`. On stocke les tokens en base, et à chaque requête Gmail on les utilise via la lib `google-api-python-client`. Si le `access_token` expire, on le rafraîchit automatiquement avec le `refresh_token`.*

### 🟡 Q5.2 — Pourquoi `gmail.readonly` et pas `gmail.modify` ?
**R** : *Principe du **moindre privilège**. PhishGuard ne fait que lire les emails pour les analyser, on n'a aucun besoin d'écriture/suppression. Cela rassure aussi l'utilisateur : impossible que PhishGuard supprime ou modifie sa boîte. Et ça facilite la validation par Google des scopes restreints.*

### 🟡 Q5.3 — Que se passe-t-il si l'utilisateur révoque l'accès depuis Google ?
**R** : *Au prochain appel Gmail API, on reçoit une erreur `invalid_grant`. On la catch, on supprime les credentials de notre base, et on demande à l'utilisateur de se reconnecter. Cas documenté dans `GMAIL_TOKEN_FIX.md`.*

### 🔴 Q5.4 — Comment passer en production avec Gmail ?
**R** : *Il faut que l'application soit **vérifiée par Google**, ce qui demande :*
1. *Politique de confidentialité publique*
2. *Conditions d'utilisation*
3. *Démonstration de l'usage des données par les Google reviewers (vidéo)*
4. *Justification de chaque scope*
5. *Audit de sécurité tiers si scopes "restricted"*

*Pour l'instant en mode "Testing", on est limité à 100 utilisateurs en test.*

---

## 6. Questions sur la base de données

### 🟢 Q6.1 — Combien de tables ?
**R** : *~10 tables principales : `users`, `analysis_history`, `statistics`, `email_providers`, `user_email_credentials`, `user_sessions`, `notifications`, `audit_logs`, `password_reset_tokens`, `email_verification_tokens`. Plus quelques tables de support pour le 2FA (intégré dans `users`).*

### 🟡 Q6.2 — Pourquoi async SQLAlchemy ?
**R** : *FastAPI étant async, utiliser un ORM sync bloquerait l'event loop à chaque requête DB et tuerait la performance. SQLAlchemy 2.0 supporte nativement l'async via `AsyncSession` et `asyncpg` comme driver Postgres. Cela permet de servir des centaines de requêtes concurrentes avec peu de workers.*

### 🟡 Q6.3 — Comment gérez-vous les migrations ?
**R** : *Aujourd'hui, simplement via `Base.metadata.create_all()` au démarrage (méthode `init_db`). C'est suffisant pour le développement et la démo. **En production, on devrait passer à Alembic** pour gérer les migrations versionnées (à mentionner comme amélioration).*

### 🔴 Q6.4 — Comment gérez-vous le pool de connexions ?
**R** : *Configuration explicite dans `database.py` :*
- *`pool_size=5` (taille de base)*
- *`max_overflow=10` (jusqu'à 15 connexions simultanées)*
- *`pool_pre_ping=True` (test de la connexion avant usage, détecte les connexions fermées par le serveur)*
- *`pool_recycle=1800` (recycle après 30 min, évite les timeouts SSL)*
- *`statement_cache_size=0` (compatibilité pgbouncer)*

*Un middleware `database_monitor.py` log un warning si on dépasse 8 connexions actives.*

---

## 7. Questions sur les bonnes pratiques

### 🟢 Q7.1 — Avez-vous des tests automatisés ?
**R** (à dire honnêtement) : *Pas encore. C'est l'amélioration prioritaire que j'ajouterais ensuite : pytest pour les services backend (auth, détecteurs ML), et Playwright/Cypress pour les tests E2E du frontend. Aujourd'hui, les tests sont manuels via la doc Swagger interactive et les scripts dans `backend/scripts/`.*

### 🟢 Q7.2 — Comment versionnez-vous le code ?
**R** : *Git + GitHub. Branches feature pour chaque nouvelle fonctionnalité, commits réguliers, README et documentation à jour. Pas de CI/CD encore, mais c'est une amélioration prévue (GitHub Actions pour tests + lint).*

### 🟡 Q7.3 — Comment gérez-vous les secrets ?
**R** : *Variables d'environnement via `.env` (chargé par `python-dotenv`). Le `.env` est dans `.gitignore`. Un `.env.example` documente les variables attendues sans les valeurs. **En production**, on basculerait sur AWS Secrets Manager / HashiCorp Vault / Doppler pour ne pas avoir de secrets sur disque.*

### 🟡 Q7.4 — Comment loggez-vous ?
**R** : *Logging Python standard configuré dans `main.py` : niveau INFO, format avec timestamp, double sortie (fichier `phishguard.log` + console). Les actions critiques (login, analysis, admin actions) sont aussi tracées dans la table `audit_logs` pour l'audit fonctionnel. **En production**, on ajouterait Sentry pour les erreurs et un agrégateur (Loki, Datadog) pour les logs.*

### 🔴 Q7.5 — Comment monitoreriez-vous PhishGuard en prod ?
**R** : *Stack typique :*
- *Prometheus pour les métriques (latence p95, taux d'erreur, requêtes/seconde) → exposées par `prometheus-fastapi-instrumentator`*
- *Grafana pour la visualisation*
- *Sentry pour le tracking d'erreurs (avec contexte utilisateur)*
- *Healthcheck endpoint `/api/health` surveillé par UptimeRobot*
- *Alerting Slack/PagerDuty si erreur critique ou latence > seuil*
- *Logs centralisés (Loki ou ELK)*

---

## 8. Questions pièges (à anticiper)

### 🔴 Q8.1 — Que feriez-vous différemment si vous recommenciez le projet ?
**R** (réponse honnête, montre la réflexion) :
- *Mettre en place les tests dès le début (TDD ou au moins tests unitaires sur la détection ML)*
- *Utiliser Alembic pour les migrations dès le début*
- *Chiffrer les tokens OAuth en base avec une clé KMS*
- *Conteneuriser tout avec Docker dès le début pour faciliter le déploiement*
- *Mettre en place CI/CD avec GitHub Actions*
- *Tester le multi-langue plus tôt*

### 🔴 Q8.2 — Quel est le bug le plus difficile que vous avez résolu ?
**R** (à adapter à votre vraie expérience) : *L'incohérence entre l'analyse manuelle et l'analyse depuis Gmail : un même email donnait deux résultats différents. Cause : le contenu Gmail venait au format HTML (avec balises) alors que l'analyse manuelle utilisait du texte brut. Solution : créer un **EmailPreprocessor** qui normalise les deux formats vers un texte propre avant l'analyse ML. Documenté dans `FIX_EMAIL_ANALYSIS_INCONSISTENCY.md`.*

### 🔴 Q8.3 — Pourquoi ne pas avoir utilisé un modèle de deep learning ?
**R** : *Plusieurs raisons :*
1. *Notre dataset (~20K emails, ~800K URLs) est suffisant pour des modèles classiques mais limité pour du deep learning*
2. *LinearSVC + Random Forest atteignent déjà 95-97 % d'accuracy → diminishing returns à passer en deep learning pour gagner 1-2 %*
3. *Les modèles classiques sont **plus rapides** (inférence < 10 ms) et **plus interprétables** (essentiel pour expliquer une décision à l'utilisateur)*
4. *Pas besoin de GPU à l'inférence → déploiement plus simple et moins cher*
5. *Comme amélioration future : on pourrait fine-tuner un DistilBERT pour gagner en performance et gérer le multilingue*

### 🔴 Q8.4 — Combien de temps de réponse pour une analyse en moyenne ?
**R** : *~100-300 ms pour une URL, ~200-500 ms pour un email (avec extraction et analyse des URLs). Le bottleneck n'est pas le ML (~10 ms) mais l'I/O DB (insert dans l'historique). Avec un cache Redis pour les analyses récentes, on pourrait descendre sous les 50 ms pour les requêtes répétées.*

### 🔴 Q8.5 — Que se passe-t-il si le service ML est trop sollicité ?
**R** : *Plusieurs garde-fous :*
1. *Rate limiting global (100 req/min/IP)*
2. *Le ML est en mémoire dans le process FastAPI → pas de surcoût d'appel réseau*
3. *L'inférence LinearSVC est extrêmement rapide (< 5 ms)*
4. *Si charge importante : scaler horizontalement (plusieurs workers Uvicorn ou plusieurs instances derrière un LB)*

### 🔴 Q8.6 — Quelle est votre contribution personnelle ?
**R** (si projet en équipe — adapter !) : *J'ai personnellement développé : [LISTE PRÉCISE]. J'ai aussi conçu l'architecture globale, choisi la stack, configuré la base de données, et entraîné les modèles ML.*

### 🔴 Q8.7 — Êtes-vous capable de redémarrer le projet de zéro maintenant ?
**R** : *Oui — il suffit de cloner le repo, suivre le README (`pip install`, `npm install`, configurer `.env`, `python scripts/init_db.py`, `python run.py` + `npm run dev`). Tout est documenté dans la section "Installation" du README et dans BACKEND_PART5_FINAL.md.*

---

## 9. Questions ouvertes / "vision"

### 🟡 Q9.1 — Quelle est la prochaine étape ?
**R** : *Trois priorités :*
1. *Tests automatisés (pytest + Playwright) pour sécuriser les évolutions*
2. *Déploiement en production (Docker + CI/CD + monitoring)*
3. *Re-training automatique des modèles ML avec un pipeline mensuel*

*À plus long terme : extension navigateur, app mobile, multi-langue (DistilBERT), API publique.*

### 🟡 Q9.2 — Comment monétiseriez-vous PhishGuard ?
**R** : *Modèle freemium :*
- *Gratuit : analyse limitée (50/jour), 1 provider email connecté*
- *Pro (~5€/mois) : illimité, analyse en masse, plusieurs providers, API*
- *Enterprise (sur devis) : SSO, support dédié, déploiement on-premise*

### 🔴 Q9.3 — Y a-t-il des considérations RGPD ?
**R** : *Oui :*
- *Le contenu des emails analysés contient des données personnelles → on stocke seulement un **preview** (1ères lignes) en `analysis_history`, pas le contenu complet*
- *L'utilisateur peut **supprimer son compte** → cascade delete sur toutes ses données*
- *Politique de rétention des `audit_logs` à définir (actuellement infini, devrait être plafonné à 1 an)*
- *Tokens OAuth → données sensibles, à chiffrer*
- *Mention légale et politique de confidentialité à rédiger pour la prod*

---

## 10. Astuces pour le jour J

1. **Si tu ne sais pas la réponse** → ne pas inventer. Dire : *« Je n'ai pas la réponse exacte, mais je vais regarder cet aspect précis. Voici comment je l'aborderais : [raisonnement à voix haute] »*. Ça vaut mieux qu'une fausse réponse.
2. **Si la question est confuse** → reformuler : *« Pour bien vous répondre : est-ce que vous voulez parler de X ou de Y ? »*
3. **Si on te pousse dans tes retranchements** → assumer les limites : *« Vous avez raison, c'est un point qu'on peut améliorer. Voici comment je le ferais : [proposition] »*. Le jury aime quand tu reconnais les limites.
4. **Reste concret** → toujours appuyer une réponse théorique avec un exemple du code ou de la démo.
5. **Garde une **fiche-réponses** sous la main pendant la préparation** — pas pendant la soutenance.

---

## 📌 Top 10 des questions les plus probables

D'après l'expérience générale en soutenance technique, **prépare ces 10 réponses par cœur** :

1. Quels algorithmes ML, et pourquoi ?
2. Combien d'utilisateurs / requêtes pourrais-tu gérer aujourd'hui ?
3. Quelle est ta valeur ajoutée vs les outils existants ?
4. Comment éviter les faux positifs ?
5. Comment gérer l'authentification (JWT + 2FA) ?
6. Comment se connecter à Gmail (OAuth) ?
7. Quelles sont les limites du projet ?
8. Quelle est ta contribution personnelle ?
9. Que ferais-tu différemment ?
10. Quelle est la prochaine étape ?
