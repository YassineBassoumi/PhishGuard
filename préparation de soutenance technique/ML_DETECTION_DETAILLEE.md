# 🤖 Documentation ML Détaillée — Détection de Phishing

> Document de référence pour expliquer en profondeur la **partie machine learning** du projet PhishGuard.
> À utiliser pour répondre aux questions techniques du jury sur les modèles, les datasets, les choix d'algorithmes et les métriques.

---

## 1. Vue d'ensemble

PhishGuard utilise **deux modèles ML distincts** + une **couche hybride** :

| Modèle | Cible | Algorithme | Fichier | Accuracy |
|---|---|---|---|---|
| **EmailDetector** | Texte d'email / message | LinearSVC + TF-IDF | `phishing_model.pkl` + `vectorizer.pkl` | **97,5 %** |
| **URLDetector** | URL | Random Forest (23 features) | `url_classifier.pkl` | **94,6 %** |
| **HybridEmailDetector** | Email avec URLs | Combine les deux modèles | `hybrid_email_detector.py` (orchestration) | n/a |

Tous les modèles sont chargés en **lazy loading** au premier appel et mis en cache mémoire pour le reste de la durée de vie du process.

---

## 2. Modèle EMAIL — `EmailDetector`

### 2.1 Algorithme : LinearSVC (Linear Support Vector Classifier)

**Pourquoi LinearSVC ?**
- ✅ **Rapide** à l'entraînement et à l'inférence (linéaire en nombre de features).
- ✅ **Performant sur du texte sparse** (TF-IDF produit des vecteurs très creux).
- ✅ **Peu de risque d'overfitting** sur petits/moyens datasets.
- ✅ **Décision interprétable** via `decision_function()` (distance à l'hyperplan).
- ❌ Pas de probabilités natives → on convertit la distance avec une **sigmoïde**.

```python
# Convention LinearSVC : 1 = phishing, 0 = légitime
def _sigmoid_confidence(decision_value: float) -> float:
    prob = 1.0 / (1.0 + math.exp(-decision_value))
    return float(max(prob, 1.0 - prob) * 100)
```

### 2.2 Vectorisation : TF-IDF

**TF-IDF** (Term Frequency – Inverse Document Frequency) transforme un texte en vecteur numérique en pondérant chaque mot par :
- sa fréquence dans le document (TF)
- l'inverse de sa fréquence dans le corpus (IDF)

Cela donne plus de poids aux mots **rares mais discriminants** (ex: "verify", "suspended", "urgent") et moins aux mots fréquents partout (ex: "the", "and").

Configuration utilisée :
- `max_features=5000` (top 5000 mots les plus informatifs)
- `ngram_range=(1, 2)` (mots seuls + bigrammes type "click here")
- `min_df=2`, `max_df=0.95` (filtrage du bruit)
- Tokenisation lowercase, suppression stopwords anglais

### 2.3 Dataset & métriques

- **Taille** : ~19 741 emails (mix phishing + legitimate).
- **Sources** : datasets publics (Enron-like + dataset phishing dédié).
- **Split** : ~80 / 20 train / test.
- **Accuracy finale** : **97,5 %** sur le set de test.
- **Convention de labels** : `1 = phishing`, `0 = safe`.

### 2.4 Prétraitement spécifique

Une originalité de PhishGuard : le **EmailPreprocessor** détecte les emails RFC822 bruts (avec headers `From:`, `Subject:`, `Received:`, etc.) et les nettoie automatiquement :

```python
def looks_like_raw_email(content: str) -> bool:
    # Cherche au moins 2 marqueurs SMTP + un From: ou Subject:
    head = content.lstrip()[:2000].lower()
    hits = sum(1 for h in RAW_EMAIL_HEADERS if h in head)
    has_from = re.search(r'^from:\s', head, re.MULTILINE) is not None
    has_subject = re.search(r'^subject:\s', head, re.MULTILINE) is not None
    return hits >= 2 and (has_from or has_subject)
```

Si c'est un email brut, on :
1. Parse les headers MIME (avec `email.policy.default`)
2. Extrait le body (text/plain ou text/html)
3. Strip les balises HTML mais **conserve les liens `href`** (essentiel pour la détection de phishing)
4. Décode quoted-printable / base64
5. Renvoie un texte propre prêt à être analysé

### 2.5 Features détectées (explicabilité)

Le modèle ML donne un score, mais on l'enrichit avec des **features explicables** pour l'utilisateur :

| Catégorie | Détection |
|---|---|
| **Mots-clés ML** | Top mots TF-IDF qui ont influencé la décision (extraits via `model.coef_`) |
| **PHISHING_KEYWORDS** | Liste de mots typiques (urgent, verify, suspended, click here…) |
| **URLs intégrées** | Compte des liens dans le corps |
| **TLD suspect** | TLDs risqués (`.tk`, `.ml`, `.xyz`…) |
| **URGENCY_WORDS** | Mots d'urgence ("immediately", "now", "limited time") |
| **CREDENTIAL_KEYWORDS** | Demande d'infos sensibles ("password", "SSN", "credit card") |
| **FINANCIAL_KEYWORDS** | Vocabulaire financier ("$", "money", "bank transfer") |
| **TYPO_BRANDS** | Typosquatting de marques (paypa1, amaz0n, mlcrosoft) |
| **IP brute** | Adresses IP au lieu de domaines |

---

## 3. Modèle URL — `URLDetector`

### 3.1 Algorithme : Random Forest

**Pourquoi Random Forest ?**
- ✅ Gère naturellement des **features hétérogènes** (numériques, booléennes, ratios, entropies).
- ✅ **Robuste aux outliers** et au bruit.
- ✅ Pas besoin de normalisation des features.
- ✅ **Importance des features** disponible (`feature_importances_`) → interprétable.
- ✅ Bonne performance "out of the box" sans tuning poussé.
- ❌ Plus lourd qu'un modèle linéaire (~quelques MB vs <1MB pour LinearSVC).

### 3.2 Pipeline de décision

```
URL en entrée
    ↓
1. IP privée / loopback ? → safe (95%) — court-circuit
    ↓
2. Domaine en whitelist ? → safe (98%) — court-circuit
   (LEGITIMATE_DOMAINS : google.com, microsoft.com, paypal.com, github.com…)
    ↓
3. Extraire les 23 features
    ↓
4. RandomForest.predict()
    ↓
5. Règles complémentaires (shorteners, typos, TLDs risqués)
    ↓
6. Retour (threat_level, confidence, features, recommendations)
```

### 3.3 Les 23 features (toutes documentées)

| # | Feature | Type | Description |
|---|---|---|---|
| 1 | `use_of_ip` | bool | URL pointe vers une IP au lieu d'un domaine |
| 2 | `count.` | int | Nombre de points dans l'URL |
| 3 | `count@` | int | Nombre de `@` (technique d'obfuscation) |
| 4 | `count_dir` | int | Nombre de `/` dans le path |
| 5 | `count_embed_domian` | int | Nombre de `//` dans le path |
| 6 | `short_url` | bool | URL raccourcie (bit.ly, tinyurl, t.co…) |
| 7 | `count%` | int | Nombre de `%` (encodage URL) |
| 8 | `count?` | int | Nombre de `?` |
| 9 | `count-` | int | Nombre de `-` |
| 10 | `count=` | int | Nombre de `=` (paramètres GET) |
| 11 | `url_length` | int | Longueur totale de l'URL |
| 12 | `hostname_length` | int | Longueur du hostname |
| 13 | `sus_url` | bool | Mots-clés suspects (login, verify, account, secure, banking…) |
| 14 | `fd_length` | int | Longueur du 1er répertoire (`/foo/bar` → len("foo")) |
| 15 | `count-digits` | int | Chiffres dans l'URL |
| 16 | `count-letters` | int | Lettres dans l'URL |
| 17 | `tld_length` | int | Longueur du TLD |
| 18 | `is_https` | bool | URL en HTTPS |
| 19 | `subdomain_count` | int | Nombre de sous-domaines |
| 20 | `path_length` | int | Longueur du path |
| 21 | `domain_entropy` | float | Entropie de Shannon du hostname (détection chaînes aléatoires) |
| 22 | `special_char_ratio` | float | Ratio caractères spéciaux / longueur totale |
| 23 | `tld_risk` | bool | TLD risqué (tk, ml, ga, cf, gq, xyz, top, pw, cc, buzz, work, click, link, info, online, site, club, icu, live, stream) |

### 3.4 Dataset & métriques

- **Taille** : ~822 000 URLs.
- **Split** : entraînement sur la majorité, test sur le reste.
- **Algorithme** : `RandomForestClassifier` (sklearn).
- **Accuracy finale** : **94,6 %** sur le set de test.
- **Format pickle** : `{'model': rf, 'label_encoder': le, 'features': [...]}` (le `label_encoder` permet de mapper les labels numériques vers les noms `phishing` / `legitimate`).

### 3.5 Heuristiques complémentaires

Pour minimiser les faux positifs / négatifs en production, des **règles métier** sont ajoutées :

```python
# Court-circuits qui surclassent le ML
- IP privée/loopback → safe direct
- Whitelist (LEGITIMATE_DOMAINS) → safe direct

# Indicateurs ajoutés au résultat ML
- URL_SHORTENERS : bit.ly, tinyurl, t.co, ow.ly… → +risque
- TYPO_BRANDS : paypa1, amaz0n, mlcrosoft, faceb00k… → +risque
- SUSPICIOUS_TLDS : .tk, .ml, .ga, .xyz, .top… → +risque
- URL_PHISHING_PATTERNS : "secure-update-paypal", "amazon-verify"… → +risque
```

---

## 4. Approche hybride — `HybridEmailDetector`

C'est l'innovation principale du projet. Plutôt que d'analyser un email comme un seul bloc de texte, on **sépare le texte des URLs** :

```
Email reçu
    │
    ├─ 1. Preprocessing (strip headers, decode HTML)
    │
    ├─ 2. Extraction des URLs (regex)
    │     │
    │     ├─ Texte sans URLs → EmailDetector (LinearSVC + TF-IDF)
    │     └─ Chaque URL → URLDetector (RandomForest 23 features)
    │
    ├─ 3. Combinaison des résultats
    │     - Si une URL est dangereuse → email = dangerous (au minimum)
    │     - Si le texte est clean mais URL douteuse → suspicious
    │     - Si tout est safe → safe
    │
    └─ 4. Decision trace : on conserve les prédictions brutes ML
          (utile pour le debug et l'explicabilité)
```

**Avantage clé** : un email avec un texte anodin mais une URL `paypa1-verify.tk` sera correctement détecté comme dangereux, là où un seul modèle textuel pourrait passer à côté.

---

## 5. Stratégie anti-faux-positifs

Les faux positifs sont l'ennemi numéro 1 d'un outil anti-phishing : si on alerte sur des emails légitimes, l'utilisateur perd confiance et désactive l'outil.

### Mesures appliquées

1. **Whitelist de domaines** (~30 grands domaines : Google, Microsoft, Apple, GitHub, banques, etc.) → court-circuit avant le ML.
2. **IP privées/locales** → toujours safe.
3. **Seuil de confiance** : on ne bascule en `dangerous` que si la confiance dépasse un seuil (typiquement 70 %).
4. **Approche hybride** : un texte safe ne se fait classer dangereux que si une URL associée l'est.
5. **Fallback rule-based** : si les modèles ne se chargent pas (fichier absent, erreur), on tombe sur les règles seules → service jamais down.

---

## 6. Fallback rule-based

Si `model_loader.email_model is None` ou si le pickle ne se charge pas, on applique une **détection à base de règles** :

```python
def _rule_based_analysis(content, content_lower):
    score = calculate_rule_based_threat_score(content)
    # Score basé sur :
    #  - mots-clés phishing (poids variable)
    #  - urgence
    #  - demande de credentials
    #  - typosquatting
    #  - patterns suspects (IP, mixed chars)
    if score > 0.7:    return ("dangerous", ...)
    elif score > 0.4:  return ("suspicious", ...)
    else:              return ("safe", ...)
```

Cela garantit que **PhishGuard fonctionne même sans les modèles ML** (utile en démo, en CI, en environnement minimal).

---

## 7. Métriques détaillées

| Métrique | Email (LinearSVC) | URL (Random Forest) |
|---|---|---|
| **Accuracy** | 97,5 % | 94,6 % |
| **Taille du dataset** | ~19 741 | ~822 000 |
| **Taille du modèle (.pkl)** | ~400 KB (modèle) + ~2 MB (vectorizer) | quelques MB |
| **Temps d'inférence** (1 sample) | < 5 ms | < 10 ms |
| **Temps de chargement** (lazy, 1 fois) | ~50 ms | ~100 ms |

> 💡 **Pour le jury** : ces chiffres sont à connaître par cœur, ce sont les plus probables à être demandés.

---

## 8. Choix d'architecture / Trade-offs

| Choix | Alternative | Justification |
|---|---|---|
| **LinearSVC** vs Logistic Regression / Naive Bayes | Plus performant sur sparse high-dim, distance interprétable |
| **Random Forest** vs XGBoost | RF plus simple, moins de tuning, déjà 94,6 % |
| **TF-IDF** vs Word2Vec / BERT | TF-IDF rapide, peu de mémoire, suffisant à ce niveau |
| **23 features URL manuelles** vs end-to-end deep learning | Interprétable, rapide, dataset suffisant |
| **Pickle (.pkl)** vs ONNX | Simplicité, compatibilité Python native |
| **Lazy loading** vs chargement au boot | Démarrage rapide, premier appel un peu plus lent |
| **Approche hybride** vs un seul modèle multi-modal | Modulaire, chaque modèle reste maintenable indépendamment |

---

## 9. Limites et pistes d'amélioration

### Limites actuelles
- **Langue** : modèle email essentiellement anglais → moins efficace en français/arabe.
- **Adversarial attacks** : les attaquants peuvent ré-écrire pour passer le filtre (paraphrase).
- **Concept drift** : les modèles vieillissent → besoin de ré-entraînement périodique.
- **Pas de détection de pièces jointes** (PDF, .exe, .docm).

### Améliorations envisagées
- **Re-training pipeline automatisé** (cron mensuel sur nouvelles données).
- **Multi-langue** : modèle multilingue (DistilBERT, XLM-R) + fine-tuning.
- **Ensembling** : XGBoost en plus du RF pour gagner 1-2 % d'accuracy URL.
- **Deep learning** : DistilBERT fine-tuné pour la classification email (gain potentiel ~99 %).
- **Threat intelligence** : intégration de feeds (PhishTank, OpenPhish) pour catch les phishing connus instantanément.
- **Active learning** : récupérer les feedbacks utilisateurs ("ce n'était pas du phishing") pour améliorer le modèle.

---

## 10. Reproductibilité

Pour reproduire l'entraînement (à présenter en backup au jury) :

```bash
cd backend/scripts
# 1. Télécharger les datasets
python download_datasets.py
# 2. Nettoyer
python clean_datasets.py
# 3. Entraîner le modèle email
python train_email_model.py
# Génère : phishing_model.pkl + vectorizer.pkl dans ml_models/
```

Le modèle URL a été entraîné avec un script séparé (non versionné dans le repo car le dataset est trop volumineux).

---

## 11. Diagramme de synthèse

```
┌─────────────────────────────────────────────────────────────┐
│                  Input utilisateur                          │
└──────────────────┬──────────────────────────────────────────┘
                   ▼
        ┌──────────────────────┐
        │  PhishingDetector    │  ← Façade unique
        │   (singleton)        │
        └──────────┬───────────┘
                   │
       ┌───────────┴────────────┐
       ▼                        ▼
┌─────────────┐          ┌──────────────┐
│ Email/text  │          │     URL      │
│  pipeline   │          │   pipeline   │
└──────┬──────┘          └──────┬───────┘
       │                        │
       ▼                        ▼
┌─────────────┐          ┌──────────────┐
│ Preprocess  │          │ IP private?  │
│ (RFC822)    │          │ Whitelist?   │
└──────┬──────┘          └──────┬───────┘
       │                        │
       ▼                        ▼
┌─────────────┐          ┌──────────────┐
│ TF-IDF      │          │ Extract      │
│ vectorize   │          │ 23 features  │
└──────┬──────┘          └──────┬───────┘
       ▼                        ▼
┌─────────────┐          ┌──────────────┐
│ LinearSVC   │          │ RandomForest │
│ predict     │          │ predict      │
└──────┬──────┘          └──────┬───────┘
       │                        │
       └────────┬───────────────┘
                ▼
   ┌────────────────────────────┐
   │ Add rule-based features    │
   │ + recommendations          │
   └────────────┬───────────────┘
                ▼
   ┌────────────────────────────┐
   │ (threat, confidence,       │
   │  features, recommendations)│
   └────────────────────────────┘
```
