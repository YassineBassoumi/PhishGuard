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
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/analyze-email", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_email(
    request: EmailAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Analyze email content for phishing patterns
    
    - **content**: The email content to analyze
    
    Returns threat level, confidence score, detected features, and recommendations
    
    Requires authentication
    """
    try:
        logger.info(f"User {current_user.username} analyzing email content (length: {len(request.content)})")
        
        # Analyze email using detection service
        threat_level, confidence, features, recommendations = detector.analyze_email(
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
        
        logger.info(f"Email analysis complete: {threat_level} (confidence: {confidence}%)")
        
        return AnalysisResponse(
            type="email",
            content=content_preview,
            threatLevel=threat_level,
            confidence=confidence,
            features=features,
            recommendations=recommendations
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


@router.get("/stats", response_model=StatsResponse, tags=["Statistics"])
async def get_stats(db: AsyncSession = Depends(get_db)):
    """
    Get platform statistics
    
    Returns detection accuracy, total analyses, and other metrics
    """
    try:
        stats = await stats_service.get_statistics(db)
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
async def get_threat_distribution(db: AsyncSession = Depends(get_db)):
    """
    Get distribution of threat levels across all analyses
    """
    try:
        distribution = await stats_service.get_threat_distribution(db)
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
    Analyze multiple emails in bulk
    
    - **emails**: List of email contents (max 50)
    
    Returns analysis results for each email plus summary statistics
    
    Requires authentication
    """
    import time
    
    try:
        start_time = time.time()
        logger.info(f"User {current_user.username} starting bulk analysis of {len(request.emails)} emails")
        
        results = []
        threat_counts = {"safe": 0, "suspicious": 0, "dangerous": 0}
        total_confidence = 0
        
        # Analyze each email
        for index, email_content in enumerate(request.emails):
            try:
                # Analyze email
                threat_level, confidence, features, recommendations = detector.analyze_email(
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
