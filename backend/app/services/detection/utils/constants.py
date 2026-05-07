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
    'twitter.com', 'x.com', 'linkedin.com', 'instagram.com', 'youtube.com', 'reddit.com',
    'discord.com', 'tiktok.com', 'pinterest.com', 'snapchat.com', 'tumblr.com',
    # Email providers
    'gmail.com', 'outlook.com', 'yahoo.com', 'protonmail.com', 'icloud.com',
    # Financial services
    'paypal.com', 'stripe.com', 'square.com', 'wise.com', 'revolut.com',
    # E-commerce & travel
    'ebay.com', 'shopify.com', 'etsy.com', 'aliexpress.com', 'booking.com',
    'airbnb.com', 'tripadvisor.com', 'expedia.com',
    # Cloud & hosting
    'github.com', 'gitlab.com', 'bitbucket.org', 'cloudflare.com', 'aws.amazon.com',
    'azure.microsoft.com', 'cloud.google.com', 'vercel.com', 'netlify.com', 'heroku.com',
    # Development tools
    'stackoverflow.com', 'npmjs.com', 'pypi.org', 'docker.com', 'python.org',
    'nodejs.org', 'rust-lang.org', 'php.net', 'rubygems.org', 'crates.io',
    # News & media
    'bbc.com', 'bbc.co.uk', 'nytimes.com', 'theguardian.com', 'reuters.com',
    'cnn.com', 'washingtonpost.com', 'lemonde.fr', 'lefigaro.fr',
    # Education & reference
    'wikipedia.org', 'medium.com', 'coursera.org', 'udemy.com', 'khanacademy.org',
    'edx.org', 'academia.edu', 'researchgate.net',
    # AI Services
    'openai.com', 'chat.openai.com', 'deepseek.com', 'chat.deepseek.com', 'anthropic.com',
    'claude.ai', 'bard.google.com', 'gemini.google.com', 'perplexity.ai', 'huggingface.co',
    # Music & Entertainment
    'spotify.com', 'netflix.com', 'twitch.tv', 'soundcloud.com', 'hulu.com',
    'disneyplus.com', 'primevideo.com', 'hbomax.com', 'deezer.com',
    # Productivity
    'notion.so', 'trello.com', 'slack.com', 'zoom.us', 'dropbox.com', 'drive.google.com',
    'docs.google.com', 'office.com', 'teams.microsoft.com', 'figma.com', 'canva.com',
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
