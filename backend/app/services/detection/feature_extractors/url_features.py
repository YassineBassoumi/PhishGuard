"""
URL Feature Extractor - UPDATED to match retrained model
Extracts exactly 12 features matching the Colab training notebook
"""

import ipaddress
from urllib.parse import urlparse


def extract_url_features(url):
    """
    Extract 12 URL features matching the retrained model
    This MUST match the training code exactly for accurate predictions
    """
    features = []
    
    try:
        parsed = urlparse(url.strip())
        hostname = parsed.netloc.lower().replace('www.', '')
        path = parsed.path.lower()
        full_url = url.lower()
        
        # 1. IP Address (but allow private IPs)
        try:
            ip = ipaddress.ip_address(hostname.split(':')[0])  # Remove port if present
            # Check if it's a private IP (192.168.x.x, 10.x.x.x, 172.16-31.x.x, 127.x.x.x)
            if ip.is_private or ip.is_loopback:
                features.append(1)  # Private IPs are safe (local network)
            else:
                features.append(-1)  # Public IPs are suspicious
        except:
            features.append(1)
        
        # 2. URL Length
        length = len(url)
        features.append(1 if length < 54 else 0 if length <= 75 else -1)
        
        # 3. URL Shortener - EXACT MATCH ONLY
        shorteners = [
            'bit.ly', 'goo.gl', 'tinyurl.com', 't.co', 'ow.ly', 'is.gd', 
            'buff.ly', 'rb.gy', 'short.link', 'tiny.cc', 'tr.im', 
            'shorturl.at', 'cutt.ly', 'short.io', 't.ly', 'bitly.com', 
            'rebrand.ly', 'short.cm', 'gear.id', 'short.gy', 'clck.ru',
            'tiny.one', 'link.to', 'soo.gd', 'v.gd', 'lnkd.in', 'tinycc.com',
            'shorte.st', 'go2l.ink', 'x.co', 'yfrog.com', 'migre.me',
            'ff.im', 'url4.eu', 'twit.ac', 'su.pr', 'twurl.nl', 'snipurl.com',
            'short.to', 'budurl.com', 'ping.fm', 'post.ly', 'just.as',
            'bkite.com', 'snipr.com', 'fic.kr', 'loopt.us', 'doiop.com',
            'short.ie', 'kl.am', 'wp.me', 'rubyurl.com', 'om.ly', 'to.ly',
            'bit.do', 'db.tt', 'qr.ae', 'adf.ly', 'cur.lv', 'ity.im',
            'q.gs', 'po.st', 'bc.vc', 'twitthis.com', 'u.to', 'j.mp',
            'buzurl.com', 'cutt.us', 'u.bb', 'yourls.org', 'prettylinkpro.com',
            'scrnch.me', 'vzturl.com', 'qr.net', '1url.com', 'tweez.me',
            'link.zip.net'
        ]
        # Only match if hostname exactly matches or ends with the shortener domain
        is_shortener = any(
            hostname == s or hostname.endswith('.' + s)
            for s in shorteners
        )
        features.append(-1 if is_shortener else 1)
        
        # 4. @ Symbol
        features.append(-1 if '@' in url else 1)
        
        # 5. Double slash redirecting
        features.append(-1 if url.find('//', 8) > -1 else 1)
        
        # 6. Dash in domain
        features.append(0 if '-' in hostname else 1)
        
        # 7. Subdomain dots
        dots = hostname.count('.')
        features.append(1 if dots == 1 else 0 if dots == 2 else -1)
        
        # 8. HTTPS
        features.append(1 if parsed.scheme == 'https' else -1)
        
        # 9. Non-standard port
        features.append(-1 if parsed.port and parsed.port not in [80, 443] else 1)
        
        # 10. Suspicious keywords in domain
        suspicious = [
            'verify', 'secure', 'account', 'update', 'confirm', 
            'banking', 'password', 'wallet', 'login', 'signin',
            'reset', 'billing', 'payment', 'suspended', 'locked',
            'verification', 'authenticate', 'credential', 'authorize'
        ]
        features.append(-1 if any(w in hostname for w in suspicious) else 1)
        
        # 11. Subdomain parts
        parts = len(hostname.split('.'))
        features.append(1 if parts == 2 else 0 if parts == 3 else -1)
        
        # 12. Suspicious TLD
        bad_tlds = ['.tk', '.ml', '.ga', '.cf', '.top', '.xyz', '.work', '.gq', 
                    '.info', '.click', '.link', '.download', '.stream', '.science',
                    '.party', '.review', '.trade', '.webcam', '.win', '.bid']
        features.append(-1 if any(hostname.endswith(t) for t in bad_tlds) else 1)
        
    except Exception as e:
        # Return neutral features on error
        features = [0] * 12
    
    return features


# Legacy class for backward compatibility
class URLFeatureExtractor:
    """Legacy wrapper - use extract_url_features() function instead"""
    
    def __init__(self, url):
        self.url = url
    
    def extract_features(self):
        """Extract 12 features (new model format)"""
        return extract_url_features(self.url)
