"""
PhishGuard AI - Detection Service
ML-powered phishing detection using trained SVM model

This is a facade module that maintains backward compatibility
while using the new modular detection system.
"""

from typing import Tuple, List
from .detection import EmailDetector, URLDetector


class PhishingDetector:
    """
    Phishing detection service facade
    
    This class provides a unified interface to the modular detection system
    while maintaining backward compatibility with existing code.
    """
    
    def __init__(self):
        """Initialize detector with email and URL detection modules"""
        self.email_detector = EmailDetector()
        self.url_detector = URLDetector()
        
        # For backward compatibility, expose these as properties
        # (though they're now loaded lazily in the model_loader)
        from .detection.models import model_loader
        self._model_loader = model_loader
    
    @property
    def model(self):
        """Get email model (for backward compatibility)"""
        return self._model_loader.email_model
    
    @property
    def vectorizer(self):
        """Get email vectorizer (for backward compatibility)"""
        return self._model_loader.email_vectorizer
    
    @property
    def url_model(self):
        """Get URL model (for backward compatibility)"""
        return self._model_loader.url_model
    
    @property
    def url_feature_names(self):
        """Get URL feature names (for backward compatibility)"""
        return self._model_loader.url_feature_names
    
    @property
    def phishing_url_model(self):
        """Get phishing URL model (for backward compatibility)"""
        return self._model_loader.phishing_url_model
    
    def analyze_email(self, content: str) -> Tuple[str, float, List[str], List[str]]:
        """
        Analyze email content for phishing patterns using ML model
        
        Args:
            content: The email content to analyze
            
        Returns:
            Tuple of (threat_level, confidence, features, recommendations)
        """
        return self.email_detector.analyze(content)
    
    def analyze_url(self, url: str) -> Tuple[str, float, List[str], List[str]]:
        """
        Analyze URL for malicious indicators using ML model
        
        Args:
            url: The URL to analyze
            
        Returns:
            Tuple of (threat_level, confidence, features, recommendations)
        """
        return self.url_detector.analyze(url)


# Singleton instance for backward compatibility
detector = PhishingDetector()
