"""
Model Loader
Handles loading of ML models
"""

import os
import pickle
import joblib
from typing import Optional, Tuple, Any
from .model_config import (
    get_model_path,
    EMAIL_MODEL_FILE,
    EMAIL_VECTORIZER_FILE,
    URL_CLASSIFIER_FILE,
)


class ModelLoader:
    """Handles loading and caching of ML models"""
    
    def __init__(self):
        self._email_model = None
        self._email_vectorizer = None
        self._url_model = None
        self._url_label_encoder = None
        self._url_feature_names = None
    
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
    
    def load_url_model(self) -> Tuple[Optional[Any], Optional[Any], Optional[Any]]:
        """
        Load the URL classifier (RandomForest, 23 features, binary).
        Pickle contains: {'model': rf, 'label_encoder': le, 'features': [...]}
        
        Returns:
            Tuple of (model, label_encoder, feature_names) or (None, None, None)
        """
        if self._url_model is not None:
            return self._url_model, self._url_label_encoder, self._url_feature_names
        
        try:
            model_path = get_model_path(URL_CLASSIFIER_FILE)
            
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    data = pickle.load(f)
                self._url_model = data['model']
                self._url_label_encoder = data['label_encoder']
                self._url_feature_names = data['features']
                print(f"✓ URL classifier loaded: {len(self._url_feature_names)} features, classes={list(self._url_label_encoder.classes_)}")
                return self._url_model, self._url_label_encoder, self._url_feature_names
            else:
                print(f"⚠ URL classifier not found at {model_path}. Using rule-based detection.")
                return None, None, None
        except Exception as e:
            print(f"⚠ Error loading URL classifier: {e}. Using rule-based detection.")
            return None, None, None
    
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
    def url_label_encoder(self):
        """Get URL label encoder (lazy loading)"""
        if self._url_label_encoder is None:
            self.load_url_model()
        return self._url_label_encoder
    
    @property
    def url_feature_names(self):
        """Get URL feature names (lazy loading)"""
        if self._url_feature_names is None:
            self.load_url_model()
        return self._url_feature_names


# Singleton instance
model_loader = ModelLoader()
