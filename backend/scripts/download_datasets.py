"""
Download Datasets for PhishGuard Email & URL Models

This script downloads the required datasets for training:
1. Email text model: Phishing email body text (phishing vs legitimate)
2. URL model: Already trained (822K URLs, 94.6% accuracy) - optional re-download

Datasets:
- Primary: ealvaradob/phishing-dataset from HuggingFace (mail subset = 18K+ emails)
- Large: Kaggle "Phishing Email Dataset" by Naser Alam (82.5K emails) - requires Kaggle API
- Combined: ealvaradob/phishing-dataset "combined_reduced" (mixed: emails, SMS, URLs, websites)

Usage:
    python scripts/download_datasets.py --source huggingface
    python scripts/download_datasets.py --source kaggle
    python scripts/download_datasets.py --source all
"""

import os
import sys
import argparse
import pandas as pd

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
DATASETS_DIR = os.path.join(BACKEND_DIR, 'datasets')
RAW_DIR = os.path.join(DATASETS_DIR, 'raw')
PROCESSED_DIR = os.path.join(DATASETS_DIR, 'processed')


def ensure_dirs():
    """Create dataset directories if they don't exist."""
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    print(f"  Dataset directories ready: {DATASETS_DIR}")


def download_huggingface_mail():
    """
    Download email phishing dataset from HuggingFace.
    Source: zefang-liu/phishing-email-dataset (18,650 emails, Parquet format)
    Original: Kaggle 'Phishing Email Detection' by Cyber Cop / subhajournal
    Columns: text (email body), label (1=phishing, 0=safe)
    """
    print("\n" + "=" * 60)
    print("  DOWNLOADING: HuggingFace Email Dataset")
    print("  Source: zefang-liu/phishing-email-dataset")
    print("  Size: ~18,650 emails (52 MB)")
    print("=" * 60)

    try:
        from datasets import load_dataset
    except ImportError:
        print("\n  [!] 'datasets' library not installed.")
        print("  Run: pip install datasets")
        return False

    try:
        dataset = load_dataset("zefang-liu/phishing-email-dataset")
        df = dataset['train'].to_pandas()

        # Normalize columns: 'Email Text' -> 'text', 'Email Type' -> 'label'
        if 'Email Text' in df.columns:
            df = df.rename(columns={'Email Text': 'text', 'Email Type': 'label'})
        if 'Unnamed: 0' in df.columns:
            df = df.drop(columns=['Unnamed: 0'])

        # Convert label: 'Phishing Email' -> 1, 'Safe Email' -> 0
        if df['label'].dtype == object:
            df['label'] = df['label'].map({
                'Phishing Email': 1, 'phishing': 1,
                'Safe Email': 0, 'safe': 0, 'legitimate': 0
            })
            df = df.dropna(subset=['label'])
            df['label'] = df['label'].astype(int)

        output_path = os.path.join(RAW_DIR, 'hf_email_phishing.csv')
        df.to_csv(output_path, index=False)

        n_phishing = (df['label'] == 1).sum()
        n_benign = (df['label'] == 0).sum()

        print(f"\n  [OK] Downloaded {len(df)} emails")
        print(f"       Phishing: {n_phishing} | Benign: {n_benign}")
        print(f"       Columns: {list(df.columns)}")
        print(f"       Saved to: {output_path}")
        return True

    except Exception as e:
        print(f"\n  [ERROR] Failed to download: {e}")
        return False


def download_huggingface_texts_json():
    """
    Download texts.json from ealvaradob/phishing-dataset (email + SMS texts).
    This is a direct file download (no loading script needed).
    Contains text + label columns, mix of emails and SMS.
    """
    print("\n" + "=" * 60)
    print("  DOWNLOADING: ealvaradob texts.json (emails + SMS)")
    print("  Source: ealvaradob/phishing-dataset/texts.json")
    print("  Size: ~52 MB")
    print("=" * 60)

    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        print("\n  [!] 'huggingface_hub' not installed.")
        print("  Run: pip install huggingface_hub")
        return False

    try:
        filepath = hf_hub_download(
            repo_id="ealvaradob/phishing-dataset",
            filename="texts.json",
            repo_type="dataset",
            local_dir=RAW_DIR
        )

        df = pd.read_json(filepath)

        output_path = os.path.join(RAW_DIR, 'hf_texts_combined.csv')
        df.to_csv(output_path, index=False)

        n_phishing = (df['label'] == 1).sum()
        n_benign = (df['label'] == 0).sum()

        print(f"\n  [OK] Downloaded {len(df)} text samples")
        print(f"       Phishing: {n_phishing} | Benign: {n_benign}")
        print(f"       Columns: {list(df.columns)}")
        print(f"       Saved to: {output_path}")
        return True

    except Exception as e:
        print(f"\n  [ERROR] Failed to download: {e}")
        return False


def download_kaggle_dataset():
    """
    Download the large Kaggle phishing email dataset (82.5K emails).
    Requires Kaggle API credentials (~/.kaggle/kaggle.json).
    
    Dataset: naserabdullahalam/phishing-email-dataset
    - 82,500 emails (42,891 spam + 39,595 legit)
    - Combined from: Enron, Ling, CEAS, Nazario, Nigerian Fraud, SpamAssassin
    """
    print("\n" + "=" * 60)
    print("  DOWNLOADING: Kaggle Phishing Email Dataset (82.5K)")
    print("  Source: naserabdullahalam/phishing-email-dataset")
    print("  Size: ~80MB compressed")
    print("=" * 60)

    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except ImportError:
        print("\n  [!] 'kaggle' library not installed.")
        print("  Run: pip install kaggle")
        print("  Then place your kaggle.json in ~/.kaggle/")
        _print_kaggle_manual_instructions()
        return False

    try:
        api = KaggleApi()
        api.authenticate()

        kaggle_dir = os.path.join(RAW_DIR, 'kaggle_phishing_email')
        os.makedirs(kaggle_dir, exist_ok=True)

        print("  Downloading from Kaggle API...")
        api.dataset_download_files(
            'naserabdullahalam/phishing-email-dataset',
            path=kaggle_dir,
            unzip=True
        )

        # Find CSV files in the downloaded data
        csv_files = [f for f in os.listdir(kaggle_dir) if f.endswith('.csv')]
        print(f"\n  [OK] Downloaded to: {kaggle_dir}")
        print(f"       Files: {csv_files}")

        for csv_file in csv_files:
            filepath = os.path.join(kaggle_dir, csv_file)
            df = pd.read_csv(filepath, nrows=5)
            print(f"       {csv_file}: columns={list(df.columns)}")

        return True

    except Exception as e:
        print(f"\n  [ERROR] Kaggle download failed: {e}")
        _print_kaggle_manual_instructions()
        return False


def _print_kaggle_manual_instructions():
    """Print manual download instructions for Kaggle."""
    print("\n  ─── MANUAL DOWNLOAD INSTRUCTIONS ───")
    print("  1. Go to: https://www.kaggle.com/datasets/naserabdullahalam/phishing-email-dataset")
    print("  2. Click 'Download' (requires Kaggle account)")
    print("  3. Extract the ZIP file")
    print(f"  4. Place the CSV file(s) in: {os.path.join(RAW_DIR, 'kaggle_phishing_email')}")
    print("  ────────────────────────────────────")


def show_summary():
    """Show summary of downloaded datasets."""
    print("\n" + "=" * 60)
    print("  DATASET SUMMARY")
    print("=" * 60)

    if not os.path.exists(RAW_DIR):
        print("  No datasets downloaded yet.")
        return

    for filename in sorted(os.listdir(RAW_DIR)):
        filepath = os.path.join(RAW_DIR, filename)
        if os.path.isfile(filepath) and filename.endswith('.csv'):
            try:
                df = pd.read_csv(filepath)
                size_mb = os.path.getsize(filepath) / (1024 * 1024)
                print(f"\n  {filename}")
                print(f"    Rows: {len(df):,} | Columns: {list(df.columns)}")
                print(f"    Size: {size_mb:.1f} MB")
                if 'label' in df.columns:
                    print(f"    Labels: {df['label'].value_counts().to_dict()}")
            except Exception as e:
                print(f"\n  {filename} — Error reading: {e}")
        elif os.path.isdir(filepath):
            csv_count = len([f for f in os.listdir(filepath) if f.endswith('.csv')])
            print(f"\n  {filename}/ ({csv_count} CSV files)")

    print("\n" + "=" * 60)
    print("  NEXT STEP: Run the training script")
    print("    python scripts/train_email_model.py")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Download PhishGuard training datasets')
    parser.add_argument(
        '--source',
        choices=['huggingface', 'kaggle', 'all', 'summary'],
        default='huggingface',
        help='Which dataset source to download from (default: huggingface)'
    )
    args = parser.parse_args()

    print("\n╔══════════════════════════════════════════════════╗")
    print("║   PhishGuard — Dataset Downloader               ║")
    print("╚══════════════════════════════════════════════════╝")

    ensure_dirs()

    if args.source == 'summary':
        show_summary()
        return

    if args.source in ('huggingface', 'all'):
        download_huggingface_mail()
        download_huggingface_texts_json()

    if args.source in ('kaggle', 'all'):
        download_kaggle_dataset()

    show_summary()


if __name__ == '__main__':
    main()
