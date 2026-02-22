"""
Email Phishing Detector
ML-powered email phishing detection
"""

from typing import Tuple, List
from .models import model_loader
from .feature_extractors import extract_email_features, calculate_rule_based_threat_score
from .utils import generate_recommendations


class EmailDetector:
    """Email phishing detection service"""
    
    def __init__(self):
        """Initialize email detector"""
        # Models are loaded lazily through model_loader
        pass
    
    def analyze(self, content: str) -> Tuple[str, float, List[str], List[str]]:
        """
        Analyze email content for phishing patterns using ML model
        
        Args:
            content: Email content to analyze
            
        Returns:
            Tuple of (threat_level, confidence, features, recommendations)
        """
        # Preprocess content
        content_lower = content.lower()
        
        # Get ML prediction if model is available
        model = model_loader.email_model
        vectorizer = model_loader.email_vectorizer
        
        if model is not None and vectorizer is not None:
            try:
                return self._ml_analysis(content, content_lower, model, vectorizer)
            except Exception as e:
                print(f"Error during ML prediction: {e}")
                # Fallback to rule-based
                return self._rule_based_analysis(content, content_lower)
        else:
            # Fallback to rule-based detection
            return self._rule_based_analysis(content, content_lower)
    
    def _ml_analysis(self, content: str, content_lower: str, model, vectorizer) -> Tuple[str, float, List[str], List[str]]:
        """
        Perform ML-based analysis
        
        Args:
            content: Original email content
            content_lower: Lowercase email content
            model: ML model
            vectorizer: Text vectorizer
            
        Returns:
            Tuple of (threat_level, confidence, features, recommendations)
        """
        # Transform content using the vectorizer
        content_tfidf = vectorizer.transform([content_lower])
        
        # Get prediction
        prediction = model.predict(content_tfidf)[0]
        
        # Try to get probability if available
        try:
            probability = model.predict_proba(content_tfidf)[0]
            ml_confidence = float(probability[prediction] * 100)
        except AttributeError:
            # Model doesn't support predict_proba
            try:
                decision = model.decision_function(content_tfidf)[0]
                # Convert decision function to confidence (0-100)
                ml_confidence = min(95.0, max(60.0, 75.0 + abs(decision) * 10))
            except:
                ml_confidence = 85.0  # Default confidence
        
        # Determine threat level based on ML prediction
        # Note: prediction 0 = Spam, 1 = Ham (based on spamEmails model)
        if prediction == 0:  # Spam/Phishing
            if ml_confidence >= 90:
                threat_level = "dangerous"
            elif ml_confidence >= 70:
                threat_level = "suspicious"
            else:
                threat_level = "suspicious"
        else:  # Ham/Legitimate
            threat_level = "safe"
        
        confidence = ml_confidence
        
        # Extract rule-based features for detailed feedback
        features = extract_email_features(content, content_lower)
        
        # Generate recommendations
        recommendations = generate_recommendations(threat_level, is_url=False)
        
        return threat_level, confidence, features, recommendations
    
    def _rule_based_analysis(self, content: str, content_lower: str) -> Tuple[str, float, List[str], List[str]]:
        """
        Fallback rule-based analysis when ML model is unavailable
        
        Args:
            content: Original email content
            content_lower: Lowercase email content
            
        Returns:
            Tuple of (threat_level, confidence, features, recommendations)
        """
        threat_score, features = calculate_rule_based_threat_score(content, content_lower)
        
        # Determine threat level and confidence
        if threat_score >= 50:
            threat_level = "dangerous"
            confidence = min(95.0, 70 + threat_score // 3)
        elif threat_score >= 25:
            threat_level = "suspicious"
            confidence = min(85.0, 60 + threat_score // 2)
        else:
            threat_level = "safe"
            confidence = 80.0
        
        recommendations = generate_recommendations(threat_level, is_url=False)
        
        return threat_level, float(confidence), features, recommendations
