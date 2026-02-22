"""
Setup script for PhishGuard backend
Helps verify environment and dependencies
"""
import os
import sys


def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("   Create one from the template in the README")
        return False
    print("✅ .env file found")
    return True


def check_required_env_vars():
    """Check if required environment variables are set"""
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        'DATABASE_URL',
        'SECRET_KEY',
    ]
    
    optional_vars = [
        'GOOGLE_CLIENT_ID',
        'GOOGLE_CLIENT_SECRET',
        'MICROSOFT_CLIENT_ID',
        'MICROSOFT_CLIENT_SECRET',
    ]
    
    all_good = True
    for var in required_vars:
        if not os.getenv(var):
            print(f"❌ {var} not set in .env")
            all_good = False
        else:
            print(f"✅ {var} is set")
    
    print("\nOptional OAuth credentials:")
    for var in optional_vars:
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            print(f"⚠️  {var} not set (OAuth won't work)")
    
    return all_good


def check_ml_models():
    """Check if ML model files exist"""
    model_files = [
        'ml_models/phishing_model.pkl',
        'ml_models/vectorizer.pkl',
        'ml_models/phishing_url_model_final_v3.pkl',
    ]
    
    found = False
    for model_file in model_files:
        if os.path.exists(model_file):
            print(f"✅ {model_file} found")
            found = True
        else:
            print(f"⚠️  {model_file} not found")
    
    return found


def main():
    """Run setup checks"""
    print("=" * 60)
    print("PhishGuard Backend Setup Check")
    print("=" * 60)
    print()
    
    print("Checking environment configuration...")
    env_ok = check_env_file()
    print()
    
    if env_ok:
        print("Checking environment variables...")
        vars_ok = check_required_env_vars()
        print()
    else:
        vars_ok = False
    
    print("Checking ML models...")
    models_ok = check_ml_models()
    print()
    
    print("=" * 60)
    if env_ok and vars_ok and models_ok:
        print("✅ Setup looks good! You can start the server:")
        print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    else:
        print("⚠️  Some issues found. Please fix them before starting.")
    print("=" * 60)


if __name__ == "__main__":
    main()
