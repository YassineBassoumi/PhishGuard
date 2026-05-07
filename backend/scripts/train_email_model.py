"""
Train PhishGuard Email Phishing Detection Model

Reads the cleaned email dataset, trains a TF-IDF + classifier pipeline,
evaluates performance, and saves the best model + vectorizer.

Input:
    ../../datasets/processed/emails_cleaned.csv   (text, label)
    label: 1 = phishing, 0 = safe/legitimate

Output:
    ../ml_models/phishing_model.pkl   (trained classifier)
    ../ml_models/vectorizer.pkl       (fitted TF-IDF vectorizer)

Usage:
    python scripts/train_email_model.py
    python scripts/train_email_model.py --model logistic_regression
    python scripts/train_email_model.py --model xgboost
"""

import os
import sys
import time
import argparse
import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    f1_score,
    roc_auc_score,
)

# ── Paths ────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)           # PhishGuard/
MODELLS_ROOT = os.path.dirname(PROJECT_ROOT)           # modells/

DATASET_PATH = os.path.join(MODELLS_ROOT, 'datasets', 'processed', 'emails_cleaned.csv')
MODEL_DIR = os.path.join(BACKEND_DIR, 'ml_models')
MODEL_OUTPUT = os.path.join(MODEL_DIR, 'phishing_model.pkl')
VECTORIZER_OUTPUT = os.path.join(MODEL_DIR, 'vectorizer.pkl')

# ── Available classifiers ────────────────────────────────────────────────
CLASSIFIERS = {
    'logistic_regression': lambda: LogisticRegression(
        max_iter=1000, C=1.0, solver='lbfgs', random_state=42
    ),
    'linear_svc': lambda: LinearSVC(
        max_iter=2000, C=1.0, random_state=42
    ),
    'naive_bayes': lambda: MultinomialNB(alpha=0.1),
    'random_forest': lambda: RandomForestClassifier(
        n_estimators=200, max_depth=None, random_state=42, n_jobs=-1
    ),
    'gradient_boosting': lambda: GradientBoostingClassifier(
        n_estimators=200, max_depth=5, learning_rate=0.1, random_state=42
    ),
}

# Try to add XGBoost if available
try:
    from xgboost import XGBClassifier
    CLASSIFIERS['xgboost'] = lambda: XGBClassifier(
        n_estimators=300, max_depth=6, learning_rate=0.1,
        use_label_encoder=False, eval_metric='logloss',
        random_state=42, n_jobs=-1
    )
except ImportError:
    pass


def load_dataset(path: str) -> pd.DataFrame:
    """Load and validate the cleaned email dataset."""
    if not os.path.exists(path):
        print(f"  [ERROR] Dataset not found: {path}")
        print(f"  Run: python scripts/clean_datasets.py")
        sys.exit(1)

    df = pd.read_csv(path)

    if 'text' not in df.columns or 'label' not in df.columns:
        print(f"  [ERROR] Dataset must have 'text' and 'label' columns.")
        sys.exit(1)

    # Drop any remaining nulls
    df = df.dropna(subset=['text', 'label'])
    df['label'] = df['label'].astype(int)

    n_phish = (df['label'] == 1).sum()
    n_safe = (df['label'] == 0).sum()
    print(f"  Loaded {len(df):,} samples — Phishing: {n_phish:,} | Safe: {n_safe:,}")
    return df


def build_vectorizer(max_features: int = 50000) -> TfidfVectorizer:
    """Create a TF-IDF vectorizer with good defaults for email text."""
    return TfidfVectorizer(
        max_features=max_features,
        ngram_range=(1, 2),       # unigrams + bigrams
        min_df=2,                 # ignore very rare terms
        max_df=0.95,              # ignore terms in >95% of docs
        sublinear_tf=True,        # apply log normalization
        strip_accents='unicode',
        lowercase=True,
    )


def train_and_evaluate(X_train, X_test, y_train, y_test, clf_name, clf):
    """Train a classifier and return metrics."""
    print(f"\n  ── Training: {clf_name} ──")
    t0 = time.time()
    clf.fit(X_train, y_train)
    train_time = time.time() - t0

    y_pred = clf.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')

    # AUC if possible
    try:
        y_proba = clf.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, y_proba)
    except (AttributeError, IndexError):
        auc = None

    print(f"  Accuracy:  {acc:.4f}")
    print(f"  F1 (wtd):  {f1:.4f}")
    if auc is not None:
        print(f"  AUC-ROC:   {auc:.4f}")
    print(f"  Time:      {train_time:.1f}s")

    return {
        'name': clf_name,
        'model': clf,
        'accuracy': acc,
        'f1': f1,
        'auc': auc,
        'time': train_time,
        'y_pred': y_pred,
    }


def main():
    parser = argparse.ArgumentParser(description='Train PhishGuard email phishing model')
    parser.add_argument(
        '--model', type=str, default='auto',
        choices=['auto'] + list(CLASSIFIERS.keys()),
        help='Classifier to use. "auto" tries all and picks best (default: auto)'
    )
    parser.add_argument(
        '--max-features', type=int, default=50000,
        help='Max TF-IDF features (default: 50000)'
    )
    parser.add_argument(
        '--test-size', type=float, default=0.2,
        help='Test set fraction (default: 0.2)'
    )
    args = parser.parse_args()

    print("\n╔══════════════════════════════════════════════════╗")
    print("║   PhishGuard — Email Model Trainer               ║")
    print("╚══════════════════════════════════════════════════╝\n")

    # ── 1. Load data ─────────────────────────────────────────────────────
    print("── Loading dataset ──")
    df = load_dataset(DATASET_PATH)

    X_raw = df['text'].values
    y = df['label'].values

    # ── 2. Split ─────────────────────────────────────────────────────────
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X_raw, y, test_size=args.test_size, random_state=42, stratify=y
    )
    print(f"\n  Train: {len(X_train_raw):,} | Test: {len(X_test_raw):,}")

    # ── 3. Vectorize ─────────────────────────────────────────────────────
    print("\n── Vectorizing (TF-IDF) ──")
    vectorizer = build_vectorizer(max_features=args.max_features)
    X_train = vectorizer.fit_transform(X_train_raw)
    X_test = vectorizer.transform(X_test_raw)
    print(f"  Vocabulary size: {len(vectorizer.vocabulary_):,}")
    print(f"  Feature matrix:  {X_train.shape}")

    # ── 4. Train ─────────────────────────────────────────────────────────
    results = []

    if args.model == 'auto':
        print("\n── Auto mode: trying all classifiers ──")
        for name, factory in CLASSIFIERS.items():
            try:
                clf = factory()
                result = train_and_evaluate(X_train, X_test, y_train, y_test, name, clf)
                results.append(result)
            except Exception as e:
                print(f"  [SKIP] {name}: {e}")
    else:
        clf = CLASSIFIERS[args.model]()
        result = train_and_evaluate(X_train, X_test, y_train, y_test, args.model, clf)
        results.append(result)

    if not results:
        print("\n  [ERROR] No classifier succeeded.")
        sys.exit(1)

    # ── 5. Pick best model ───────────────────────────────────────────────
    best = max(results, key=lambda r: r['f1'])

    print("\n" + "=" * 60)
    print("  RESULTS SUMMARY")
    print("=" * 60)
    print(f"  {'Classifier':<25} {'Accuracy':>10} {'F1':>10} {'AUC':>10} {'Time':>8}")
    print(f"  {'-'*25} {'-'*10} {'-'*10} {'-'*10} {'-'*8}")
    for r in sorted(results, key=lambda x: -x['f1']):
        auc_str = f"{r['auc']:.4f}" if r['auc'] is not None else "N/A"
        marker = " <-- BEST" if r['name'] == best['name'] else ""
        print(f"  {r['name']:<25} {r['accuracy']:>10.4f} {r['f1']:>10.4f} {auc_str:>10} {r['time']:>7.1f}s{marker}")

    # ── 6. Detailed report for best model ────────────────────────────────
    print(f"\n── Best model: {best['name']} ──")
    print("\n  Classification Report:")
    print(classification_report(
        y_test, best['y_pred'],
        target_names=['Safe (0)', 'Phishing (1)'],
        digits=4
    ))

    print("  Confusion Matrix:")
    cm = confusion_matrix(y_test, best['y_pred'])
    print(f"                  Predicted Safe  Predicted Phishing")
    print(f"  Actual Safe     {cm[0][0]:>14,}  {cm[0][1]:>18,}")
    print(f"  Actual Phishing {cm[1][0]:>14,}  {cm[1][1]:>18,}")

    # ── 7. Save ──────────────────────────────────────────────────────────
    os.makedirs(MODEL_DIR, exist_ok=True)

    joblib.dump(best['model'], MODEL_OUTPUT)
    joblib.dump(vectorizer, VECTORIZER_OUTPUT)

    model_size = os.path.getsize(MODEL_OUTPUT) / 1024
    vec_size = os.path.getsize(VECTORIZER_OUTPUT) / 1024

    print(f"\n  Saved model:      {MODEL_OUTPUT} ({model_size:.0f} KB)")
    print(f"  Saved vectorizer: {VECTORIZER_OUTPUT} ({vec_size:.0f} KB)")

    # ── 8. Label convention note ─────────────────────────────────────────
    print("\n  LABEL CONVENTION:")
    print("    0 = Safe / Legitimate")
    print("    1 = Phishing / Spam")
    print("    (email_detector.py must use: prediction == 1 for phishing)")

    print(f"\n  Training complete. Model ready for PhishGuard.\n")


if __name__ == '__main__':
    main()
