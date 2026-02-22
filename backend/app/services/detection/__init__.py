"""
PhishGuard Detection Module
Modular phishing detection system with ML and rule-based analysis
"""

from .email_detector import EmailDetector
from .url_detector import URLDetector
from .models import model_loader
from .utils import generate_recommendations

__all__ = [
    'EmailDetector',
    'URLDetector',
    'model_loader',
    'generate_recommendations'
]

__version__ = '2.0.0'
