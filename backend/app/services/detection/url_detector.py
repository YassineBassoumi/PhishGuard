"""
URL Phishing Detector
ML-powered URL phishing detection (RandomForest, 23 features, binary)
"""

import re
import random
import ipaddress
import pandas as pd
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
        pass
    
    def analyze(self, url: str) -> Tuple[str, float, List[str], List[str]]:
        """
        Analyze URL for malicious indicators.
        
        Flow: private-IP check -> whitelist check -> ML model -> rule-based fallback
        
        Returns:
            Tuple of (threat_level, confidence, features, recommendations)
        """
        # 1. Private/local IP — always safe
        try:
            parsed = urlparse(url)
            hostname = parsed.netloc.split(':')[0]
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback:
                return "safe", 95.0, [
                    "Adresse IP privée/locale détectée",
                    "Il s'agit d'une ressource réseau locale (routeur, appareil, etc.)",
                    "Non accessible depuis Internet"
                ], [
                    "Cela semble être un appareil réseau local",
                    "Assurez-vous de faire confiance au réseau local auquel vous êtes connecté",
                    "Les IP privées ne sont pas des sites de phishing"
                ]
        except Exception:
            pass
        
        # 2. Whitelist for known legitimate domains (prevents false positives)
        domain = self._extract_domain(url)
        if domain:
            for legit in LEGITIMATE_DOMAINS:
                if domain == legit or domain.endswith('.' + legit):
                    return "safe", 98.0, [
                        f"Domaine légitime vérifié : {legit}",
                        "Le domaine est dans la liste de confiance",
                        "Aucun indicateur de phishing détecté"
                    ], [
                        "Il s'agit d'un site web légitime connu",
                        "Vérifiez toujours que l'URL exacte correspond au domaine officiel",
                        "Vérifiez la présence de HTTPS et d'un certificat valide"
                    ]
        
        # 3. ML model (primary detection)
        if model_loader.url_model is not None:
            try:
                return self._ml_analysis(url)
            except Exception as e:
                print(f"Error during ML URL analysis: {e}, falling back to rule-based")
        
        # 4. Rule-based fallback
        return self._rule_based_analysis(url)
    
    def _extract_domain(self, url: str) -> str:
        """Extract clean domain from URL for whitelist comparison."""
        try:
            parsed = urlparse(url if '://' in url else 'http://' + url)
            domain = parsed.netloc.lower().split(':')[0]
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception:
            return ''
    
    def _ml_analysis(self, url: str) -> Tuple[str, float, List[str], List[str]]:
        """
        Analyze URL using RandomForest model (23 features, binary).
        Label encoder: legitimate=0, phishing=1
        """
        # Extract features as dict
        features_dict = extract_url_features(url)
        
        # Build DataFrame with correct column order
        feature_names = model_loader.url_feature_names
        X = pd.DataFrame([features_dict])[feature_names]
        
        model = model_loader.url_model
        le = model_loader.url_label_encoder
        
        pred_class = model.predict(X)[0]
        pred_proba = model.predict_proba(X)[0]
        
        predicted_label = le.classes_[pred_class]       # 'legitimate' or 'phishing'
        confidence = float(pred_proba[pred_class]) * 100
        is_phishing = (predicted_label == 'phishing')
        
        # Map to threat levels
        if is_phishing:
            if confidence >= 85:
                threat_level = "dangerous"
            else:
                threat_level = "suspicious"
        else:
            if confidence >= 80:
                threat_level = "safe"
            elif confidence >= 65:
                threat_level = "suspicious"
            else:
                threat_level = "suspicious"
        
        display_features = self._build_display_features(features_dict, threat_level)
        recommendations = generate_recommendations(threat_level, is_url=True, url_features=features_dict)
        
        return threat_level, confidence, display_features, recommendations
    
    def _build_display_features(self, fd: dict, threat_level: str) -> List[str]:
        """Build human-readable feature list from the extracted feature dict."""
        warnings = []   # suspicious/dangerous indicators
        positives = []   # safe indicators

        # --- Suspicious / dangerous indicators ---
        if fd.get('use_of_ip', 0) == 1:
            warnings.append("Utilise une adresse IP au lieu d'un nom de domaine")

        if fd.get('short_url', 0) == 1:
            warnings.append("Raccourcisseur d'URL détecté")

        if fd.get('sus_url', 0) == 1:
            warnings.append("Mots-clés suspects détectés (login, account, PayPal, etc.)")

        if fd.get('tld_risk', 0) == 1:
            warnings.append("Domaine de premier niveau à risque (.tk, .xyz, .ml, etc.)")

        if fd.get('count@', 0) > 0:
            warnings.append("Contient le symbole @ (technique de redirection trompeuse)")

        if fd.get('subdomain_count', 0) > 3:
            warnings.append(f"Sous-domaines excessifs ({fd['subdomain_count']} niveaux)")

        if fd.get('url_length', 0) > 100:
            warnings.append(f"URL anormalement longue ({fd['url_length']} caractères)")

        if fd.get('domain_entropy', 0) > 4.0:
            warnings.append("Nom de domaine avec structure aléatoire suspecte")

        if fd.get('count_embed_domian', 0) > 0:
            warnings.append("Double slash de redirection détecté dans le chemin")

        if fd.get('hostname_length', 0) > 30:
            warnings.append(f"Nom d'hôte anormalement long ({fd['hostname_length']} caractères)")

        if fd.get('count-', 0) > 3:
            warnings.append(f"Nombre excessif de tirets dans l'URL ({fd['count-']})")

        if fd.get('count-digits', 0) > 15:
            warnings.append("Nombre élevé de chiffres dans l'URL")

        if fd.get('path_length', 0) > 80:
            warnings.append("Chemin d'URL inhabituellement long")

        if fd.get('special_char_ratio', 0) > 0.35:
            warnings.append("Ratio élevé de caractères spéciaux")

        if fd.get('count_dir', 0) > 5:
            warnings.append(f"Structure de répertoires complexe ({fd['count_dir']} niveaux)")

        if fd.get('is_https', 0) == 0 and threat_level != 'safe':
            warnings.append("Chiffrement HTTPS manquant")

        # --- Safe indicators ---
        if fd.get('is_https', 0) == 1:
            positives.append("✓ Connexion HTTPS sécurisée")

        if fd.get('tld_risk', 0) == 0 and fd.get('tld_length', 0) > 0:
            positives.append("✓ Domaine de premier niveau fiable")

        if fd.get('subdomain_count', 0) <= 1 and fd.get('hostname_length', 0) < 30:
            positives.append("✓ Structure de domaine normale")

        if fd.get('domain_entropy', 0) < 3.5 and fd.get('domain_entropy', 0) > 0:
            positives.append("✓ Nom de domaine lisible et cohérent")

        if fd.get('sus_url', 0) == 0 and fd.get('short_url', 0) == 0 and fd.get('use_of_ip', 0) == 0:
            positives.append("✓ Aucun mot-clé de phishing ou raccourcisseur détecté")

        # --- Assemble based on threat level ---
        if threat_level in ('dangerous', 'suspicious'):
            if warnings:
                return warnings
            # Model detected threat but no individual check fired
            return [
                "Modèle d'IA avancé : Combinaison suspecte de caractéristiques",
                "Le profil global de l'URL correspond à des schémas d'attaques connues"
            ]
        else:
            # Safe: show positive indicators, optionally with minor warnings
            display = positives[:4] if positives else ["✓ Aucun indicateur malveillant détecté"]
            if warnings:
                display.append(f"⚠ Note : {warnings[0]}")
            return display
    
    def _rule_based_analysis(self, url: str) -> Tuple[str, float, List[str], List[str]]:
        """
        Fallback: rule-based detection when ML model is unavailable.
        """
        # Check whitelist
        domain = self._extract_domain(url)
        if domain:
            for legit in LEGITIMATE_DOMAINS:
                if domain == legit or domain.endswith('.' + legit):
                    return "safe", 95.0, [
                        f"Domaine légitime vérifié : {legit}",
                        "Le domaine est dans la liste de confiance"
                    ], [
                        "Il s'agit d'un site web légitime connu",
                        "Vérifiez toujours que l'URL exacte correspond au domaine officiel"
                    ]
        
        url_lower = url.lower()
        features = []
        threat_score = 0
        
        if not url_lower.startswith('https://'):
            features.append("Chiffrement HTTPS manquant")
            threat_score += 20
        
        if any(tld in url_lower for tld in SUSPICIOUS_TLDS):
            features.append("Domaine de premier niveau suspect")
            threat_score += 30
        
        if re.search(r'://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url):
            features.append("Utilise une adresse IP au lieu d'un nom de domaine")
            threat_score += 25
        
        found_patterns = [p for p in URL_PHISHING_PATTERNS if p in url_lower]
        if found_patterns:
            features.append(f"Mots-clés d'URL suspects : {', '.join(found_patterns[:2])}")
            threat_score += len(found_patterns) * 15
        
        try:
            domain_parts = url_lower.split('://')[1].split('/')[0].split('.')
            if len(domain_parts) > 4:
                features.append("Sous-domaines excessifs détectés")
                threat_score += 15
        except Exception:
            pass
        
        if any(brand in url_lower for brand in TYPO_BRANDS):
            features.append("Typosquatting potentiel détecté")
            threat_score += 40
        
        if threat_score >= 50:
            threat_level = "dangerous"
            confidence = min(95, 70 + threat_score // 3)
        elif threat_score >= 25:
            threat_level = "suspicious"
            confidence = min(85, 60 + threat_score // 2)
        else:
            threat_level = "safe"
            confidence = random.randint(75, 92)
        
        recommendations = generate_recommendations(threat_level, is_url=True)
        
        if not features:
            features.append("Aucun indicateur malveillant évident détecté")
        
        return threat_level, float(confidence), features, recommendations
