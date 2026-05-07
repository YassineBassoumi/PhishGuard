"""
Hybrid Email Detector
Combines email text analysis with deep URL analysis for better phishing detection

This detector:
1. Extracts URLs from email content
2. Analyzes text content (without URLs) using email phishing model (LinearSVC)
3. Analyzes each URL using URL phishing model
4. Combines results for final verdict
"""

import re
from typing import Tuple, List, Dict, Optional
from .email_detector import EmailDetector
from .url_detector import URLDetector
from .email_preprocessor import preprocess as preprocess_raw_email


class HybridEmailDetector:
    """
    Hybrid email detector that combines text and URL analysis
    
    This provides better detection by:
    - Using email model for text context (tone, keywords, urgency)
    - Using URL model for deep URL analysis (domain, structure, patterns)
    - Combining results intelligently
    """
    
    def __init__(self):
        """Initialize hybrid detector with both email and URL detectors"""
        self.email_detector = EmailDetector()
        self.url_detector = URLDetector()
    
    def analyze(self, content: str, use_hybrid: bool = True) -> Tuple[str, float, List[str], List[str], Optional[List[Dict]], Dict]:
        """
        Analyze email content using hybrid approach.

        Returns:
            Tuple of (threat_level, confidence, features, recommendations, url_analysis_results, decision_trace)
        """
        # Step 0: Preprocess raw RFC822 emails (full headers + MIME + quoted-printable HTML).
        # If the user pasted a raw email, this strips headers/boilerplate and decodes the body
        # so the ML pipeline only sees clean human-readable text.
        content, was_preprocessed = preprocess_raw_email(content)

        if not use_hybrid:
            threat_level, confidence, features, recommendations, text_trace = \
                self.email_detector.analyze_with_trace(content)
            trace = self._build_trace(text_trace, [], threat_level, "Mode standard (analyse texte uniquement)", was_preprocessed)
            return threat_level, confidence, features, recommendations, None, trace

        # Step 1: Extract URLs from content
        url_pattern = r'https?://[^\s<>"\']+'
        urls = re.findall(url_pattern, content)

        if not urls:
            # No URLs found - use standard email analysis
            threat_level, confidence, features, recommendations, text_trace = \
                self.email_detector.analyze_with_trace(content)
            trace = self._build_trace(text_trace, [], threat_level, "Aucune URL détectée - analyse texte uniquement", was_preprocessed)
            return threat_level, confidence, features, recommendations, None, trace

        # Step 2: Create text-only version
        text_only = content
        for url in urls:
            text_only = text_only.replace(url, '[URL]')

        # Step 3: Analyze text content using email phishing model (with trace)
        text_threat, text_confidence, text_features, text_recommendations, text_trace = \
            self.email_detector.analyze_with_trace(text_only)
        
        # Step 4: Analyze each URL using URL model
        url_results = []
        url_threats = []
        
        for url in urls:
            try:
                url_threat, url_confidence, url_features, url_recommendations = self.url_detector.analyze(url)
                url_results.append({
                    'url': url,
                    'threat_level': url_threat,
                    'confidence': url_confidence,
                    'features': url_features,
                    'recommendations': url_recommendations
                })
                url_threats.append(url_threat)
            except Exception as e:
                print(f"Error analyzing URL {url}: {e}")
                # If URL analysis fails, mark as suspicious
                url_results.append({
                    'url': url,
                    'threat_level': 'suspicious',
                    'confidence': 50.0,
                    'features': ['Erreur lors de l\'analyse de l\'URL'],
                    'recommendations': ['Vérifier manuellement cette URL']
                })
                url_threats.append('suspicious')
        
        # Step 5: Combine results intelligently
        final_threat, final_confidence, final_features, final_recommendations, combiner_rule = self._combine_results(
            text_threat, text_confidence, text_features, text_recommendations,
            url_results, url_threats
        )

        # Step 6: Build full decision trace
        trace = self._build_trace(text_trace, url_results, final_threat, combiner_rule, was_preprocessed)

        return final_threat, final_confidence, final_features, final_recommendations, url_results, trace

    def _build_trace(self, text_trace: Dict, url_results: List[Dict], final_threat: str, combiner_rule: str, was_preprocessed: bool = False) -> Dict:
        """Build the unified decision trace exposed to the frontend."""
        return {
            "ml_email": {
                "prediction": text_trace.get("ml_prediction"),
                "confidence": text_trace.get("ml_confidence"),
                "rule_score": text_trace.get("rule_score"),
                "verdict": text_trace.get("verdict"),
                "reason": text_trace.get("reason"),
            },
            "url_models": [
                {
                    "url": u["url"],
                    "verdict": u["threat_level"],
                    "confidence": round(float(u["confidence"]), 2),
                }
                for u in url_results
            ],
            "combiner_rule": combiner_rule,
            "final_verdict": final_threat,
            "ml_overridden": text_trace.get("verdict") != final_threat,
            "preprocessed": was_preprocessed,
        }
    
    def _combine_results(
        self,
        text_threat: str,
        text_confidence: float,
        text_features: List[str],
        text_recommendations: List[str],
        url_results: List[Dict],
        url_threats: List[str]
    ) -> Tuple[str, float, List[str], List[str], str]:
        """
        Combine text and URL analysis results intelligently
        
        Logic:
        - If ANY URL is dangerous → Final is at least suspicious (or dangerous if text agrees)
        - If text is dangerous AND URLs are suspicious → Final is dangerous
        - If text is safe but URLs are dangerous → Final is dangerous (URLs override)
        - If both are safe → Final is safe
        - Confidence is weighted average
        
        Args:
            text_threat: Threat level from text analysis
            text_confidence: Confidence from text analysis
            text_features: Features from text analysis
            text_recommendations: Recommendations from text analysis
            url_results: List of URL analysis results
            url_threats: List of URL threat levels
            
        Returns:
            Tuple of (final_threat_level, final_confidence, final_features, final_recommendations)
        """
        # Count threat levels in URLs
        dangerous_urls = url_threats.count('dangerous')
        suspicious_urls = url_threats.count('suspicious')
        safe_urls = url_threats.count('safe')
        total_urls = len(url_threats)
        
        # Determine final threat level (and capture which combiner rule fired)
        final_threat, combiner_rule = self._determine_combined_threat(
            text_threat, dangerous_urls, suspicious_urls, safe_urls, total_urls
        )
        
        # Calculate weighted confidence
        # Text gets 60% weight, URLs get 40% weight (text context is slightly more important)
        url_avg_confidence = sum(r['confidence'] for r in url_results) / len(url_results) if url_results else 0
        final_confidence = (text_confidence * 0.6) + (url_avg_confidence * 0.4)
        
        # Combine features
        final_features = text_features.copy()
        
        # Add URL-specific features
        if dangerous_urls > 0:
            final_features.insert(0, f"⚠️ {dangerous_urls} URL(s) dangereuse(s) détectée(s)")
        if suspicious_urls > 0:
            final_features.insert(0, f"⚠️ {suspicious_urls} URL(s) suspecte(s) détectée(s)")
        
        # Add top URL features (max 2 URLs)
        for i, url_result in enumerate(url_results[:2]):
            if url_result['threat_level'] in ['dangerous', 'suspicious']:
                url_short = url_result['url'][:50] + '...' if len(url_result['url']) > 50 else url_result['url']
                final_features.append(f"URL {i+1}: {url_short}")
                # Add top 2 features from this URL
                for feature in url_result['features'][:2]:
                    final_features.append(f"  └─ {feature}")
        
        # Combine recommendations (prioritize most severe)
        final_recommendations = []
        
        if final_threat == 'dangerous':
            final_recommendations.append("🚨 NE PAS cliquer sur les liens dans cet email")
            final_recommendations.append("Supprimer cet email immédiatement")
            final_recommendations.append("Signaler comme phishing à votre service IT")
        elif final_threat == 'suspicious':
            final_recommendations.append("⚠️ Vérifier l'expéditeur avant de cliquer sur les liens")
            final_recommendations.append("Ne pas fournir d'informations personnelles")
            final_recommendations.append("Contacter l'expéditeur par un canal alternatif pour confirmer")
        else:
            final_recommendations.append("✓ Email semble légitime")
            final_recommendations.append("Toujours vérifier l'URL avant de cliquer")
            final_recommendations.append("Rester vigilant face aux demandes inhabituelles")
        
        # Add URL-specific recommendations
        if dangerous_urls > 0 or suspicious_urls > 0:
            final_recommendations.append(f"Vérifier manuellement les {total_urls} URL(s) avant de cliquer")

        return final_threat, final_confidence, final_features, final_recommendations, combiner_rule
    
    def _determine_combined_threat(
        self,
        text_threat: str,
        dangerous_urls: int,
        suspicious_urls: int,
        safe_urls: int,
        total_urls: int
    ) -> Tuple[str, str]:
        """
        Determine final threat level based on text and URL threats
        
        Priority rules:
        1. If ANY URL is dangerous AND text is not safe → DANGEROUS
        2. If majority of URLs are dangerous → DANGEROUS
        3. If text is dangerous AND any URL is suspicious → DANGEROUS
        4. If ANY URL is dangerous but text is safe → SUSPICIOUS (escalate from safe)
        5. If text is suspicious OR any URL is suspicious → SUSPICIOUS
        6. If both text and all URLs are safe → SAFE
        
        Args:
            text_threat: Threat level from text analysis
            dangerous_urls: Count of dangerous URLs
            suspicious_urls: Count of suspicious URLs
            safe_urls: Count of safe URLs
            total_urls: Total number of URLs
            
        Returns:
            Final threat level: 'dangerous', 'suspicious', or 'safe'
        """
        # Rule 1
        if dangerous_urls > 0 and text_threat != 'safe':
            return 'dangerous', "Règle 1: URL dangereuse + texte non sûr → DANGEROUS"
        # Rule 2
        if dangerous_urls > total_urls / 2:
            return 'dangerous', "Règle 2: Majorité des URLs dangereuses → DANGEROUS"
        # Rule 3
        if text_threat == 'dangerous' and suspicious_urls > 0:
            return 'dangerous', "Règle 3: Texte dangereux + URL suspecte → DANGEROUS"
        # Rule 4
        if dangerous_urls > 0 and text_threat == 'safe':
            return 'suspicious', "Règle 4: URL dangereuse mais texte sûr → SUSPICIOUS (escalade)"
        # Rule 5
        if suspicious_urls > 0:
            return 'suspicious', "Règle 5: URL suspecte détectée → SUSPICIOUS"
        # Rule 6: downgrade
        if text_threat == 'suspicious' and safe_urls == total_urls and total_urls > 0:
            return 'safe', "Règle 6: Texte suspect mais toutes les URLs sûres → SAFE (rétrogradé)"
        # Rule 7
        if text_threat == 'suspicious':
            return 'suspicious', "Règle 7: Texte suspect sans URL → SUSPICIOUS"
        # Rule 8
        if text_threat == 'safe' and dangerous_urls == 0 and suspicious_urls == 0:
            return 'safe', "Règle 8: Texte et URLs tous sûrs → SAFE"
        # Default
        return 'suspicious', "Par défaut: incertain → SUSPICIOUS (par prudence)"


# Create singleton instance
hybrid_email_detector = HybridEmailDetector()
