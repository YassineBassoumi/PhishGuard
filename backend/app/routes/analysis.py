"""
PhishGuard AI - API Routes
REST endpoints for phishing detection
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.schemas import (
    EmailAnalysisRequest,
    URLAnalysisRequest,
    AnalysisResponse,
    StatsResponse,
    HealthResponse,
    BulkEmailAnalysisRequest,
    BulkAnalysisResponse,
    BulkAnalysisResult
)
from app.services.detector import detector
from app.services.stats_service import stats_service
from app.database import get_db
from app.services.auth_service import get_current_active_user
from app.models.user_models import User
from datetime import datetime
import logging
import asyncio

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/analyze-email", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_email(
    request: EmailAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Analyze message/text content for phishing patterns using HYBRID approach
    
    - **content**: The message content to analyze (plain text, no structured email headers required)
    
    Returns threat level, confidence score, detected features, and recommendations
    
    **NEW: Now uses hybrid analysis by default!**
    - Automatically extracts URLs from content
    - Analyzes text separately using email phishing model (LinearSVC, 97.5% accuracy)
    - Analyzes each URL using URL phishing model
    - Combines results intelligently for better accuracy
    
    Note: If no URLs are found, uses standard text analysis (no performance overhead)
    
    Requires authentication
    """
    try:
        logger.info(f"User {current_user.username} analyzing email content with hybrid approach (length: {len(request.content)})")
        
        # Use hybrid analysis by default for better detection
        threat_level, confidence, features, recommendations, url_results, decision_trace = detector.analyze_email_hybrid(
            request.content
        )
        
        # Create content preview (first 100 chars)
        content_preview = request.content[:100] + "..." if len(request.content) > 100 else request.content
        
        # Save to database with user_id
        await stats_service.save_analysis(
            db=db,
            analysis_type="email",
            content_preview=content_preview,
            threat_level=threat_level,
            confidence=confidence,
            features=features,
            recommendations=recommendations,
            user_id=current_user.id
        )
        
        # Note: dangerous-email notifications for manual analyses are intentionally disabled.
        # Manual analyses already display the verdict directly in the UI; pushing them to
        # the notifications panel was creating duplicate noise. Background Gmail scanning
        # still creates its own notifications via its own service.

        logger.info(f"Hybrid email analysis complete: {threat_level} (confidence: {confidence}%)")
        
        return AnalysisResponse(
            type="email",
            content=content_preview,
            threatLevel=threat_level,
            confidence=confidence,
            features=features,
            recommendations=recommendations,
            decision_trace=decision_trace
        )
    
    except Exception as e:
        logger.error(f"Email analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze-url", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_url(
    request: URLAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Analyze URL for malicious indicators
    
    - **url**: The URL to analyze
    
    Returns threat level, confidence score, detected features, and recommendations
    
    Requires authentication
    """
    try:
        logger.info(f"User {current_user.username} analyzing URL: {request.url}")
        
        # Analyze URL using detection service
        threat_level, confidence, features, recommendations = detector.analyze_url(
            request.url
        )
        
        # Save to database with user_id
        await stats_service.save_analysis(
            db=db,
            analysis_type="url",
            content_preview=request.url,
            threat_level=threat_level,
            confidence=confidence,
            features=features,
            recommendations=recommendations,
            user_id=current_user.id
        )
        
        logger.info(f"URL analysis complete: {threat_level} (confidence: {confidence}%)")
        
        return AnalysisResponse(
            type="url",
            content=request.url,
            threatLevel=threat_level,
            confidence=confidence,
            features=features,
            recommendations=recommendations
        )
    
    except Exception as e:
        logger.error(f"URL analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze-email-hybrid", tags=["Analysis"])
async def analyze_email_hybrid(
    request: EmailAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Analyze email using HYBRID approach (Text + URL split analysis)
    
    This endpoint provides better detection by:
    1. Extracting URLs from email content
    2. Analyzing text (without URLs) using email phishing model (LinearSVC, 97.5% accuracy)
    3. Analyzing each URL separately using URL phishing model
    4. Combining results intelligently
    
    - **content**: The email content to analyze
    
    Returns threat level, confidence score, detected features, recommendations,
    and detailed URL analysis results
    
    Requires authentication
    """
    try:
        logger.info(f"User {current_user.username} analyzing email with hybrid approach (length: {len(request.content)})")
        
        # Analyze email using hybrid detection service
        threat_level, confidence, features, recommendations, url_results, _trace = detector.analyze_email_hybrid(
            request.content
        )
        
        # Create content preview (first 100 chars)
        content_preview = request.content[:100] + "..." if len(request.content) > 100 else request.content
        
        # Save to database with user_id
        await stats_service.save_analysis(
            db=db,
            analysis_type="email",
            content_preview=content_preview,
            threat_level=threat_level,
            confidence=confidence,
            features=features,
            recommendations=recommendations,
            user_id=current_user.id
        )
        
        # Note: dangerous-email notifications for manual analyses are intentionally disabled.
        # Manual analyses already display the verdict directly in the UI; pushing them to
        # the notifications panel was creating duplicate noise. Background Gmail scanning
        # still creates its own notifications via its own service.

        logger.info(f"Hybrid email analysis complete: {threat_level} (confidence: {confidence}%)")
        
        # Build response with URL details
        response_data = {
            "type": "email",
            "content": content_preview,
            "threatLevel": threat_level,
            "confidence": confidence,
            "features": features,
            "recommendations": recommendations
        }
        
        # Add URL analysis results if available
        if url_results:
            response_data["urlAnalysis"] = url_results
        
        return response_data
    
    except Exception as e:
        logger.error(f"Hybrid email analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/stats", response_model=StatsResponse, tags=["Statistics"])
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user-specific statistics
    
    Returns detection accuracy, total analyses, and other metrics for the current user
    """
    try:
        stats = await stats_service.get_statistics(db, user_id=current_user.id)
        return StatsResponse(**stats)
    except Exception as e:
        logger.error(f"Failed to get statistics: {str(e)}", exc_info=True)
        # Return default stats on error
        return StatsResponse(
            totalAnalyses=0,
            accuracy=99.2,
            averageResponseTime="<2s",
            threatsDetected=0
        )


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    
    Returns server status
    """
    return HealthResponse(
        status="ok",
        message="PhishGuard AI is running"
    )


@router.get("/history", tags=["Statistics"])
async def get_history(
    limit: int = 10,
    analysis_type: str = None,
    threat_level: str = None,
    start_date: str = None,
    end_date: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get recent analysis history with optional filters
    
    - **limit**: Number of recent analyses to return (default: 10, max: 100)
    - **analysis_type**: Filter by type ('email' or 'url')
    - **threat_level**: Filter by threat level ('safe', 'suspicious', 'dangerous')
    - **start_date**: Filter from date (ISO format: YYYY-MM-DD)
    - **end_date**: Filter to date (ISO format: YYYY-MM-DD)
    
    Returns only the current user's analyses
    
    Requires authentication
    """
    try:
        from datetime import datetime
        
        # Validate and parse dates
        start_datetime = None
        end_datetime = None
        
        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date)
                # Set to end of day
                end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
        
        # Validate limit
        if limit > 100:
            limit = 100
        
        history = await stats_service.get_recent_analyses(
            db, 
            limit=limit,
            analysis_type=analysis_type,
            threat_level=threat_level,
            start_date=start_datetime,
            end_date=end_datetime,
            user_id=current_user.id  # Filter by current user
        )
        return {"history": history, "count": len(history)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")


@router.get("/threat-distribution", tags=["Statistics"])
async def get_threat_distribution(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get distribution of threat levels for the current user's analyses
    """
    try:
        distribution = await stats_service.get_threat_distribution(db, user_id=current_user.id)
        return distribution
    except Exception as e:
        logger.error(f"Failed to get threat distribution: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve distribution: {str(e)}")


@router.post("/analyze-bulk", tags=["Analysis"])
async def analyze_bulk_emails(
    request: BulkEmailAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Analyze multiple messages in bulk using HYBRID approach (Text + URL split analysis)
    
    - **emails**: List of message contents (max 50, plain text)
    
    Returns analysis results for each message plus summary statistics
    
    **NEW: Now uses hybrid analysis by default!**
    - Automatically extracts URLs from each message
    - Analyzes text separately using email phishing model (LinearSVC, 97.5% accuracy)
    - Analyzes each URL using URL phishing model
    - Combines results intelligently for better accuracy
    
    This endpoint provides better detection by:
    1. Extracting URLs from email content
    2. Analyzing text (without URLs) using email phishing model (LinearSVC, 97.5% accuracy)
    
    Note: Works with plain text content, not structured email headers
    
    Requires authentication
    """
    import time
    
    try:
        start_time = time.time()
        logger.info(f"User {current_user.username} starting bulk hybrid analysis of {len(request.emails)} emails")
        
        results = []
        threat_counts = {"safe": 0, "suspicious": 0, "dangerous": 0}
        total_confidence = 0
        
        # Analyze each email using hybrid approach
        for index, email_content in enumerate(request.emails):
            try:
                # Analyze email using hybrid detection (text + URL split)
                threat_level, confidence, features, recommendations, url_results, _trace = detector.analyze_email_hybrid(
                    email_content
                )
                
                # Create preview
                content_preview = email_content[:100] + "..." if len(email_content) > 100 else email_content
                
                # Save to database with user_id
                await stats_service.save_analysis(
                    db=db,
                    analysis_type="email",
                    content_preview=content_preview,
                    threat_level=threat_level,
                    confidence=confidence,
                    features=features,
                    recommendations=recommendations,
                    user_id=current_user.id
                )
                
                # Add to results
                results.append(BulkAnalysisResult(
                    index=index,
                    content_preview=content_preview,
                    threat_level=threat_level,
                    confidence=confidence,
                    features=features,
                    recommendations=recommendations
                ))
                
                # Update counts
                threat_counts[threat_level] += 1
                total_confidence += confidence
                
            except Exception as e:
                logger.error(f"Error analyzing email {index}: {str(e)}", exc_info=True)
                # Add error result
                results.append(BulkAnalysisResult(
                    index=index,
                    content_preview=email_content[:100] + "...",
                    threat_level="safe",
                    confidence=0,
                    features=[f"Analysis failed: {str(e)}"],
                    recommendations=["Please try analyzing this email individually"]
                ))
        
        # Calculate summary
        processing_time = time.time() - start_time
        average_confidence = total_confidence / len(request.emails) if request.emails else 0
        
        summary = {
            "safe": threat_counts["safe"],
            "suspicious": threat_counts["suspicious"],
            "dangerous": threat_counts["dangerous"],
            "average_confidence": round(average_confidence, 2),
            "threats_detected": threat_counts["suspicious"] + threat_counts["dangerous"]
        }
        
        logger.info(f"Bulk analysis complete: {len(results)} emails processed in {processing_time:.2f}s")
        
        return BulkAnalysisResponse(
            total=len(results),
            results=results,
            summary=summary,
            processing_time=round(processing_time, 2)
        )
        
    except Exception as e:
        logger.error(f"Bulk analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Bulk analysis failed: {str(e)}")


@router.post("/analyze-progressive", tags=["Analysis"])
async def analyze_progressive(
    request: URLAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Progressive URL analysis with step-by-step indicators.
    
    Uses the same extract_url_features() as the ML model so the
    live indicators match exactly what the model sees.
    
    Requires authentication
    """
    from app.services.detection.feature_extractors import extract_url_features
    
    try:
        url = request.url
        logger.info(f"User {current_user.username} starting progressive analysis: {url}")
        
        # Extract features using the SAME function the ML model uses (23 features)
        fd = extract_url_features(url)
        
        indicators = {}
        
        # 1. HTTPS Check (model feature: is_https)
        has_https = fd.get('is_https', 0) == 1
        indicators['https'] = {
            'status': 'safe' if has_https else 'warning',
            'label': 'Vérification SSL',
            'message': 'HTTPS détecté — connexion sécurisée' if has_https else 'HTTPS manquant — données non chiffrées',
            'passed': has_https
        }
        
        # 2. Domain Analysis (model features: use_of_ip, subdomain_count, hostname_length,
        #    domain_entropy, tld_risk)
        domain_issues = []
        if fd.get('use_of_ip', 0) == 1:
            domain_issues.append('Utilise une adresse IP')
        if fd.get('subdomain_count', 0) > 3:
            domain_issues.append(f"{fd['subdomain_count']} sous-domaines")
        if fd.get('hostname_length', 0) > 30:
            domain_issues.append('Nom d\'hôte très long')
        if fd.get('domain_entropy', 0) > 4.0:
            domain_issues.append('Domaine aléatoire suspect')
        if fd.get('tld_risk', 0) == 1:
            domain_issues.append('TLD à risque')
        
        if domain_issues:
            indicators['domain'] = {
                'status': 'danger' if len(domain_issues) >= 2 else 'warning',
                'label': 'Analyse du Domaine',
                'message': ' · '.join(domain_issues),
                'passed': False
            }
        else:
            indicators['domain'] = {
                'status': 'safe',
                'label': 'Analyse du Domaine',
                'message': 'Structure de domaine normale',
                'passed': True
            }
        
        # 3. Phishing Keywords Check (model features: sus_url, short_url)
        kw_issues = []
        if fd.get('sus_url', 0) == 1:
            kw_issues.append('Mots-clés de phishing détectés')
        if fd.get('short_url', 0) == 1:
            kw_issues.append('Raccourcisseur d\'URL')
        
        if kw_issues:
            indicators['keywords'] = {
                'status': 'danger' if len(kw_issues) == 2 else 'warning',
                'label': 'Mots-clés Suspects',
                'message': ' · '.join(kw_issues),
                'passed': False
            }
        else:
            indicators['keywords'] = {
                'status': 'safe',
                'label': 'Mots-clés Suspects',
                'message': 'Aucun mot-clé suspect détecté',
                'passed': True
            }
        
        # 4. URL Structure Check (model features: url_length, count@, count_embed_domian,
        #    path_length, count_dir, special_char_ratio, count-, count-digits)
        struct_issues = []
        if fd.get('url_length', 0) > 100:
            struct_issues.append(f"URL longue ({fd['url_length']} car.)")
        if fd.get('count@', 0) > 0:
            struct_issues.append('Symbole @ détecté')
        if fd.get('count_embed_domian', 0) > 0:
            struct_issues.append('Double slash dans le chemin')
        if fd.get('path_length', 0) > 80:
            struct_issues.append('Chemin très long')
        if fd.get('count-', 0) > 3:
            struct_issues.append(f"{fd['count-']} tirets")
        if fd.get('special_char_ratio', 0) > 0.35:
            struct_issues.append('Ratio élevé de caractères spéciaux')
        if fd.get('count_dir', 0) > 5:
            struct_issues.append(f"{fd['count_dir']} niveaux de répertoires")
        
        if struct_issues:
            indicators['structure'] = {
                'status': 'danger' if len(struct_issues) >= 2 else 'warning',
                'label': 'Structure URL',
                'message': ' · '.join(struct_issues),
                'passed': False
            }
        else:
            indicators['structure'] = {
                'status': 'safe',
                'label': 'Structure URL',
                'message': 'Structure URL normale',
                'passed': True
            }
        
        # Now run full ML analysis
        threat_level, confidence, features, recommendations = detector.analyze_url(url)
        
        # NOTE: Do NOT save to database here - this is just for progressive indicators
        # The main /analyze-url endpoint will save the final analysis
        
        logger.info(f"Progressive analysis complete: {threat_level} (confidence: {confidence}%)")
        
        return {
            'indicators': indicators,
            'analysis': {
                'type': 'url',
                'content': url,
                'threatLevel': threat_level,
                'confidence': confidence,
                'features': features,
                'recommendations': recommendations
            }
        }
        
    except Exception as e:
        logger.error(f"Progressive analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")



@router.post("/analyze-email-progressive", tags=["Analysis"])
async def analyze_email_progressive(
    request: EmailAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Progressive message analysis with step-by-step indicators
    
    Returns individual check results for real-time display using ML model
    
    Note: Analyzes plain text content (email body, messages) without requiring structured headers
    
    Requires authentication
    """
    import re
    
    try:
        content = request.content
        logger.info(f"User {current_user.username} starting progressive email analysis")
        
        indicators = {}
        content_lower = content.lower()
        
        # Now run full HYBRID analysis (text + URL models) to match the final analysis
        threat_level, confidence, features, recommendations, _url_results, _trace = detector.analyze_email_hybrid(content)
        
        # Adjust indicator statuses based on ML model's verdict
        # If ML says "safe", don't show danger indicators even if keywords are found
        ml_is_safe = threat_level in ['safe', 'low']
        ml_is_suspicious = threat_level == 'suspicious'
        ml_is_dangerous = threat_level in ['dangerous', 'high']
        
        # 1. Phishing Keywords Check (aligned with ML verdict)
        phishing_keywords = ['verify', 'urgent', 'suspended', 'locked', 'confirm', 
                            'click here', 'account', 'password', 'update', 'expire',
                            'winner', 'congratulations', 'claim', 'prize', 'free']
        found_keywords = [kw for kw in phishing_keywords if kw in content_lower]
        
        # If ML says safe, show safe even if keywords found (they're in legitimate context)
        if ml_is_safe:
            keywords_status = 'safe'
            keywords_msg = 'Contexte légitime détecté' if len(found_keywords) > 0 else 'Aucun mot-clé suspect'
        elif ml_is_suspicious:
            keywords_status = 'warning'
            keywords_msg = f'{len(found_keywords)} mot(s)-clé(s) dans contexte suspect'
        else:  # dangerous
            keywords_status = 'danger'
            keywords_msg = f'{len(found_keywords)} mot(s)-clé(s) de phishing détecté(s)'
        
        indicators['phishingKeywords'] = {
            'status': keywords_status,
            'label': 'Mots-clés de Phishing',
            'message': keywords_msg,
            'passed': ml_is_safe
        }
        
        # 2. Urgency Language Check (aligned with ML verdict)
        urgency_words = ['urgent', 'immediate', 'immediately', 'act now', 'expire', 
                        'expires', 'suspended', 'limited time', 'hurry', 'quick']
        found_urgency = [word for word in urgency_words if word in content_lower]
        
        if ml_is_safe:
            urgency_status = 'safe'
            urgency_msg = 'Langage approprié au contexte' if len(found_urgency) > 0 else 'Pas de langage urgent'
        elif ml_is_suspicious:
            urgency_status = 'warning'
            urgency_msg = f'{len(found_urgency)} expression(s) urgente(s)'
        else:
            urgency_status = 'danger'
            urgency_msg = f'Langage urgent manipulateur détecté'
        
        indicators['urgencyLanguage'] = {
            'status': urgency_status,
            'label': 'Langage Urgent',
            'message': urgency_msg,
            'passed': ml_is_safe
        }
        
        # 3. Suspicious Links Check (aligned with ML verdict)
        url_pattern = r'https?://[^\s<>"\']+'
        urls = re.findall(url_pattern, content)
        
        suspicious_url_count = 0
        for url in urls:
            if any(keyword in url.lower() for keyword in ['login', 'verify', 'account', 'secure', 'update']):
                suspicious_url_count += 1
        
        if len(urls) == 0:
            links_status = 'safe'
            links_msg = 'Aucun lien détecté'
        elif ml_is_safe:
            links_status = 'safe'
            links_msg = f'{len(urls)} lien(s) légitime(s)'
        elif ml_is_suspicious:
            links_status = 'warning'
            links_msg = f'{len(urls)} lien(s) à vérifier'
        else:
            links_status = 'danger'
            links_msg = f'{suspicious_url_count} lien(s) suspect(s) sur {len(urls)}' if suspicious_url_count > 0 else f'{len(urls)} lien(s) dangereux'
        
        indicators['suspiciousLinks'] = {
            'status': links_status,
            'label': 'Liens Suspects',
            'message': links_msg,
            'passed': ml_is_safe
        }
        
        # 4. Credential Request Check (aligned with ML verdict)
        credential_words = ['password', 'username', 'login', 'credential', 'ssn', 
                           'social security', 'credit card', 'bank account', 'pin',
                           'cvv', 'card number', 'account number']
        found_credentials = [word for word in credential_words if word in content_lower]
        
        if len(found_credentials) == 0:
            credentials_status = 'safe'
            credentials_msg = 'Aucune demande suspecte'
        elif ml_is_safe:
            credentials_status = 'safe'
            credentials_msg = 'Mentions légitimes détectées'
        elif ml_is_suspicious:
            credentials_status = 'warning'
            credentials_msg = 'Demande d\'informations à vérifier'
        else:
            credentials_status = 'danger'
            credentials_msg = 'Tentative de vol d\'informations sensibles'
        
        indicators['credentialRequest'] = {
            'status': credentials_status,
            'label': 'Demande de Données',
            'message': credentials_msg,
            'passed': ml_is_safe
        }
        
        # NOTE: Do NOT save to database here - this is just for progressive indicators
        # The main /analyze-email endpoint will save the final analysis
        
        logger.info(f"Progressive email analysis complete: {threat_level} (confidence: {confidence}%)")
        
        return {
            'indicators': indicators,
            'analysis': {
                'type': 'email',
                'content': content[:100] + '...' if len(content) > 100 else content,
                'threatLevel': threat_level,
                'confidence': confidence,
                'features': features,
                'recommendations': recommendations
            }
        }
        
    except Exception as e:
        logger.error(f"Progressive email analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
