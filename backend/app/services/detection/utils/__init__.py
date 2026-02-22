"""
Detection Utilities
"""

from .constants import (
    PHISHING_KEYWORDS,
    SUSPICIOUS_TLDS,
    LEGITIMATE_DOMAINS,
    URGENCY_WORDS,
    CREDENTIAL_KEYWORDS,
    FINANCIAL_KEYWORDS,
    URL_PHISHING_PATTERNS,
    TYPO_BRANDS,
    URL_SHORTENERS,
    BRAND_NAMES,
    URL_PHISHING_KEYWORDS
)
from .recommendations import generate_recommendations

__all__ = [
    'PHISHING_KEYWORDS',
    'SUSPICIOUS_TLDS',
    'LEGITIMATE_DOMAINS',
    'URGENCY_WORDS',
    'CREDENTIAL_KEYWORDS',
    'FINANCIAL_KEYWORDS',
    'URL_PHISHING_PATTERNS',
    'TYPO_BRANDS',
    'URL_SHORTENERS',
    'BRAND_NAMES',
    'URL_PHISHING_KEYWORDS',
    'generate_recommendations'
]
