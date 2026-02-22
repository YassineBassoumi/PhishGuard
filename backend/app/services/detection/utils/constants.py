"""
Detection Constants
Common constants used across detection modules
"""

# Phishing keywords for rule-based feature detection
PHISHING_KEYWORDS = [
    'verify', 'urgent', 'suspended', 'locked', 'confirm',
    'click here', 'account', 'password', 'update', 'expire',
    'security', 'act now', 'immediate', 'validate', 'unusual activity'
]

# Suspicious TLDs
SUSPICIOUS_TLDS = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top']

# Legitimate domains whitelist (prevents false positives on well-known sites)
# This is a safety net for rule-based fallback and edge cases
LEGITIMATE_DOMAINS = [
    # Major tech companies
    'google.com', 'microsoft.com', 'apple.com', 'amazon.com', 'meta.com', 'facebook.com',
    # Social media & communication
    'twitter.com', 'linkedin.com', 'instagram.com', 'youtube.com', 'reddit.com', 'discord.com',
    # Email providers
    'gmail.com', 'outlook.com', 'yahoo.com', 'protonmail.com',
    # Financial services
    'paypal.com', 'stripe.com', 'square.com',
    # E-commerce
    'ebay.com', 'shopify.com', 'etsy.com',
    # Cloud & hosting
    'github.com', 'gitlab.com', 'bitbucket.org', 'cloudflare.com', 'aws.amazon.com',
    # Development tools
    'stackoverflow.com', 'npmjs.com', 'pypi.org', 'docker.com',
    # Education & reference
    'wikipedia.org', 'medium.com', 'coursera.org', 'udemy.com'
]

# Urgency words for email analysis
URGENCY_WORDS = ['urgent', 'immediate', 'act now', 'expire', 'suspended']

# Credential request keywords
CREDENTIAL_KEYWORDS = ['password', 'username', 'login', 'credential', 'ssn', 'social security']

# Financial keywords
FINANCIAL_KEYWORDS = ['refund', 'prize', 'won', 'lottery', 'million', 'transfer', 'bank account']

# URL phishing patterns
URL_PHISHING_PATTERNS = ['paypal', 'login', 'verify', 'account', 'secure', 'update']

# Typosquatting brands
TYPO_BRANDS = ['paypa1', 'g00gle', 'micros0ft', 'amazom', 'app1e']

# URL shorteners
URL_SHORTENERS = ['bit.ly', 'goo.gl', 'tinyurl', 't.co', 'ow.ly', 'is.gd']

# Brand names for detection
BRAND_NAMES = ['google', 'facebook', 'microsoft', 'apple', 'amazon', 'paypal', 'netflix']

# Phishing keywords for URL analysis
URL_PHISHING_KEYWORDS = [
    'login', 'signin', 'account', 'verify', 'secure', 'update',
    'confirm', 'banking', 'paypal', 'ebay', 'amazon'
]
