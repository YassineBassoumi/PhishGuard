"""
Clean & Preprocess PhishGuard Email Datasets

Takes the two raw HuggingFace CSVs, merges them, deduplicates,
removes junk rows, and outputs a single clean CSV ready for training.

Input:
    datasets/raw/hf_email_phishing.csv   (zefang-liu, ~18K emails)
    datasets/raw/hf_texts_combined.csv   (ealvaradob, mixed emails+SMS)

Output:
    datasets/processed/emails_cleaned.csv  (deduplicated, cleaned)

Usage:
    python scripts/clean_datasets.py
    python scripts/clean_datasets.py --min-words 5 --max-chars 50000
"""

import os
import re
import sys
import argparse
import pandas as pd
import numpy as np

# ── Paths ────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
RAW_DIR = os.path.join(BACKEND_DIR, 'datasets', 'raw')
PROCESSED_DIR = os.path.join(BACKEND_DIR, 'datasets', 'processed')

RAW_FILE_1 = os.path.join(RAW_DIR, 'hf_email_phishing.csv')
RAW_FILE_2 = os.path.join(RAW_DIR, 'hf_texts_combined.csv')
OUTPUT_FILE = os.path.join(PROCESSED_DIR, 'emails_cleaned.csv')


def load_raw_datasets():
    """Load both raw CSVs and return a merged DataFrame."""
    frames = []

    for path, name in [(RAW_FILE_1, 'hf_email_phishing'),
                       (RAW_FILE_2, 'hf_texts_combined')]:
        if not os.path.exists(path):
            print(f"  [SKIP] {name} not found at {path}")
            continue
        df = pd.read_csv(path)
        df['source'] = name
        print(f"  [OK] Loaded {name}: {len(df):,} rows, columns={list(df.columns)}")
        frames.append(df)

    if not frames:
        print("  [ERROR] No raw datasets found. Run download_datasets.py first.")
        sys.exit(1)

    merged = pd.concat(frames, ignore_index=True)
    print(f"\n  Merged total: {len(merged):,} rows")
    return merged


def clean_text(text):
    """Clean a single text string."""
    if not isinstance(text, str):
        return ""

    # Strip HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)

    # Remove URLs (http/https/www)
    text = re.sub(r'https?://\S+|www\.\S+', ' [URL] ', text)

    # Remove email addresses
    text = re.sub(r'\S+@\S+\.\S+', ' [EMAIL] ', text)

    # Collapse multiple whitespace / newlines into single space
    text = re.sub(r'\s+', ' ', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def run_cleaning(df, min_words=5, max_chars=50000):
    """
    Full cleaning pipeline:
    1. Validate columns
    2. Drop nulls
    3. Clean text
    4. Remove too-short / too-long texts
    5. Deduplicate
    6. Validate labels
    """
    stats = {}
    stats['raw_total'] = len(df)

    # ── 1. Validate required columns ─────────────────────────────────────
    if 'text' not in df.columns or 'label' not in df.columns:
        print("  [ERROR] Missing 'text' or 'label' column.")
        sys.exit(1)

    # ── 2. Drop rows with null text or label ─────────────────────────────
    before = len(df)
    df = df.dropna(subset=['text', 'label'])
    stats['dropped_nulls'] = before - len(df)
    print(f"  Dropped nulls: {stats['dropped_nulls']:,}")

    # ── 3. Ensure label is int (0 or 1) ──────────────────────────────────
    if df['label'].dtype == object:
        label_map = {
            'Phishing Email': 1, 'phishing': 1, 'spam': 1, '1': 1,
            'Safe Email': 0, 'safe': 0, 'legitimate': 0, 'ham': 0, '0': 0
        }
        df['label'] = df['label'].map(label_map)
        before = len(df)
        df = df.dropna(subset=['label'])
        stats['dropped_bad_labels'] = before - len(df)
    else:
        # Keep only 0 and 1
        before = len(df)
        df = df[df['label'].isin([0, 1])]
        stats['dropped_bad_labels'] = before - len(df)

    df['label'] = df['label'].astype(int)
    print(f"  Dropped invalid labels: {stats['dropped_bad_labels']:,}")

    # ── 4. Clean text ────────────────────────────────────────────────────
    print("  Cleaning text (HTML, whitespace, URLs, emails)...")
    df['text'] = df['text'].apply(clean_text)

    # ── 5. Remove empty / too-short texts ────────────────────────────────
    before = len(df)
    df['word_count'] = df['text'].str.split().str.len()
    df = df[df['word_count'] >= min_words]
    stats['dropped_short'] = before - len(df)
    print(f"  Dropped short texts (<{min_words} words): {stats['dropped_short']:,}")

    # ── 6. Remove excessively long texts ─────────────────────────────────
    before = len(df)
    df = df[df['text'].str.len() <= max_chars]
    stats['dropped_long'] = before - len(df)
    print(f"  Dropped long texts (>{max_chars:,} chars): {stats['dropped_long']:,}")

    # ── 7. Deduplicate on text ───────────────────────────────────────────
    before = len(df)
    df = df.drop_duplicates(subset=['text'], keep='first')
    stats['dropped_dupes'] = before - len(df)
    print(f"  Dropped duplicates: {stats['dropped_dupes']:,}")

    # ── 8. Drop helper columns, keep only text + label ───────────────────
    df = df[['text', 'label']].reset_index(drop=True)
    stats['final_total'] = len(df)

    return df, stats


def print_summary(df, stats):
    """Print a clean summary of the cleaning results."""
    n_phish = (df['label'] == 1).sum()
    n_safe = (df['label'] == 0).sum()
    ratio = n_phish / n_safe if n_safe > 0 else float('inf')

    avg_len = df['text'].str.len().mean()
    median_len = df['text'].str.len().median()

    print("\n" + "=" * 60)
    print("  CLEANING SUMMARY")
    print("=" * 60)
    print(f"  Raw rows loaded:       {stats['raw_total']:>10,}")
    print(f"  Dropped nulls:         {stats['dropped_nulls']:>10,}")
    print(f"  Dropped bad labels:    {stats['dropped_bad_labels']:>10,}")
    print(f"  Dropped short texts:   {stats['dropped_short']:>10,}")
    print(f"  Dropped long texts:    {stats['dropped_long']:>10,}")
    print(f"  Dropped duplicates:    {stats['dropped_dupes']:>10,}")
    print(f"  ─────────────────────────────────────")
    print(f"  Final clean rows:      {stats['final_total']:>10,}")
    print(f"    Phishing (1):        {n_phish:>10,}")
    print(f"    Safe (0):            {n_safe:>10,}")
    print(f"    Ratio (phish/safe):  {ratio:>10.2f}")
    print(f"  Avg text length:       {avg_len:>10,.0f} chars")
    print(f"  Median text length:    {median_len:>10,.0f} chars")
    print("=" * 60)

    # Label distribution warning
    if ratio > 2.0 or ratio < 0.5:
        print("  ⚠  Dataset is imbalanced. Consider oversampling/undersampling during training.")


def main():
    parser = argparse.ArgumentParser(description='Clean PhishGuard email datasets')
    parser.add_argument('--min-words', type=int, default=5,
                        help='Minimum word count to keep a sample (default: 5)')
    parser.add_argument('--max-chars', type=int, default=50000,
                        help='Maximum character count to keep a sample (default: 50000)')
    args = parser.parse_args()

    print("\n╔══════════════════════════════════════════════════╗")
    print("║   PhishGuard — Dataset Cleaner                  ║")
    print("╚══════════════════════════════════════════════════╝\n")

    os.makedirs(PROCESSED_DIR, exist_ok=True)

    # Load
    print("── Loading raw datasets ──")
    df = load_raw_datasets()

    # Clean
    print("\n── Cleaning ──")
    df_clean, stats = run_cleaning(df, min_words=args.min_words, max_chars=args.max_chars)

    # Save
    df_clean.to_csv(OUTPUT_FILE, index=False)
    size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
    print(f"\n  Saved to: {OUTPUT_FILE}")
    print(f"  File size: {size_mb:.1f} MB")

    # Summary
    print_summary(df_clean, stats)

    print(f"\n  NEXT STEP: Train the email model")
    print(f"    python scripts/train_email_model.py\n")


if __name__ == '__main__':
    main()
