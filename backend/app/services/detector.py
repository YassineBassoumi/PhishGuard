"""
PhishGuard AI - Detection Service
ML-powered phishing detection using trained SVM model

This is a facade module that maintains backward compatibility
while using the new modular detection system.
"""

from typing import Tuple, List, Optional, Dict
from .detection import EmailDetector, URLDetector
from .detection.hybrid_email_detector import HybridEmailDetector


class PhishingDetector:
    """
    Phishing detection service facade
    
    This class provides a unified interface to the modular detection system
    while maintaining backward compatibility with existing code.
    """
    
    def __init__(self):
        """Initialize detector with email, URL, and hybrid detection modules"""
        self.email_detector = EmailDetector()
        self.url_detector = URLDetector()
        self.hybrid_email_detector = HybridEmailDetector()
        
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
    
    def analyze_email(self, content: str, use_hybrid: bool = False) -> Tuple[str, float, List[str], List[str]]:
        """
        Analyze message content for phishing patterns using ML model
        
        Args:
            content: Message content to analyze (email body, plain text, etc.)
            use_hybrid: If True, uses hybrid analysis (splits text and URLs for separate analysis)
            
        Returns:
            Tuple of (threat_level, confidence, features, recommendations)
            
        Note: Uses LinearSVC model trained on 19,741 emails (97.5% accuracy).
        Label convention: 1 = Phishing, 0 = Safe.
        
        Hybrid mode (use_hybrid=True):
        - Extracts URLs from content
        - Analyzes text separately using email model
        - Analyzes each URL using URL model
        - Combines results for better accuracy
        """
        if use_hybrid:
            # Use hybrid analysis (text + URL split)
            threat_level, confidence, features, recommendations, url_results, _trace = \
                self.hybrid_email_detector.analyze(content, use_hybrid=True)
            return threat_level, confidence, features, recommendations
        else:
            # Standard analysis (backward compatible)
            return self.email_detector.analyze(content)
    
    def analyze_email_hybrid(self, content: str) -> Tuple[str, float, List[str], List[str], Optional[List[Dict]], Dict]:
        """
        Analyze email using hybrid approach (text + URL split analysis)
        
        This method:
        1. Extracts URLs from email content
        2. Analyzes text (without URLs) using email phishing model
        3. Analyzes each URL using URL phishing model
        4. Combines results intelligently
        
        Args:
            content: Email content to analyze
            
        Returns:
            Tuple of (threat_level, confidence, features, recommendations, url_analysis_results)
            
        Note: url_analysis_results contains detailed analysis for each URL found
        """
        return self.hybrid_email_detector.analyze(content, use_hybrid=True)
    
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
