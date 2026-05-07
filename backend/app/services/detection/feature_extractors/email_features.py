"""
Email Feature Extractor
Extracts features from email content for analysis

Combines rule-based pattern matching with ML model signals
to provide accurate, explainable threat indicators.
"""

import re
import numpy as np
from typing import List, Dict, Optional, Any
from ..utils.constants import (
    PHISHING_KEYWORDS,
    SUSPICIOUS_TLDS,
    URGENCY_WORDS,
    CREDENTIAL_KEYWORDS,
    FINANCIAL_KEYWORDS,
    TYPO_BRANDS,
    BRAND_NAMES
)


def extract_email_features(
    content: str,
    content_lower: str,
    model: Optional[Any] = None,
    vectorizer: Optional[Any] = None,
    prediction: Optional[int] = None
) -> List[str]:
    """
    Extract features from email content for detailed user feedback.
    
    Combines rule-based pattern matching with ML model signals
    (top TF-IDF words) to explain why the model flagged or cleared the email.
    
    Args:
        content: Original email content
        content_lower: Lowercase version of email content
        model: Trained ML model (optional, for TF-IDF signal extraction)
        vectorizer: Fitted TF-IDF vectorizer (optional)
        prediction: ML prediction 1=phishing, 0=safe (optional)
        
    Returns:
        List of detected threat indicators
    """
    threat_indicators = []
    
    # ── ML model signals (top words that influenced the decision) ─────
    if model is not None and vectorizer is not None and prediction is not None:
        ml_signals = _extract_ml_signals(content_lower, model, vectorizer, prediction)
        if ml_signals:
            threat_indicators.extend(ml_signals)
    
    # ── Rule-based pattern detection ──────────────────────────────────
    # Check for phishing keywords
    found_keywords = [kw for kw in PHISHING_KEYWORDS if kw in content_lower]
    if found_keywords:
        threat_indicators.append(f"Mots-clés de phishing détectés : {', '.join(found_keywords[:3])}")
    
    # Check for suspicious URLs
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
    if urls:
        # Check for suspicious domains
        has_suspicious_domain = False
        for url in urls:
            if any(tld in url for tld in SUSPICIOUS_TLDS):
                threat_indicators.append("TLD de domaine suspect détecté")
                has_suspicious_domain = True
                break
        
        # Only mention links if they're suspicious or there are many
        if has_suspicious_domain or len(urls) > 3:
            threat_indicators.append(f"Contient {len(urls)} lien(s) intégré(s)")
    
    # Check for urgency language
    found_urgency = [w for w in URGENCY_WORDS if w in content_lower]
    if found_urgency:
        threat_indicators.append("Langage urgent détecté")
    
    # Check for credential requests
    found_credentials = [w for w in CREDENTIAL_KEYWORDS if w in content_lower]
    if found_credentials:
        threat_indicators.append("Demande d'informations sensibles")
    
    # Check for financial indicators
    found_financial = [w for w in FINANCIAL_KEYWORDS if w in content_lower]
    if found_financial:
        threat_indicators.append("Langage financier/monétaire détecté")
    
    # Check for typosquatting (brand impersonation)
    found_typos = [b for b in TYPO_BRANDS if b in content_lower]
    if found_typos:
        threat_indicators.append(f"Usurpation de marque détectée : {', '.join(found_typos[:2])}")
    
    # Check for suspicious patterns (IP addresses, mixed chars)
    if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', content_lower):
        threat_indicators.append("Adresse IP détectée dans le contenu")
    
    # Return threat indicators if found, otherwise positive message
    if threat_indicators:
        return threat_indicators
    else:
        return [
            "Aucun indicateur de phishing détecté",
            "La structure de l'email semble normale",
            "Les modèles de l'expéditeur semblent légitimes"
        ]


def _extract_ml_signals(
    content_lower: str,
    model: Any,
    vectorizer: Any,
    prediction: int,
    top_n: int = 5
) -> List[str]:
    """
    Extract top TF-IDF words that influenced the model's decision.
    
    For LinearSVC: uses model.coef_ to find the most impactful words
    in the email that pushed the prediction toward phishing or safe.
    """
    try:
        content_tfidf = vectorizer.transform([content_lower])
        feature_names = vectorizer.get_feature_names_out()
        
        # Get model coefficients (word importance for phishing class)
        if hasattr(model, 'coef_'):
            coefs = model.coef_[0]
        else:
            return []
        
        # Get TF-IDF values for this email
        tfidf_values = content_tfidf.toarray()[0]
        
        # Word impact = TF-IDF value × coefficient
        # Positive impact → pushes toward phishing, negative → safe
        word_impacts = tfidf_values * coefs
        
        # Get non-zero impacts
        nonzero = np.nonzero(word_impacts)[0]
        if len(nonzero) == 0:
            return []
        
        if prediction == 1:  # Phishing
            # Top words pushing toward phishing (positive impact)
            top_idx = nonzero[np.argsort(word_impacts[nonzero])[-top_n:]]
            top_idx = top_idx[word_impacts[top_idx] > 0]
            if len(top_idx) > 0:
                top_words = [feature_names[i] for i in top_idx]
                return [f"Termes suspects détectés par l'IA : {', '.join(top_words)}"]
        else:  # Safe
            # Top words pushing toward safe (negative impact)
            top_idx = nonzero[np.argsort(word_impacts[nonzero])[:top_n]]
            top_idx = top_idx[word_impacts[top_idx] < 0]
            if len(top_idx) > 0:
                top_words = [feature_names[i] for i in top_idx]
                return [f"Termes légitimes détectés par l'IA : {', '.join(top_words)}"]
        
        return []
    except Exception:
        return []


def calculate_rule_based_threat_score(content: str, content_lower: str) -> tuple[int, List[str]]:
    """
    Calculate threat score based on rule-based analysis
    
    Args:
        content: Original email content
        content_lower: Lowercase version of email content
        
    Returns:
        Tuple of (threat_score, features_list)
    """
    features = []
    threat_score = 0
    
    # Check for phishing keywords
    found_keywords = [kw for kw in PHISHING_KEYWORDS if kw in content_lower]
    if found_keywords:
        features.append(f"Mots-clés de phishing détectés : {', '.join(found_keywords[:3])}")
        threat_score += len(found_keywords) * 10
    
    # Check for suspicious URLs
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
    if urls:
        features.append(f"Contient {len(urls)} lien(s) intégré(s)")
        threat_score += len(urls) * 15
        
        for url in urls:
            if any(tld in url for tld in SUSPICIOUS_TLDS):
                features.append("TLD de domaine suspect détecté")
                threat_score += 20
    
    # Check for urgency
    if any(word in content_lower for word in URGENCY_WORDS):
        features.append("Langage urgent détecté")
        threat_score += 15
    
    # Check for credential requests
    if any(word in content_lower for word in CREDENTIAL_KEYWORDS):
        features.append("Demande d'informations sensibles")
        threat_score += 20
    
    if not features:
        features.append("Aucun indicateur de phishing évident détecté")
    
    return threat_score, features
