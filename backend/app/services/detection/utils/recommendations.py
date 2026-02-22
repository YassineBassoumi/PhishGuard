"""
Recommendation Generator
Generates security recommendations based on threat level
"""

from typing import List


def generate_recommendations(threat_level: str, is_url: bool = False) -> List[str]:
    """
    Generate security recommendations based on threat level
    
    Args:
        threat_level: The threat level (dangerous, suspicious, safe)
        is_url: Whether this is for URL or email analysis
        
    Returns:
        List of recommendation strings
    """
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
