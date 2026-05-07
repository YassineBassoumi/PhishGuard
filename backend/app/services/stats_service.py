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
        """Save analysis to history and update aggregate counters."""
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

        # Maintain BOTH aggregate rows: the global singleton (user_id IS NULL)
        # and the per-user row (when user_id is provided).
        await StatsService._update_statistics(db, analysis_type, threat_level, user_id)

        return analysis

    @staticmethod
    async def _get_or_create_stats_row(db: AsyncSession, target_user_id) -> Statistics:
        """Fetch the Statistics row for a given scope, creating it on first use.

        target_user_id = None  -> the global singleton row.
        target_user_id = <int> -> the per-user aggregate row.
        """
        if target_user_id is None:
            stmt = select(Statistics).where(Statistics.user_id.is_(None))
        else:
            stmt = select(Statistics).where(Statistics.user_id == target_user_id)

        result = await db.execute(stmt)
        stats = result.scalar_one_or_none()

        if stats is None:
            stats = Statistics(
                user_id=target_user_id,
                total_analyses=0,
                threats_detected=0,
                emails_analyzed=0,
                urls_analyzed=0,
            )
            db.add(stats)
            await db.flush()

        return stats

    @staticmethod
    async def _update_statistics(
        db: AsyncSession,
        analysis_type: str,
        threat_level: str,
        user_id: int = None,
    ):
        """Increment counters on the global row and (optionally) the per-user row."""
        # Always update the global singleton (user_id IS NULL)
        targets = [None]
        # Also update the per-user row when authenticated
        if user_id is not None:
            targets.append(user_id)

        for target_user_id in targets:
            stats = await StatsService._get_or_create_stats_row(db, target_user_id)
            stats.total_analyses += 1
            if analysis_type == "email":
                stats.emails_analyzed += 1
            else:
                stats.urls_analyzed += 1
            if threat_level in ["suspicious", "dangerous"]:
                stats.threats_detected += 1
            # `last_updated` is automatically refreshed by PostgreSQL via
            # `onupdate=func.now()` declared on the column, no manual write needed.

    @staticmethod
    async def get_statistics(db: AsyncSession, user_id: int = None) -> Dict:
        """Get statistics for a specific user or platform-wide.

        O(1) lookup: reads directly from the materialised Statistics row
        (per-user when user_id is provided, global singleton otherwise).
        Falls back to a live COUNT(*) on analysis_history if the
        materialised row is missing (defensive, e.g. legacy data before
        migration).
        """
        if user_id:
            stmt = select(Statistics).where(Statistics.user_id == user_id)
        else:
            stmt = select(Statistics).where(Statistics.user_id.is_(None))

        result = await db.execute(stmt)
        stats = result.scalar_one_or_none()

        if stats is not None:
            return {
                "totalAnalyses": stats.total_analyses,
                "accuracy": 99.2,
                "averageResponseTime": "<2s",
                "threatsDetected": stats.threats_detected,
            }

        # Fallback: compute live from analysis_history (slower, used only
        # when the aggregate row hasn't been materialised yet).
        total_query = select(func.count(AnalysisHistory.id))
        threats_query = select(func.count(AnalysisHistory.id)).where(
            AnalysisHistory.threat_level.in_(["suspicious", "dangerous"])
        )
        if user_id:
            total_query = total_query.where(AnalysisHistory.user_id == user_id)
            threats_query = threats_query.where(AnalysisHistory.user_id == user_id)

        total_analyses = (await db.execute(total_query)).scalar() or 0
        threats_detected = (await db.execute(threats_query)).scalar() or 0

        return {
            "totalAnalyses": total_analyses,
            "accuracy": 99.2,
            "averageResponseTime": "<2s",
            "threatsDetected": threats_detected,
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
