"""
Statistics Service
Handles analysis history and statistics tracking
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.database_models import AnalysisHistory, Statistics
from typing import Dict, List
from datetime import datetime


class StatsService:
    """Service for managing statistics and analysis history"""
    
    @staticmethod
    async def save_analysis(
        db: AsyncSession,
        analysis_type: str,
        content_preview: str,
        threat_level: str,
        confidence: float,
        features: List[str],
        recommendations: List[str],
        user_id: int = None
    ) -> AnalysisHistory:
        """Save analysis to history"""
        analysis = AnalysisHistory(
            user_id=user_id,
            analysis_type=analysis_type,
            content_preview=content_preview,
            threat_level=threat_level,
            confidence=confidence,
            features=features,
            recommendations=recommendations
        )
        db.add(analysis)
        await db.flush()
        
        # Update statistics
        await StatsService._update_statistics(db, analysis_type, threat_level)
        
        return analysis
    
    @staticmethod
    async def _update_statistics(db: AsyncSession, analysis_type: str, threat_level: str):
        """Update platform statistics"""
        # Get or create statistics record
        result = await db.execute(select(Statistics).limit(1))
        stats = result.scalar_one_or_none()
        
        if not stats:
            stats = Statistics(
                total_analyses=0,
                threats_detected=0,
                emails_analyzed=0,
                urls_analyzed=0
            )
            db.add(stats)
        
        # Update counts
        stats.total_analyses += 1
        
        if analysis_type == "email":
            stats.emails_analyzed += 1
        else:
            stats.urls_analyzed += 1
        
        if threat_level in ["suspicious", "dangerous"]:
            stats.threats_detected += 1
        
        stats.last_updated = datetime.utcnow()
    
    @staticmethod
    async def get_statistics(db: AsyncSession, user_id: int = None) -> Dict:
        """Get statistics for a specific user or platform-wide"""
        if user_id:
            # Get user-specific statistics
            # Count total analyses for this user
            total_result = await db.execute(
                select(func.count(AnalysisHistory.id))
                .where(AnalysisHistory.user_id == user_id)
            )
            total_analyses = total_result.scalar() or 0
            
            # Count threats detected for this user
            threats_result = await db.execute(
                select(func.count(AnalysisHistory.id))
                .where(AnalysisHistory.user_id == user_id)
                .where(AnalysisHistory.threat_level.in_(["suspicious", "dangerous"]))
            )
            threats_detected = threats_result.scalar() or 0
            
            return {
                "totalAnalyses": total_analyses,
                "accuracy": 99.2,  # This would be calculated from actual data
                "averageResponseTime": "<2s",
                "threatsDetected": threats_detected
            }
        else:
            # Get platform-wide statistics
            result = await db.execute(select(Statistics).limit(1))
            stats = result.scalar_one_or_none()
            
            if not stats:
                return {
                    "totalAnalyses": 0,
                    "accuracy": 99.2,
                    "averageResponseTime": "<2s",
                    "threatsDetected": 0
                }
            
            return {
                "totalAnalyses": stats.total_analyses,
                "accuracy": 99.2,  # This would be calculated from actual data
                "averageResponseTime": "<2s",
                "threatsDetected": stats.threats_detected
            }
    
    @staticmethod
    async def get_recent_analyses(
        db: AsyncSession, 
        limit: int = 10,
        analysis_type: str = None,
        threat_level: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        user_id: int = None
    ) -> List[Dict]:
        """Get recent analysis history with optional filters"""
        query = select(AnalysisHistory)
        
        # Filter by user if provided
        if user_id:
            query = query.where(AnalysisHistory.user_id == user_id)
        
        # Apply filters
        if analysis_type:
            query = query.where(AnalysisHistory.analysis_type == analysis_type)
        
        if threat_level:
            query = query.where(AnalysisHistory.threat_level == threat_level)
        
        if start_date:
            query = query.where(AnalysisHistory.created_at >= start_date)
        
        if end_date:
            query = query.where(AnalysisHistory.created_at <= end_date)
        
        # Order and limit
        query = query.order_by(AnalysisHistory.created_at.desc()).limit(limit)
        
        result = await db.execute(query)
        analyses = result.scalars().all()
        
        return [
            {
                "id": a.id,
                "type": a.analysis_type,
                "content": a.content_preview,
                "threatLevel": a.threat_level,
                "confidence": a.confidence,
                "features": a.features,
                "recommendations": a.recommendations,
                "timestamp": a.created_at.isoformat()
            }
            for a in analyses
        ]
    
    @staticmethod
    async def get_threat_distribution(db: AsyncSession, user_id: int = None) -> Dict:
        """Get distribution of threat levels for a specific user or platform-wide"""
        query = select(
            AnalysisHistory.threat_level,
            func.count(AnalysisHistory.id).label('count')
        )
        
        # Filter by user if provided
        if user_id:
            query = query.where(AnalysisHistory.user_id == user_id)
        
        query = query.group_by(AnalysisHistory.threat_level)
        
        result = await db.execute(query)
        
        distribution = {row.threat_level: row.count for row in result}
        
        return {
            "safe": distribution.get("safe", 0),
            "suspicious": distribution.get("suspicious", 0),
            "dangerous": distribution.get("dangerous", 0)
        }


# Singleton instance
stats_service = StatsService()
