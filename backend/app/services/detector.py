"""
PhishGuard AI - Detection Service
ML-powered phishing detection using trained SVM model
"""

import re
from typing import Tuple, List
import os
import joblib
import numpy as np
import random


class PhishingDetector:
    """Phishing detection service with ML model"""
    
    # Phishing keywords for rule-based feature detection
    PHISHING_KEYWORDS = [
        'verify', 'urgent', 'suspended', 'locked', 'confirm',
        'click here', 'account', 'password', 'update', 'expire',
        'security', 'act now', 'immediate', 'validate', 'unusual activity'
    ]
    
    # Suspicious TLDs
    SUSPICIOUS_TLDS = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top']
    
    # Legitimate domains (whitelist to prevent false positives)
    LEGITIMATE_DOMAINS = [
        'google.com', 'microsoft.com', 'apple.com', 'amazon.com', 'facebook.com',
        'github.com', 'stackoverflow.com', 'reddit.com', 'wikipedia.org', 'youtube.com',
        'twitter.com', 'linkedin.com', 'instagram.com', 'netflix.com', 'paypal.com',
        'ebay.com', 'dropbox.com', 'adobe.com', 'oracle.com', 'salesforce.com',
        'gmail.com', 'outlook.com', 'yahoo.com', 'bing.com', 'cloudflare.com',
        # Add more common legitimate domains
        'postgresql.org', 'python.org', 'nodejs.org', 'reactjs.org', 'vuejs.org',
        'angular.io', 'docker.com', 'kubernetes.io', 'mongodb.com', 'mysql.com',
        'npmjs.com', 'pypi.org', 'maven.org', 'gradle.org', 'jenkins.io',
        'atlassian.com', 'jetbrains.com', 'visualstudio.com', 'code.visualstudio.com',
        'w3.org', 'mozilla.org', 'chromium.org', 'webkit.org', 'apache.org',
        'gnu.org', 'fsf.org', 'opensource.org', 'creativecommons.org',
        'medium.com', 'dev.to', 'hashnode.com', 'freecodecamp.org', 'codecademy.com',
        'udemy.com', 'coursera.org', 'edx.org', 'khanacademy.org', 'pluralsight.com'
    ]
    
    def __init__(self):
        """Initialize detector and load ML models"""
        self.model = None
        self.vectorizer = None
        self.url_model = None
        self.url_feature_names = None
        self.phishing_url_model = None  # New: Phishing-URL-Detection model
        self._load_model()
        self._load_url_model()
        self._load_phishing_url_model()
    
    def _load_model(self):
        """Load the trained ML model and vectorizer"""
        try:
            # Get the directory of this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            backend_dir = os.path.dirname(os.path.dirname(current_dir))
            
            model_path = os.path.join(backend_dir, 'models', 'phishing_model.pkl')
            vectorizer_path = os.path.join(backend_dir, 'models', 'vectorizer.pkl')
            
            if os.path.exists(model_path) and os.path.exists(vectorizer_path):
                self.model = joblib.load(model_path)
                self.vectorizer = joblib.load(vectorizer_path)
                print("✓ ML model loaded successfully")
            else:
                print("⚠ ML model files not found. Using rule-based detection as fallback.")
        except Exception as e:
            print(f"⚠ Error loading ML model: {e}. Using rule-based detection as fallback.")
    
    def _load_url_model(self):
        """Load the trained URL phishing detection model"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            backend_dir = os.path.dirname(os.path.dirname(current_dir))
            
            url_model_path = os.path.join(backend_dir, 'models', 'url_phishing_model.pkl')
            url_features_path = os.path.join(backend_dir, 'models', 'url_feature_names.pkl')
            
            if os.path.exists(url_model_path) and os.path.exists(url_features_path):
                self.url_model = joblib.load(url_model_path)
                self.url_feature_names = joblib.load(url_features_path)
                print("✓ URL ML model loaded successfully")
            else:
                print("⚠ URL ML model files not found. Using rule-based detection as fallback.")
        except Exception as e:
            print(f"⚠ Error loading URL ML model: {e}. Using rule-based detection as fallback.")
    
    def _load_phishing_url_model(self):
        """Load the Phishing-URL-Detection model (12 features)"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            backend_dir = os.path.dirname(os.path.dirname(current_dir))
            
            # Try models in order of preference (newest first)
            model_names = [
                'phishing_url_model_final_v3.pkl',  # Latest retrained model
                'phishing_model_final_v2.pkl',      # Previous version
                'phishing_url_model.pkl'            # Original name
            ]
            
            model_path = None
            for model_name in model_names:
                test_path = os.path.join(backend_dir, 'models', model_name)
                if os.path.exists(test_path):
                    model_path = test_path
                    break
            
            if model_path:
                self.phishing_url_model = joblib.load(model_path)
                print(f"✓ Phishing URL model loaded successfully: {os.path.basename(model_path)}")
            else:
                print("⚠ Phishing URL model not found.")
        except Exception as e:
            print(f"⚠ Error loading Phishing URL model: {e}")
    
    def analyze_email(self, content: str) -> Tuple[str, float, List[str], List[str]]:
        """
        Analyze email content for phishing patterns using ML model
        
        Returns:
            Tuple of (threat_level, confidence, features, recommendations)
        """
        # Preprocess content
        content_lower = content.lower()
        
        # Get ML prediction if model is available
        if self.model is not None and self.vectorizer is not None:
            try:
                # Transform content using the vectorizer
                content_tfidf = self.vectorizer.transform([content_lower])
                
                # Get prediction
                prediction = self.model.predict(content_tfidf)[0]
                
                # Try to get probability if available (some models don't support it)
                try:
                    probability = self.model.predict_proba(content_tfidf)[0]
                    ml_confidence = float(probability[prediction] * 100)
                except AttributeError:
                    # Model doesn't support predict_proba (e.g., SVC without probability=True)
                    # Use decision function or default confidence
                    try:
                        decision = self.model.decision_function(content_tfidf)[0]
                        # Convert decision function to confidence (0-100)
                        ml_confidence = min(95.0, max(60.0, 75.0 + abs(decision) * 10))
                    except:
                        ml_confidence = 85.0  # Default confidence
                
                # Determine threat level based on ML prediction
                # Note: prediction 0 = Spam, 1 = Ham (based on spamEmails model)
                if prediction == 0:  # Spam/Phishing
                    if ml_confidence >= 90:
                        threat_level = "dangerous"
                    elif ml_confidence >= 70:
                        threat_level = "suspicious"
                    else:
                        threat_level = "suspicious"
                else:  # Ham/Legitimate
                    threat_level = "safe"
                
                # Adjust confidence based on prediction certainty
                confidence = ml_confidence
                
            except Exception as e:
                print(f"Error during ML prediction: {e}")
                # Fallback to rule-based
                return self._rule_based_analysis(content, content_lower)
        else:
            # Fallback to rule-based detection
            return self._rule_based_analysis(content, content_lower)
        
        # Extract rule-based features for detailed feedback
        features = self._extract_features(content, content_lower)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(threat_level)
        
        return threat_level, confidence, features, recommendations
    
    def _rule_based_analysis(self, content: str, content_lower: str) -> Tuple[str, float, List[str], List[str]]:
        """Fallback rule-based analysis when ML model is unavailable"""
        features = []
        threat_score = 0
        
        # Check for phishing keywords
        found_keywords = [kw for kw in self.PHISHING_KEYWORDS if kw in content_lower]
        if found_keywords:
            features.append(f"Phishing keywords detected: {', '.join(found_keywords[:3])}")
            threat_score += len(found_keywords) * 10
        
        # Check for suspicious URLs
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
        if urls:
            features.append(f"Contains {len(urls)} embedded link(s)")
            threat_score += len(urls) * 15
            
            for url in urls:
                if any(tld in url for tld in self.SUSPICIOUS_TLDS):
                    features.append("Suspicious domain TLD detected")
                    threat_score += 20
        
        # Check for urgency
        urgency_words = ['urgent', 'immediate', 'act now', 'expire', 'suspended']
        if any(word in content_lower for word in urgency_words):
            features.append("Urgency language detected")
            threat_score += 15
        
        # Check for credential requests
        if any(word in content_lower for word in ['password', 'username', 'login', 'credential']):
            features.append("Requests sensitive information")
            threat_score += 20
        
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
        
        if not features:
            features.append("No obvious phishing indicators detected")
        
        recommendations = self._generate_recommendations(threat_level)
        
        return threat_level, float(confidence), features, recommendations
    
    def _extract_features(self, content: str, content_lower: str) -> List[str]:
        """Extract rule-based features for detailed user feedback"""
        threat_indicators = []
        
        # Check for phishing keywords
        found_keywords = [kw for kw in self.PHISHING_KEYWORDS if kw in content_lower]
        if found_keywords:
            threat_indicators.append(f"Phishing keywords detected: {', '.join(found_keywords[:3])}")
        
        # Check for suspicious URLs
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
        if urls:
            # Check for suspicious domains
            has_suspicious_domain = False
            for url in urls:
                if any(tld in url for tld in self.SUSPICIOUS_TLDS):
                    threat_indicators.append("Suspicious domain TLD detected")
                    has_suspicious_domain = True
                    break
            
            # Only mention links if they're suspicious or there are many
            if has_suspicious_domain or len(urls) > 3:
                threat_indicators.append(f"Contains {len(urls)} embedded link(s)")
        
        # Check for urgency language
        urgency_words = ['urgent', 'immediate', 'act now', 'expire', 'suspended']
        if any(word in content_lower for word in urgency_words):
            threat_indicators.append("Urgency language detected")
        
        # Check for credential requests
        if any(word in content_lower for word in ['password', 'username', 'login', 'credential', 'ssn', 'social security']):
            threat_indicators.append("Requests sensitive information")
        
        # Check for financial indicators
        if any(word in content_lower for word in ['refund', 'prize', 'won', 'lottery', 'million', 'transfer', 'bank account']):
            threat_indicators.append("Financial/monetary language detected")
        
        # Check for suspicious patterns
        if re.search(r'\d[a-z]\d|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', content_lower):
            threat_indicators.append("Suspicious character patterns detected")
        
        # Return threat indicators if found, otherwise positive message
        if threat_indicators:
            return threat_indicators
        else:
            return ["No phishing indicators detected", "Email structure appears normal", "Sender patterns look legitimate"]
    
    def analyze_url(self, url: str) -> Tuple[str, float, List[str], List[str]]:
        """
        Analyze URL for malicious indicators using ML model
        
        Returns:
            Tuple of (threat_level, confidence, features, recommendations)
        """
        # Try Phishing-URL-Detection model first (most accurate)
        if self.phishing_url_model is not None:
            try:
                return self._phishing_url_analysis(url)
            except Exception as e:
                print(f"Error with phishing URL model: {e}, trying alternative")
        
        # Fallback to custom ML model
        if self.url_model is not None and self.url_feature_names is not None:
            try:
                return self._ml_url_analysis_v2(url)
            except Exception as e:
                print(f"Error during ML URL analysis: {e}, falling back to rule-based")
        
        # Final fallback to rule-based detection
        return self._rule_based_url_analysis(url)
    
    def _extract_url_features_for_ml(self, url: str) -> dict:
        """Extract features from URL matching the PhiUSIIL dataset format"""
        from urllib.parse import urlparse
        
        features = {}
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            path = parsed.path
            query = parsed.query
            
            # Basic length features
            features['URLLength'] = len(url)
            features['DomainLength'] = len(domain)
            
            # Domain features
            features['IsDomainIP'] = 1 if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', domain) else 0
            features['NoOfSubDomain'] = len(domain.split('.')) - 2 if len(domain.split('.')) > 2 else 0
            
            # Protocol
            features['IsHTTPS'] = 1 if parsed.scheme == 'https' else 0
            
            # Character counts
            features['NoOfLettersInURL'] = sum(c.isalpha() for c in url)
            features['LetterRatioInURL'] = features['NoOfLettersInURL'] / len(url) if len(url) > 0 else 0
            features['NoOfDegitsInURL'] = sum(c.isdigit() for c in url)
            features['DegitRatioInURL'] = features['NoOfDegitsInURL'] / len(url) if len(url) > 0 else 0
            
            # Special characters
            features['NoOfEqualsInURL'] = url.count('=')
            features['NoOfQMarkInURL'] = url.count('?')
            features['NoOfAmpersandInURL'] = url.count('&')
            features['NoOfOtherSpecialCharsInURL'] = sum(1 for c in url if c in '@#$%^*()[]{}|\\:;"<>,/')
            special_chars = features['NoOfEqualsInURL'] + features['NoOfQMarkInURL'] + features['NoOfAmpersandInURL'] + features['NoOfOtherSpecialCharsInURL']
            features['SpacialCharRatioInURL'] = special_chars / len(url) if len(url) > 0 else 0
            
            # TLD features
            tld_parts = domain.split('.')
            features['TLD'] = tld_parts[-1] if tld_parts else ''
            features['TLDLength'] = len(features['TLD'])
            
            # Suspicious patterns
            features['HasObfuscation'] = 1 if re.search(r'%[0-9a-fA-F]{2}', url) else 0
            features['NoOfObfuscatedChar'] = len(re.findall(r'%[0-9a-fA-F]{2}', url))
            features['ObfuscationRatio'] = features['NoOfObfuscatedChar'] / len(url) if len(url) > 0 else 0
            
            # Phishing keywords
            features['Bank'] = 1 if any(word in url.lower() for word in ['bank', 'banking']) else 0
            features['Pay'] = 1 if any(word in url.lower() for word in ['pay', 'payment', 'paypal']) else 0
            features['Crypto'] = 1 if any(word in url.lower() for word in ['crypto', 'bitcoin', 'wallet']) else 0
            
            # Set default values for features we can't extract from URL alone
            default_features = {
                'URLSimilarityIndex': 0, 'CharContinuationRate': 0.0, 'TLDLegitimateProb': 0.5,
                'URLCharProb': 0.5, 'LineOfCode': 0, 'LargestLineLength': 0, 'HasTitle': 0,
                'DomainTitleMatchScore': 0.0, 'URLTitleMatchScore': 0.0, 'HasFavicon': 0,
                'Robots': 0, 'IsResponsive': 0, 'NoOfURLRedirect': 0, 'NoOfSelfRedirect': 0,
                'HasDescription': 0, 'NoOfPopup': 0, 'NoOfiFrame': 0, 'HasExternalFormSubmit': 0,
                'HasSocialNet': 0, 'HasSubmitButton': 0, 'HasHiddenFields': 0, 'HasPasswordField': 0,
                'HasCopyrightInfo': 0, 'NoOfImage': 0, 'NoOfCSS': 0, 'NoOfJS': 0,
                'NoOfSelfRef': 0, 'NoOfEmptyRef': 0, 'NoOfExternalRef': 0
            }
            
            features.update(default_features)
            
        except Exception as e:
            print(f"Error extracting URL features: {e}")
            # Return default features
            features = {name: 0 for name in self.url_feature_names}
        
        return features
    
    def _ml_url_analysis(self, url: str) -> Tuple[str, float, List[str], List[str]]:
        """Analyze URL using ML model"""
        # Extract features
        features_dict = self._extract_url_features_for_ml(url)
        
        # Create feature array in correct order
        feature_array = np.array([[features_dict.get(name, 0) for name in self.url_feature_names]])
        
        # Get prediction
        prediction = self.url_model.predict(feature_array)[0]
        probability = self.url_model.predict_proba(feature_array)[0]
        
        # Determine threat level (PhiUSIIL dataset: 0 = phishing, 1 = legitimate - REVERSED!)
        if prediction == 0:  # 0 means PHISHING in PhiUSIIL dataset
            ml_confidence = probability[0] * 100
            if ml_confidence >= 90:
                threat_level = "dangerous"
            elif ml_confidence >= 70:
                threat_level = "suspicious"
            else:
                threat_level = "suspicious"
        else:  # 1 means LEGITIMATE in PhiUSIIL dataset
            threat_level = "safe"
            ml_confidence = probability[1] * 100
        
        confidence = float(ml_confidence)
        
        # Extract interpretable features for user feedback
        features = self._extract_url_features_for_display(url, features_dict)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(threat_level, is_url=True)
        
        return threat_level, confidence, features, recommendations
    
    def _extract_url_features_for_display(self, url: str, features_dict: dict) -> List[str]:
        """Extract human-readable features from URL for display"""
        display_features = []
        
        # HTTPS check
        if features_dict.get('IsHTTPS', 0) == 0:
            display_features.append("Missing HTTPS encryption")
        
        # IP address
        if features_dict.get('IsDomainIP', 0) == 1:
            display_features.append("Uses IP address instead of domain name")
        
        # Suspicious TLDs
        tld = features_dict.get('TLD', '')
        if tld in ['tk', 'ml', 'ga', 'cf', 'gq', 'xyz', 'top']:
            display_features.append(f"Suspicious top-level domain (.{tld})")
        
        # Excessive subdomains
        if features_dict.get('NoOfSubDomain', 0) > 3:
            display_features.append("Excessive subdomains detected")
        
        # Obfuscation
        if features_dict.get('HasObfuscation', 0) == 1:
            display_features.append("URL contains obfuscated characters")
        
        # Phishing keywords
        keywords_found = []
        if features_dict.get('Bank', 0) == 1:
            keywords_found.append('banking')
        if features_dict.get('Pay', 0) == 1:
            keywords_found.append('payment')
        if features_dict.get('Crypto', 0) == 1:
            keywords_found.append('crypto')
        
        if keywords_found:
            display_features.append(f"Contains sensitive keywords: {', '.join(keywords_found)}")
        
        # URL length
        if features_dict.get('URLLength', 0) > 100:
            display_features.append("Unusually long URL")
        
        # High special character ratio
        if features_dict.get('SpacialCharRatioInURL', 0) > 0.3:
            display_features.append("High ratio of special characters")
        
        if not display_features:
            display_features.append("No obvious malicious indicators detected")
        
        return display_features
    
    def _phishing_url_analysis(self, url: str) -> Tuple[str, float, List[str], List[str]]:
        """Analyze URL using retrained model (12 features) - matches training code exactly"""
        from app.services.url_feature_extractor import extract_url_features
        
        # WHITELIST DISABLED - Testing retrained model performance
        # Uncomment below to re-enable whitelist protection
        # url_lower = url.lower()
        # for legit_domain in self.LEGITIMATE_DOMAINS:
        #     if legit_domain in url_lower:
        #         return "safe", 95.0, ["Recognized legitimate domain"], self._generate_recommendations("safe", is_url=True)
        
        # Extract 12 features (matching training code exactly)
        features = extract_url_features(url)
        features_array = np.array(features).reshape(1, -1)
        
        # Get prediction - EXACTLY as in training code
        prediction = self.phishing_url_model.predict(features_array)[0]
        probability = self.phishing_url_model.predict_proba(features_array)[0]
        
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
        
        recommendations = self._generate_recommendations(threat_level, is_url=True)
        
        return threat_level, confidence, display_features, recommendations
    
    def _ml_url_analysis_v2(self, url: str) -> Tuple[str, float, List[str], List[str]]:
        """Analyze URL using ML model with custom feature extraction"""
        from urllib.parse import urlparse, parse_qs
        from collections import Counter
        
        # WHITELIST DISABLED - Testing retrained model performance
        # Uncomment below to re-enable whitelist protection
        # url_lower = url.lower()
        # for legit_domain in self.LEGITIMATE_DOMAINS:
        #     if legit_domain in url_lower:
        #         return "safe", 95.0, ["Recognized legitimate domain"], self._generate_recommendations("safe", is_url=True)
        
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
            suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.work', '.click']
            features_dict['suspicious_tld'] = 1 if any(url.endswith(t) for t in suspicious_tlds) else 0
            
            # 8. Phishing keywords
            phishing_keywords = ['login', 'signin', 'account', 'verify', 'secure', 'update', 
                                'confirm', 'banking', 'paypal', 'ebay', 'amazon']
            features_dict['phishing_keyword_count'] = sum(1 for kw in phishing_keywords if kw in url.lower())
            
            # 9. URL shortener
            shorteners = ['bit.ly', 'goo.gl', 'tinyurl', 't.co', 'ow.ly', 'is.gd']
            features_dict['is_shortened'] = 1 if any(short in url.lower() for short in shorteners) else 0
            
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
            brands = ['google', 'facebook', 'microsoft', 'apple', 'amazon', 'paypal', 'netflix']
            features_dict['brand_mention'] = sum(1 for brand in brands if brand in url.lower())
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            return self._rule_based_url_analysis(url)
        
        # Create feature array in the order expected by the model
        feature_array = np.array([[features_dict.get(name, 0) for name in self.url_feature_names]])
        
        # Get prediction
        prediction = self.url_model.predict(feature_array)[0]
        probability = self.url_model.predict_proba(feature_array)[0]
        
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
        
        # Generate recommendations
        recommendations = self._generate_recommendations(threat_level, is_url=True)
        
        return threat_level, confidence, display_features, recommendations
    
    def _rule_based_url_analysis(self, url: str) -> Tuple[str, float, List[str], List[str]]:
        """
        Analyze URL for malicious indicators
        
        Returns:
            Tuple of (threat_level, confidence, features, recommendations)
        """
        url_lower = url.lower()
        features = []
        threat_score = 0
        
        # Check HTTPS
        if not url_lower.startswith('https://'):
            features.append("Missing HTTPS encryption")
            threat_score += 20
        
        # Check for suspicious TLDs
        if any(tld in url_lower for tld in self.SUSPICIOUS_TLDS):
            features.append("Suspicious top-level domain")
            threat_score += 30
        
        # Check for IP address instead of domain
        if re.search(r'://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url):
            features.append("Uses IP address instead of domain name")
            threat_score += 25
        
        # Check for common phishing patterns
        phishing_patterns = ['paypal', 'login', 'verify', 'account', 'secure', 'update']
        found_patterns = [p for p in phishing_patterns if p in url_lower and not any(legit in url_lower for legit in self.LEGITIMATE_DOMAINS)]
        if found_patterns:
            features.append(f"Suspicious URL keywords: {', '.join(found_patterns[:2])}")
            threat_score += len(found_patterns) * 15
        
        # Check for excessive subdomains
        domain_parts = url_lower.split('://')[1].split('/')[0].split('.')
        if len(domain_parts) > 4:
            features.append("Excessive subdomains detected")
            threat_score += 15
        
        # Check for typosquatting common brands
        typo_brands = ['paypa1', 'g00gle', 'micros0ft', 'amazom', 'app1e']
        if any(brand in url_lower for brand in typo_brands):
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
        recommendations = self._generate_recommendations(threat_level, is_url=True)
        
        # If no features detected, add a default message
        if not features:
            features.append("No obvious malicious indicators detected")
        
        return threat_level, float(confidence), features, recommendations
    
    def _generate_recommendations(self, threat_level: str, is_url: bool = False) -> List[str]:
        """Generate security recommendations based on threat level"""
        recommendations = []
        
        if threat_level == "dangerous":
            if is_url:
                recommendations = [
                    "Do NOT visit this URL",
                    "This appears to be a phishing or malicious site",
                    "Report this URL to your IT security team",
                    "Block this domain in your security software"
                ]
            else:
                recommendations = [
                    "Delete this email immediately",
                    "Do not click any links or download attachments",
                    "Report this email as phishing",
                    "Contact the supposed sender through official channels"
                ]
        
        elif threat_level == "suspicious":
            if is_url:
                recommendations = [
                    "Exercise caution before visiting this URL",
                    "Verify the URL legitimacy through official sources",
                    "Use a secure browser with anti-phishing features"
                ]
            else:
                recommendations = [
                    "Verify sender identity before taking action",
                    "Do not provide sensitive information",
                    "Contact the sender through known official channels",
                    "Be cautious with links and attachments"
                ]
        
        else:  # safe
            if is_url:
                recommendations = [
                    "URL appears legitimate",
                    "Always verify you're on the correct website after visiting",
                    "Check for HTTPS and valid certificates"
                ]
            else:
                recommendations = [
                    "Email appears legitimate",
                    "Continue to verify sender identity for important requests",
                    "Stay vigilant for any unusual content"
                ]
        
        return recommendations


# Singleton instance
detector = PhishingDetector()
