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

# URL classifier: RandomForest trained on 822K URLs (94.6% accuracy)
# Pickle contains: {'model': rf, 'label_encoder': le, 'features': [...]}
URL_CLASSIFIER_FILE = 'url_classifier.pkl'
