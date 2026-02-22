"""
Model Configuration
Paths and settings for ML models
"""

import os


def get_model_path(model_filename: str) -> str:
    """
    Get the full path to a model file
    
    Args:
        model_filename: Name of the model file
        
    Returns:
        Full path to the model file
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
    return os.path.join(backend_dir, 'ml_models', model_filename)


# Model file names
EMAIL_MODEL_FILE = 'phishing_model.pkl'
EMAIL_VECTORIZER_FILE = 'vectorizer.pkl'
URL_MODEL_FILE = 'url_phishing_model.pkl'
URL_FEATURES_FILE = 'url_feature_names.pkl'

# Phishing URL model names (in order of preference)
PHISHING_URL_MODEL_FILES = [
    'phishing_url_model_final_v3.pkl',  # Latest retrained model
    'phishing_model_final_v2.pkl',      # Previous version
    'phishing_url_model.pkl'            # Original name
]
