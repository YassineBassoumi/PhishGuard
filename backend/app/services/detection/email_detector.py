"""
Email Phishing Detector
ML-powered email/message phishing detection using LinearSVC + TF-IDF

Model: LinearSVC trained on 19,741 emails (97.5% accuracy)
Label convention: 1 = Phishing, 0 = Safe/Legitimate
"""

import math
import re
from typing import Tuple, List, Dict, Any
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
        """Analyze message content for phishing patterns. Returns 4-tuple (backward compatible)."""
        threat, conf, feat, rec, _ = self.analyze_with_trace(content)
        return threat, conf, feat, rec

    def analyze_with_trace(self, content: str) -> Tuple[str, float, List[str], List[str], Dict[str, Any]]:
        """
        Same as analyze() but also returns a decision trace dict explaining
        what the raw ML model predicted vs. what rules decided.
        """
        content_lower = content.lower()
        model = model_loader.email_model
        vectorizer = model_loader.email_vectorizer

        if model is not None and vectorizer is not None:
            try:
                return self._ml_analysis(content, content_lower, model, vectorizer)
            except Exception as e:
                print(f"Error during ML prediction: {e}")
                return self._rule_based_analysis(content, content_lower)
        else:
            return self._rule_based_analysis(content, content_lower)
    
    @staticmethod
    def _sigmoid_confidence(decision_value: float) -> float:
        """
        Convert LinearSVC decision_function value to a 0-100 confidence score.
        
        decision_function output:
          positive → leans class 1 (phishing), negative → leans class 0 (safe)
          magnitude = distance from hyperplane (higher = more certain)
        """
        prob = 1.0 / (1.0 + math.exp(-decision_value))
        # prob ∈ (0,1): >0.5 = phishing, <0.5 = safe
        # Confidence = certainty about the *predicted* class
        return float(max(prob, 1.0 - prob) * 100)

    def _ml_analysis(self, content: str, content_lower: str, model, vectorizer) -> Tuple[str, float, List[str], List[str], Dict[str, Any]]:
        """
        Perform ML-based analysis (LinearSVC + TF-IDF)
        
        Args:
            content: Original email content
            content_lower: Lowercase email content
            model: Trained classifier
            vectorizer: Fitted TF-IDF vectorizer
            
        Returns:
            Tuple of (threat_level, confidence, features, recommendations)
        """
        # Transform content
        content_tfidf = vectorizer.transform([content_lower])
        
        # Get prediction  (1 = phishing, 0 = safe)
        prediction = model.predict(content_tfidf)[0]
        
        # Get confidence score
        try:
            probability = model.predict_proba(content_tfidf)[0]
            ml_confidence = float(probability[prediction] * 100)
        except AttributeError:
            # LinearSVC — use decision_function → sigmoid mapping
            try:
                decision = model.decision_function(content_tfidf)[0]
                ml_confidence = self._sigmoid_confidence(decision)
            except Exception:
                ml_confidence = 85.0
        
        # Extract features (ML signals + rule-based) for user-facing feedback
        features = extract_email_features(content, content_lower, model, vectorizer, prediction)
        
        # Get rule-based threat score for hybrid boost
        rule_score, _ = calculate_rule_based_threat_score(content, content_lower)
        
        # ── Determine threat level ───────────────────────────────────────
        # Label convention: 1 = Phishing, 0 = Safe
        if prediction == 1:  # ML says phishing
            if ml_confidence >= 85 or rule_score >= 30:
                threat_level = "dangerous"
                rule_fired = "ML=phishing + (confidence>=85% OU rule_score>=30) → DANGEROUS"
            elif ml_confidence >= 70:
                threat_level = "suspicious"
                rule_fired = "ML=phishing + confidence>=70% → SUSPICIOUS"
            else:
                threat_level = "suspicious"
                rule_fired = "ML=phishing + confidence<70% → SUSPICIOUS (par défaut)"
        else:  # ML says safe
            if rule_score >= 50:
                threat_level = "suspicious"
                rule_fired = "ML=safe MAIS rule_score>=50 → SUSPICIOUS (les règles ont surclassé l'IA)"
            elif rule_score <= 10 and ml_confidence >= 65:
                threat_level = "safe"
                rule_fired = "ML=safe + rule_score<=10 + confidence>=65% → SAFE (les deux d'accord)"
            elif ml_confidence >= 80:
                threat_level = "safe"
                rule_fired = "ML=safe + confidence>=80% → SAFE (l'IA très confiante)"
            elif rule_score >= 25:
                threat_level = "suspicious"
                rule_fired = "ML=safe MAIS rule_score>=25 → SUSPICIOUS (signaux de règles modérés)"
            else:
                threat_level = "safe"
                rule_fired = "ML=safe + rule_score<25 → SAFE"

        confidence = ml_confidence

        trace = {
            "ml_prediction": "phishing" if prediction == 1 else "safe",
            "ml_confidence": round(float(ml_confidence), 2),
            "rule_score": int(rule_score),
            "verdict": threat_level,
            "reason": rule_fired,
            "ml_overridden": (prediction == 0 and threat_level != "safe") or (prediction == 1 and threat_level == "safe"),
        }
        
        # Build context for smart recommendations
        urls = re.findall(r'http[s]?://[^\s<>"\']+', content)
        email_context = {
            'has_urgency': any(w in content_lower for w in ['urgent', 'immediate', 'act now', 'expire', 'suspended']),
            'has_credentials': any(w in content_lower for w in ['password', 'username', 'login', 'credential', 'ssn']),
            'has_financial': any(w in content_lower for w in ['refund', 'prize', 'won', 'lottery', 'bank account', 'transfer']),
            'has_urls': len(urls) > 0,
            'has_suspicious_tld': any(tld in content_lower for tld in ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top']),
            'has_typosquatting': any(b in content_lower for b in ['paypa1', 'g00gle', 'micros0ft', 'amazom', 'app1e']),
        }
        
        # Generate context-aware recommendations
        recommendations = generate_recommendations(threat_level, is_url=False, email_context=email_context)
        
        return threat_level, confidence, features, recommendations, trace

    def _rule_based_analysis(self, content: str, content_lower: str) -> Tuple[str, float, List[str], List[str], Dict[str, Any]]:
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

        trace = {
            "ml_prediction": "unavailable",
            "ml_confidence": 0.0,
            "rule_score": int(threat_score),
            "verdict": threat_level,
            "reason": f"Modèle ML indisponible - analyse par règles uniquement (score={threat_score})",
            "ml_overridden": False,
        }

        return threat_level, float(confidence), features, recommendations, trace
