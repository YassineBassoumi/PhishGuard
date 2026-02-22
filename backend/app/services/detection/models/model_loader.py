"""
Model Loader
Handles loading of ML models
"""

import os
import joblib
from typing import Optional, Tuple, Any
from .model_config import (
    get_model_path,
    EMAIL_MODEL_FILE,
    EMAIL_VECTORIZER_FILE,
    URL_MODEL_FILE,
    URL_FEATURES_FILE,
    PHISHING_URL_MODEL_FILES
)


class ModelLoader:
    """Handles loading and caching of ML models"""
    
    def __init__(self):
        self._email_model = None
        self._email_vectorizer = None
        self._url_model = None
        self._url_feature_names = None
        self._phishing_url_model = None
    
    def load_email_model(self) -> Tuple[Optional[Any], Optional[Any]]:
        """
        Load the email phishing detection model and vectorizer
        
        Returns:
            Tuple of (model, vectorizer) or (None, None) if loading fails
        """
        if self._email_model is not None and self._email_vectorizer is not None:
            return self._email_model, self._email_vectorizer
        
        try:
            model_path = get_model_path(EMAIL_MODEL_FILE)
            vectorizer_path = get_model_path(EMAIL_VECTORIZER_FILE)
            
            if os.path.exists(model_path) and os.path.exists(vectorizer_path):
                self._email_model = joblib.load(model_path)
                self._email_vectorizer = joblib.load(vectorizer_path)
                print("✓ Email ML model loaded successfully")
                return self._email_model, self._email_vectorizer
            else:
                print("⚠ Email ML model files not found. Using rule-based detection as fallback.")
                return None, None
        except Exception as e:
            print(f"⚠ Error loading email ML model: {e}. Using rule-based detection as fallback.")
            return None, None
    
    def load_url_model(self) -> Tuple[Optional[Any], Optional[Any]]:
        """
        Load the URL phishing detection model and feature names
        
        Returns:
            Tuple of (model, feature_names) or (None, None) if loading fails
        """
        if self._url_model is not None and self._url_feature_names is not None:
            return self._url_model, self._url_feature_names
        
        try:
            model_path = get_model_path(URL_MODEL_FILE)
            features_path = get_model_path(URL_FEATURES_FILE)
            
            if os.path.exists(model_path) and os.path.exists(features_path):
                self._url_model = joblib.load(model_path)
                self._url_feature_names = joblib.load(features_path)
                print("✓ URL ML model loaded successfully")
                return self._url_model, self._url_feature_names
            else:
                print("⚠ URL ML model files not found. Using rule-based detection as fallback.")
                return None, None
        except Exception as e:
            print(f"⚠ Error loading URL ML model: {e}. Using rule-based detection as fallback.")
            return None, None
    
    def load_phishing_url_model(self) -> Optional[Any]:
        """
        Load the Phishing-URL-Detection model (12 features)
        
        Returns:
            Model or None if loading fails
        """
        if self._phishing_url_model is not None:
            return self._phishing_url_model
        
        try:
            # Try models in order of preference (newest first)
            model_path = None
            for model_name in PHISHING_URL_MODEL_FILES:
                test_path = get_model_path(model_name)
                if os.path.exists(test_path):
                    model_path = test_path
                    break
            
            if model_path:
                self._phishing_url_model = joblib.load(model_path)
                print(f"✓ Phishing URL model loaded successfully: {os.path.basename(model_path)}")
                return self._phishing_url_model
            else:
                print("⚠ Phishing URL model not found.")
                return None
        except Exception as e:
            print(f"⚠ Error loading Phishing URL model: {e}")
            return None
    
    @property
    def email_model(self):
        """Get email model (lazy loading)"""
        if self._email_model is None:
            self.load_email_model()
        return self._email_model
    
    @property
    def email_vectorizer(self):
        """Get email vectorizer (lazy loading)"""
        if self._email_vectorizer is None:
            self.load_email_model()
        return self._email_vectorizer
    
    @property
    def url_model(self):
        """Get URL model (lazy loading)"""
        if self._url_model is None:
            self.load_url_model()
        return self._url_model
    
    @property
    def url_feature_names(self):
        """Get URL feature names (lazy loading)"""
        if self._url_feature_names is None:
            self.load_url_model()
        return self._url_feature_names
    
    @property
    def phishing_url_model(self):
        """Get phishing URL model (lazy loading)"""
        if self._phishing_url_model is None:
            self.load_phishing_url_model()
        return self._phishing_url_model


# Singleton instance
model_loader = ModelLoader()
