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
                "✓ This URL appears to be legitimate and safe to visit",
                "✓ No suspicious patterns or phishing indicators detected",
                "✓ The domain structure looks normal and trustworthy",
                "Always ensure you see HTTPS and a valid certificate when visiting"
            ]
        else:
            recommendations = [
                "✓ This email appears to be legitimate",
                "✓ No phishing indicators or suspicious content detected",
                "✓ The sender and content seem trustworthy",
                "Continue to stay vigilant with unexpected requests"
            ]
    
    return recommendations
