"""
URL Feature Extractor - 23 features for RandomForest classifier
Trained on 822K URLs (94.6% accuracy, binary: legitimate/phishing)
"""

import re
import math
from urllib.parse import urlparse
from tld import get_tld


def normalize_url(url):
    """Ensure URL has a protocol so urlparse works correctly."""
    url = str(url).strip()
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    return url


def extract_url_features(url):
    """
    Extract 23 URL features as a dict for the phishing detection model.
    Keys match the trained model's feature names exactly.
    """
    url = normalize_url(url)
    tld = get_tld(url, fail_silently=True)

    try:
        parsed = urlparse(url)
    except Exception:
        parsed = None

    # --- helper lambdas ---
    def _hostname():
        try:
            return urlparse(url).hostname or ''
        except Exception:
            return ''

    def _netloc():
        try:
            return urlparse(url).netloc
        except Exception:
            return ''

    def _path():
        try:
            return urlparse(url).path
        except Exception:
            return ''

    hostname = _hostname()
    netloc = _netloc()
    path = _path()

    # 1. IP address in URL
    ip_match = re.search(
        r'(([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.'
        r'([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\/)|'
        r'((0x[0-9a-fA-F]{1,2})\.(0x[0-9a-fA-F]{1,2})\.(0x[0-9a-fA-F]{1,2})\.(0x[0-9a-fA-F]{1,2})\/)'
        r'(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}', url)
    use_of_ip = 1 if ip_match else 0

    # 2-5. Character counts
    count_dot = url.count('.')
    count_at = url.count('@')
    count_dir = path.count('/')
    count_embed = path.count('//')

    # 6. URL shortener
    shortener_match = re.search(
        r'bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|'
        r'yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|'
        r'short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|'
        r'doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|lnkd\.in|'
        r'db\.tt|qr\.ae|adf\.ly|bitly\.com|cur\.lv|tinyurl\.com|ity\.im|'
        r'q\.gs|po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|'
        r'prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|'
        r'link\.zip\.net', url)
    short_url = 1 if shortener_match else 0

    # 7-10. More character counts
    count_pct = url.count('%')
    count_ques = url.count('?')
    count_hyphen = url.count('-')
    count_equal = url.count('=')

    # 11-12. Length features
    url_length = len(url)
    hostname_length = len(netloc)

    # 13. Suspicious words
    sus_match = re.search(
        r'PayPal|login|signin|bank|account|update|free|lucky|service|bonus|ebayisapi|webscr',
        url, re.IGNORECASE)
    sus_url = 1 if sus_match else 0

    # 14. First directory length
    try:
        fd_length = len(path.split('/')[1])
    except Exception:
        fd_length = 0

    # 15-16. Digit and letter counts
    count_digits = sum(c.isnumeric() for c in url)
    count_letters = sum(c.isalpha() for c in url)

    # 17. TLD length
    tld_length = len(tld) if tld else -1

    # 18. HTTPS flag
    is_https = 1 if url.startswith('https://') else 0

    # 19. Subdomain count
    host_parts = hostname.split('.') if hostname else []
    subdomain_count = max(0, len(host_parts) - 2)

    # 20. Path length
    path_length = len(path)

    # 21. Domain entropy (Shannon)
    domain_entropy = 0.0
    if hostname:
        freq = {}
        for c in hostname:
            freq[c] = freq.get(c, 0) + 1
        for count in freq.values():
            p = count / len(hostname)
            domain_entropy -= p * math.log2(p)
        domain_entropy = round(domain_entropy, 4)

    # 22. Special character ratio
    if url:
        specials = sum(not c.isalnum() for c in url)
        special_char_ratio = round(specials / len(url), 4)
    else:
        special_char_ratio = 0.0

    # 23. Risky TLD
    RISKY_TLDS = {'tk', 'ml', 'ga', 'cf', 'gq', 'xyz', 'top', 'pw', 'cc',
                  'buzz', 'work', 'click', 'link', 'info', 'online', 'site',
                  'club', 'icu', 'live', 'stream'}
    tld_risk = 1 if (tld and tld.lower() in RISKY_TLDS) else 0

    return {
        'use_of_ip': use_of_ip,
        'count.': count_dot,
        'count@': count_at,
        'count_dir': count_dir,
        'count_embed_domian': count_embed,
        'short_url': short_url,
        'count%': count_pct,
        'count?': count_ques,
        'count-': count_hyphen,
        'count=': count_equal,
        'url_length': url_length,
        'hostname_length': hostname_length,
        'sus_url': sus_url,
        'fd_length': fd_length,
        'count-digits': count_digits,
        'count-letters': count_letters,
        'tld_length': tld_length,
        'is_https': is_https,
        'subdomain_count': subdomain_count,
        'path_length': path_length,
        'domain_entropy': domain_entropy,
        'special_char_ratio': special_char_ratio,
        'tld_risk': tld_risk,
    }
