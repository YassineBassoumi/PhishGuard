"""
Recommendation Generator
Generates security recommendations based on threat level
"""

from typing import List, Optional


def generate_recommendations(
    threat_level: str,
    is_url: bool = False,
    url_features: Optional[dict] = None,
    email_context: Optional[dict] = None,
) -> List[str]:
    """
    Generate security recommendations based on threat level and context.
    
    Args:
        threat_level: The threat level (dangerous, suspicious, safe)
        is_url: Whether this is for URL or email analysis
        url_features: Optional dict of extracted URL features for context-aware tips
        email_context: Optional dict with detected threat signals for context-aware email tips
            Keys: has_urgency, has_credentials, has_financial, has_urls,
                  has_suspicious_tld, has_typosquatting, phishing_keywords
        
    Returns:
        List of recommendation strings
    """
    if is_url and url_features is not None:
        return _url_recommendations(threat_level, url_features)
    
    if not is_url and email_context is not None:
        return _email_recommendations(threat_level, email_context)

    recommendations = []
    
    if threat_level == "dangerous":
        if is_url:
            recommendations = [
                "⛔ NE visitez PAS cette URL",
                "Cela semble être un site de phishing ou malveillant",
                "Signalez cette URL à votre équipe de sécurité informatique",
                "Bloquez ce domaine dans votre logiciel de sécurité"
            ]
        else:
            recommendations = [
                "Supprimez cet email immédiatement",
                "Ne cliquez sur aucun lien et ne téléchargez pas de pièces jointes",
                "Signalez cet email comme phishing",
                "Contactez l'expéditeur supposé via les canaux officiels"
            ]
    
    elif threat_level == "suspicious":
        if is_url:
            recommendations = [
                "⚠ Faites preuve de prudence avant de visiter cette URL",
                "Vérifiez la légitimité de l'URL via des sources officielles",
                "Utilisez un navigateur sécurisé avec des fonctionnalités anti-phishing"
            ]
        else:
            recommendations = [
                "Vérifiez l'identité de l'expéditeur avant d'agir",
                "Ne fournissez pas d'informations sensibles",
                "Contactez l'expéditeur via des canaux officiels connus",
                "Soyez prudent avec les liens et les pièces jointes"
            ]
    
    else:  # safe
        if is_url:
            recommendations = [
                "✓ Cette URL semble légitime et sûre à visiter",
                "✓ Aucun modèle suspect ou indicateur de phishing détecté",
                "✓ La structure du domaine semble normale et digne de confiance",
                "Assurez-vous toujours de voir HTTPS et un certificat valide lors de la visite"
            ]
        else:
            recommendations = [
                "✓ Cet email semble légitime",
                "✓ Aucun indicateur de phishing ou contenu suspect détecté",
                "✓ L'expéditeur et le contenu semblent dignes de confiance",
                "Restez vigilant face aux demandes inattendues"
            ]
    
    return recommendations


def _email_recommendations(threat_level: str, ctx: dict) -> List[str]:
    """Context-aware recommendations based on actual threats found in the email."""
    
    if threat_level == "dangerous":
        recs = ["🚨 Cet email présente des signes forts de phishing"]
        
        if ctx.get('has_credentials'):
            recs.append("Ne saisissez JAMAIS vos identifiants ou mots de passe en réponse")
        if ctx.get('has_urgency'):
            recs.append("L'urgence est une tactique de manipulation — prenez le temps de vérifier")
        if ctx.get('has_urls'):
            recs.append("Ne cliquez sur AUCUN lien dans cet email")
        if ctx.get('has_financial'):
            recs.append("Ne communiquez jamais vos informations bancaires par email")
        if ctx.get('has_typosquatting'):
            recs.append("L'expéditeur imite une marque connue — vérifiez l'adresse exacte")
        if ctx.get('has_suspicious_tld'):
            recs.append("Le domaine utilise une extension suspecte (.tk, .xyz, etc.)")
        
        recs.append("Signalez cet email comme phishing et supprimez-le")
        recs.append("Contactez l'organisation concernée via son site officiel")
        return recs
    
    elif threat_level == "suspicious":
        recs = ["⚠️ Cet email contient des éléments suspects"]
        
        if ctx.get('has_credentials'):
            recs.append("Ne partagez pas vos identifiants sans vérification préalable")
        if ctx.get('has_urgency'):
            recs.append("Méfiez-vous du ton urgent — les services légitimes ne pressent pas ainsi")
        if ctx.get('has_urls'):
            recs.append("Vérifiez les liens en survolant avant de cliquer")
        if ctx.get('has_financial'):
            recs.append("Vérifiez toute demande financière par un canal séparé")
        if ctx.get('has_typosquatting'):
            recs.append("Vérifiez l'orthographe exacte du nom de domaine")
        
        recs.append("Vérifiez l'identité de l'expéditeur via les canaux officiels")
        return recs
    
    else:  # safe
        recs = ["✓ Cet email semble légitime"]
        recs.append("✓ Aucun indicateur de phishing détecté par notre modèle d'IA")
        
        if ctx.get('has_urls'):
            recs.append("Vérifiez tout de même les URLs avant de saisir des données sensibles")
        else:
            recs.append("✓ Contenu et structure conformes aux emails légitimes")
        
        recs.append("Restez vigilant face aux demandes inattendues")
        return recs


def _url_recommendations(threat_level: str, fd: dict) -> List[str]:
    """Context-aware recommendations based on what was actually detected in the URL."""

    if threat_level == "dangerous":
        recs = ["⛔ NE visitez PAS cette URL — risque élevé de phishing"]

        if fd.get('sus_url', 0) == 1:
            recs.append("Ne saisissez JAMAIS vos identifiants sur ce site")
        if fd.get('short_url', 0) == 1:
            recs.append("Les raccourcisseurs d'URL masquent la destination réelle — ne cliquez pas")
        if fd.get('tld_risk', 0) == 1:
            recs.append("Ce domaine utilise un TLD souvent associé aux escroqueries")
        if fd.get('use_of_ip', 0) == 1:
            recs.append("Les sites légitimes n'utilisent pas d'adresses IP comme URL")
        if fd.get('is_https', 0) == 0:
            recs.append("Absence de HTTPS — vos données ne seraient pas chiffrées")

        recs.append("Signalez cette URL à votre équipe de sécurité informatique")
        recs.append("Bloquez ce domaine dans votre logiciel de sécurité")
        return recs

    elif threat_level == "suspicious":
        recs = ["⚠ Faites preuve de prudence avant de visiter cette URL"]

        if fd.get('sus_url', 0) == 1:
            recs.append("L'URL contient des mots-clés de type phishing — vérifiez le domaine officiel")
        if fd.get('short_url', 0) == 1:
            recs.append("Utilisez un outil d'expansion d'URL pour voir la destination réelle")
        if fd.get('is_https', 0) == 0:
            recs.append("Privilégiez les sites utilisant HTTPS pour protéger vos données")
        if fd.get('tld_risk', 0) == 1:
            recs.append("Méfiez-vous des domaines avec des extensions inhabituelles")
        if fd.get('domain_entropy', 0) > 4.0:
            recs.append("Le nom de domaine semble généré aléatoirement — signe de fraude possible")

        recs.append("Vérifiez la légitimité via le site officiel de l'organisation concernée")
        recs.append("N'entrez aucune information personnelle avant vérification")
        return recs

    else:  # safe
        recs = ["✓ Cette URL semble légitime et sûre à visiter"]

        if fd.get('is_https', 0) == 1:
            recs.append("✓ Connexion sécurisée par HTTPS")
        else:
            recs.append("Conseil : préférez toujours la version HTTPS d'un site")

        recs.append("✓ Aucun indicateur de phishing détecté par notre modèle d'IA")
        recs.append("Restez vigilant : vérifiez toujours l'URL avant de saisir des informations sensibles")
        return recs
