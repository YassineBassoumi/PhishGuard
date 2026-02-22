"""
URL Phishing Detector
ML-powered URL phishing detection with multiple detection methods
"""

import re
import random
import numpy as np
import ipaddress
from typing import Tuple, List
from urllib.parse import urlparse

from .models import model_loader
from .feature_extractors import extract_url_features
from .utils import (
    generate_recommendations,
    SUSPICIOUS_TLDS,
    LEGITIMATE_DOMAINS,
    URL_PHISHING_PATTERNS,
    TYPO_BRANDS,
    URL_SHORTENERS
)


class URLDetector:
    """URL phishing detection service"""
    
    def __init__(self):
        """Initialize URL detector"""
        # Models are loaded lazily through model_loader
        pass
    
    def analyze(self, url: str) -> Tuple[str, float, List[str], List[str]]:
        """
        Analyze URL for malicious indicators using ML model
        
        Args:
            url: URL to analyze
            
        Returns:
            Tuple of (threat_level, confidence, features, recommendations)
        """
        # Try Phishing-URL-Detection model first (most accurate)
        if model_loader.phishing_url_model is not None:
            try:
                return self._phishing_url_analysis(url)
            except Exception as e:
                print(f"Error with phishing URL model: {e}, trying alternative")
        
        # Fallback to custom ML model
        if model_loader.url_model is not None and model_loader.url_feature_names is not None:
            try:
                return self._ml_url_analysis_v2(url)
            except Exception as e:
                print(f"Error during ML URL analysis: {e}, falling back to rule-based")
        
        # Final fallback to rule-based detection
        return self._rule_based_analysis(url)
    
    def _phishing_url_analysis(self, url: str) -> Tuple[str, float, List[str], List[str]]:
        """
        Analyze URL using retrained model (12 features) - matches training code exactly
        
        Args:
            url: URL to analyze
            
        Returns:
            Tuple of (threat_level, confidence, features, recommendations)
        """
        # Check for private/local IPs first (these are safe by definition)
        try:
            parsed = urlparse(url)
            hostname = parsed.netloc.split(':')[0]  # Remove port
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback:
                return "safe", 95.0, [
                    "Private/local IP address detected",
                    "This is a local network resource (router, device, etc.)",
                    "Not accessible from the internet"
                ], [
                    "This appears to be a local network device",
                    "Ensure you trust the local network you're connected to",
                    "Private IPs are not phishing sites"
                ]
        except:
            pass  # Not an IP address, continue with normal analysis
        
        # Check whitelist for known legitimate domains (prevents false positives)
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove port and www prefix for comparison
            domain = domain.split(':')[0]
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Check if domain or parent domain is in whitelist
            for legitimate_domain in LEGITIMATE_DOMAINS:
                if domain == legitimate_domain or domain.endswith('.' + legitimate_domain):
                    return "safe", 98.0, [
                        f"Verified legitimate domain: {legitimate_domain}",
                        "Domain is in trusted whitelist",
                        "No phishing indicators detected"
                    ], [
                        "This is a known legitimate website",
                        "Always verify the exact URL matches the official domain",
                        "Check for HTTPS and valid certificate"
                    ]
        except:
            pass  # Continue with ML analysis if whitelist check fails
        
        # Extract 12 features (matching training code exactly)
        features = extract_url_features(url)
        features_array = np.array(features).reshape(1, -1)
        
        # Get prediction - EXACTLY as in training code
        model = model_loader.phishing_url_model
        prediction = model.predict(features_array)[0]
        probability = model.predict_proba(features_array)[0]
        
        # Model returns: 1 = SAFE, -1 = PHISHING (as per training code)
        is_phishing = (prediction == -1)
        
        if is_phishing:
            # Phishing detected
            confidence = float(probability[0] * 100)  # Probability of phishing class
            if confidence >= 90:
                threat_level = "dangerous"
            elif confidence >= 70:
                threat_level = "suspicious"
            else:
                threat_level = "suspicious"
        else:
            # Safe URL
            threat_level = "safe"
            confidence = float(probability[1] * 100)  # Probability of safe class
        
        # Extract interpretable features for display
        display_features = self._extract_display_features_from_12(features)
        
        recommendations = generate_recommendations(threat_level, is_url=True)
        
        return threat_level, confidence, display_features, recommendations
    
    def _extract_display_features_from_12(self, features: List[int]) -> List[str]:
        """
        Extract human-readable features from 12-feature array
        
        Args:
            features: List of 12 feature values
            
        Returns:
            List of human-readable feature descriptions
        """
        display_features = []
        
        if features[0] == -1:  # Using IP
            display_features.append("Uses IP address instead of domain")
        
        if features[1] == -1:  # Long URL
            display_features.append("Unusually long URL")
        
        if features[2] == -1:  # URL shortener
            display_features.append("URL shortening service detected")
        
        if features[3] == -1:  # @ symbol
            display_features.append("Contains @ symbol (phishing technique)")
        
        if features[4] == -1:  # Double slash
            display_features.append("Double slash redirecting detected")
        
        if features[5] == 0:  # Dash in domain
            display_features.append("Dash in domain name (suspicious)")
        
        if features[6] == -1:  # Too many subdomains
            display_features.append("Excessive subdomains detected")
        
        if features[7] == -1:  # No HTTPS
            display_features.append("Missing HTTPS encryption")
        
        if features[8] == -1:  # Non-standard port
            display_features.append("Non-standard port detected")
        
        if features[9] == -1:  # Suspicious keywords
            display_features.append("Suspicious keywords in domain")
        
        if features[11] == -1:  # Suspicious TLD
            display_features.append("Suspicious top-level domain")
        
        if not display_features:
            display_features.append("No obvious malicious indicators detected")
        
        return display_features
    
    def _ml_url_analysis_v2(self, url: str) -> Tuple[str, float, List[str], List[str]]:
        """
        Analyze URL using ML model with custom feature extraction
        
        Args:
            url: URL to analyze
            
        Returns:
            Tuple of (threat_level, confidence, features, recommendations)
        """
        from urllib.parse import parse_qs
        from collections import Counter
        
        # Extract features matching the training notebook
        features_dict = {}
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            
            # Import tldextract if available, otherwise use simple parsing
            try:
                import tldextract
                extracted = tldextract.extract(url)
                domain_name = extracted.domain
                subdomain = extracted.subdomain
                tld = extracted.suffix
            except:
                parts = domain.split('.')
                domain_name = parts[-2] if len(parts) >= 2 else domain
                subdomain = '.'.join(parts[:-2]) if len(parts) > 2 else ''
                tld = parts[-1] if parts else ''
            
            # 1. Length features
            features_dict['url_length'] = len(url)
            features_dict['domain_length'] = len(domain_name)
            features_dict['path_length'] = len(parsed.path)
            
            # 2. Protocol
            features_dict['has_https'] = 1 if parsed.scheme == 'https' else 0
            features_dict['has_http'] = 1 if parsed.scheme == 'http' else 0
            
            # 3. Domain features
            features_dict['subdomain_count'] = len(subdomain.split('.')) if subdomain else 0
            features_dict['has_subdomain'] = 1 if subdomain else 0
            
            # 4. Special character counts
            features_dict['dot_count'] = url.count('.')
            features_dict['hyphen_count'] = url.count('-')
            features_dict['underscore_count'] = url.count('_')
            features_dict['slash_count'] = url.count('/')
            features_dict['question_count'] = url.count('?')
            features_dict['equal_count'] = url.count('=')
            features_dict['at_count'] = url.count('@')
            features_dict['ampersand_count'] = url.count('&')
            features_dict['exclamation_count'] = url.count('!')
            features_dict['tilde_count'] = url.count('~')
            features_dict['percent_count'] = url.count('%')
            
            # 5. Digit features
            features_dict['digit_count'] = sum(c.isdigit() for c in url)
            features_dict['digit_ratio'] = features_dict['digit_count'] / len(url) if len(url) > 0 else 0
            
            # 6. IP address detection
            features_dict['has_ip'] = 1 if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', domain) else 0
            
            # 7. Suspicious TLD
            features_dict['suspicious_tld'] = 1 if any(url.endswith(t) for t in SUSPICIOUS_TLDS) else 0
            
            # 8. Phishing keywords
            from ..utils.constants import URL_PHISHING_KEYWORDS
            features_dict['phishing_keyword_count'] = sum(1 for kw in URL_PHISHING_KEYWORDS if kw in url.lower())
            
            # 9. URL shortener
            features_dict['is_shortened'] = 1 if any(short in url.lower() for short in URL_SHORTENERS) else 0
            
            # 10. Port
            features_dict['has_port'] = 1 if parsed.port else 0
            
            # 11. Query parameters
            features_dict['query_param_count'] = len(parse_qs(parsed.query))
            
            # 12. Entropy
            def calc_entropy(text):
                if not text: return 0
                counter = Counter(text)
                length = len(text)
                return -sum((c/length) * np.log2(c/length) for c in counter.values())
            
            features_dict['url_entropy'] = calc_entropy(url)
            features_dict['domain_entropy'] = calc_entropy(domain_name)
            
            # 13. Consecutive patterns
            features_dict['max_consecutive_digits'] = max([len(s) for s in re.findall(r'\d+', url)] or [0])
            features_dict['max_consecutive_chars'] = max([len(s) for s in re.findall(r'[a-zA-Z]+', url)] or [0])
            
            # 14. Brand mentions
            from ..utils.constants import BRAND_NAMES
            features_dict['brand_mention'] = sum(1 for brand in BRAND_NAMES if brand in url.lower())
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            return self._rule_based_analysis(url)
        
        # Create feature array in the order expected by the model
        feature_names = model_loader.url_feature_names
        feature_array = np.array([[features_dict.get(name, 0) for name in feature_names]])
        
        # Get prediction
        model = model_loader.url_model
        prediction = model.predict(feature_array)[0]
        probability = model.predict_proba(feature_array)[0]
        
        # Determine threat level (0 = legitimate, 1 = phishing - standard format)
        if prediction == 1:  # Phishing
            ml_confidence = probability[1] * 100
            if ml_confidence >= 90:
                threat_level = "dangerous"
            elif ml_confidence >= 70:
                threat_level = "suspicious"
            else:
                threat_level = "suspicious"
        else:  # Legitimate
            threat_level = "safe"
            ml_confidence = probability[0] * 100
        
        confidence = float(ml_confidence)
        
        # Extract interpretable features for display
        display_features = self._extract_display_features_from_dict(features_dict)
        
        # Generate recommendations
        recommendations = generate_recommendations(threat_level, is_url=True)
        
        return threat_level, confidence, display_features, recommendations
    
    def _extract_display_features_from_dict(self, features_dict: dict) -> List[str]:
        """
        Extract human-readable features from feature dictionary
        
        Args:
            features_dict: Dictionary of extracted features
            
        Returns:
            List of human-readable feature descriptions
        """
        display_features = []
        
        if features_dict.get('has_https', 0) == 0:
            display_features.append("Missing HTTPS encryption")
        
        if features_dict.get('has_ip', 0) == 1:
            display_features.append("Uses IP address instead of domain name")
        
        if features_dict.get('suspicious_tld', 0) == 1:
            display_features.append("Suspicious top-level domain")
        
        if features_dict.get('subdomain_count', 0) > 3:
            display_features.append("Excessive subdomains detected")
        
        if features_dict.get('phishing_keyword_count', 0) > 0:
            display_features.append(f"Contains {features_dict['phishing_keyword_count']} phishing keyword(s)")
        
        if features_dict.get('url_length', 0) > 100:
            display_features.append("Unusually long URL")
        
        if features_dict.get('is_shortened', 0) == 1:
            display_features.append("URL shortener detected")
        
        if not display_features:
            display_features.append("No obvious malicious indicators detected")
        
        return display_features
    
    def _rule_based_analysis(self, url: str) -> Tuple[str, float, List[str], List[str]]:
        """
        Analyze URL for malicious indicators using rule-based detection
        
        Args:
            url: URL to analyze
            
        Returns:
            Tuple of (threat_level, confidence, features, recommendations)
        """
        # Check whitelist first (prevents false positives)
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove port and www prefix for comparison
            domain = domain.split(':')[0]
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Check if domain or parent domain is in whitelist
            for legitimate_domain in LEGITIMATE_DOMAINS:
                if domain == legitimate_domain or domain.endswith('.' + legitimate_domain):
                    return "safe", 95.0, [
                        f"Verified legitimate domain: {legitimate_domain}",
                        "Domain is in trusted whitelist"
                    ], [
                        "This is a known legitimate website",
                        "Always verify the exact URL matches the official domain"
                    ]
        except:
            pass  # Continue with rule-based analysis if whitelist check fails
        
        url_lower = url.lower()
        features = []
        threat_score = 0
        
        # Check HTTPS
        if not url_lower.startswith('https://'):
            features.append("Missing HTTPS encryption")
            threat_score += 20
        
        # Check for suspicious TLDs
        if any(tld in url_lower for tld in SUSPICIOUS_TLDS):
            features.append("Suspicious top-level domain")
            threat_score += 30
        
        # Check for IP address instead of domain
        if re.search(r'://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url):
            features.append("Uses IP address instead of domain name")
            threat_score += 25
        
        # Check for common phishing patterns
        found_patterns = [p for p in URL_PHISHING_PATTERNS if p in url_lower]
        if found_patterns:
            features.append(f"Suspicious URL keywords: {', '.join(found_patterns[:2])}")
            threat_score += len(found_patterns) * 15
        
        # Check for excessive subdomains
        domain_parts = url_lower.split('://')[1].split('/')[0].split('.')
        if len(domain_parts) > 4:
            features.append("Excessive subdomains detected")
            threat_score += 15
        
        # Check for typosquatting common brands
        if any(brand in url_lower for brand in TYPO_BRANDS):
            features.append("Potential typosquatting detected")
            threat_score += 40
        
        # Determine threat level and confidence
        if threat_score >= 50:
            threat_level = "dangerous"
            confidence = min(95, 70 + threat_score // 3)
        elif threat_score >= 25:
            threat_level = "suspicious"
            confidence = min(85, 60 + threat_score // 2)
        else:
            threat_level = "safe"
            confidence = random.randint(75, 92)
        
        # Generate recommendations
        recommendations = generate_recommendations(threat_level, is_url=True)
        
        # If no features detected, add a default message
        if not features:
            features.append("No obvious malicious indicators detected")
        
        return threat_level, float(confidence), features, recommendations
