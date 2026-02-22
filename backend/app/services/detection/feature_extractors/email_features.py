"""
Email Feature Extractor
Extracts features from email content for analysis
"""

import re
from typing import List
from ..utils.constants import (
    PHISHING_KEYWORDS,
    SUSPICIOUS_TLDS,
    URGENCY_WORDS,
    CREDENTIAL_KEYWORDS,
    FINANCIAL_KEYWORDS
)


def extract_email_features(content: str, content_lower: str) -> List[str]:
    """
    Extract rule-based features from email content for detailed user feedback
    
    Args:
        content: Original email content
        content_lower: Lowercase version of email content
        
    Returns:
        List of detected threat indicators
    """
    threat_indicators = []
    
    # Check for phishing keywords
    found_keywords = [kw for kw in PHISHING_KEYWORDS if kw in content_lower]
    if found_keywords:
        threat_indicators.append(f"Phishing keywords detected: {', '.join(found_keywords[:3])}")
    
    # Check for suspicious URLs
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
    if urls:
        # Check for suspicious domains
        has_suspicious_domain = False
        for url in urls:
            if any(tld in url for tld in SUSPICIOUS_TLDS):
                threat_indicators.append("Suspicious domain TLD detected")
                has_suspicious_domain = True
                break
        
        # Only mention links if they're suspicious or there are many
        if has_suspicious_domain or len(urls) > 3:
            threat_indicators.append(f"Contains {len(urls)} embedded link(s)")
    
    # Check for urgency language
    if any(word in content_lower for word in URGENCY_WORDS):
        threat_indicators.append("Urgency language detected")
    
    # Check for credential requests
    if any(word in content_lower for word in CREDENTIAL_KEYWORDS):
        threat_indicators.append("Requests sensitive information")
    
    # Check for financial indicators
    if any(word in content_lower for word in FINANCIAL_KEYWORDS):
        threat_indicators.append("Financial/monetary language detected")
    
    # Check for suspicious patterns
    if re.search(r'\d[a-z]\d|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', content_lower):
        threat_indicators.append("Suspicious character patterns detected")
    
    # Return threat indicators if found, otherwise positive message
    if threat_indicators:
        return threat_indicators
    else:
        return [
            "No phishing indicators detected",
            "Email structure appears normal",
            "Sender patterns look legitimate"
        ]


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
        features.append(f"Phishing keywords detected: {', '.join(found_keywords[:3])}")
        threat_score += len(found_keywords) * 10
    
    # Check for suspicious URLs
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
    if urls:
        features.append(f"Contains {len(urls)} embedded link(s)")
        threat_score += len(urls) * 15
        
        for url in urls:
            if any(tld in url for tld in SUSPICIOUS_TLDS):
                features.append("Suspicious domain TLD detected")
                threat_score += 20
    
    # Check for urgency
    if any(word in content_lower for word in URGENCY_WORDS):
        features.append("Urgency language detected")
        threat_score += 15
    
    # Check for credential requests
    if any(word in content_lower for word in CREDENTIAL_KEYWORDS):
        features.append("Requests sensitive information")
        threat_score += 20
    
    if not features:
        features.append("No obvious phishing indicators detected")
    
    return threat_score, features
