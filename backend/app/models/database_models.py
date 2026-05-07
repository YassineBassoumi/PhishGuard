"""
Database models for storing analysis history
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.sql import func, text
from sqlalchemy.orm import relationship
from app.database import Base


class AnalysisHistory(Base):
    """Store analysis history"""
    __tablename__ = "analysis_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    analysis_type = Column(String(10), nullable=False)  # 'email' or 'url'
    content_preview = Column(Text, nullable=False)
    threat_level = Column(String(20), nullable=False)  # 'safe', 'suspicious', 'dangerous'
    confidence = Column(Float, nullable=False)
    features = Column(JSON, nullable=True)  # Store as JSON array
    recommendations = Column(JSON, nullable=True)  # Store as JSON array
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    user = relationship("User", back_populates="analyses")
    
    def __repr__(self):
        return f"<AnalysisHistory(id={self.id}, type={self.analysis_type}, threat={self.threat_level})>"


class Statistics(Base):
    """Aggregated analysis statistics (global or per-user).

    Design:
        - One row with user_id IS NULL holds the platform-wide aggregates
          (singleton). This row is queried by admin / global dashboards.
        - Each authenticated user gets at most one row with user_id = their ID,
          updated lazily on first analysis. This row is queried by the
          per-user personal dashboard in O(1) instead of scanning
          analysis_history with COUNT(*).
        - Both rows are kept in sync by StatsService._update_statistics(),
          which writes to global + (optionally) per-user on every analysis.
    """
    __tablename__ = "statistics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        unique=True,
        index=True,
    )
    total_analyses = Column(Integer, default=0, nullable=False)
    threats_detected = Column(Integer, default=0, nullable=False)
    emails_analyzed = Column(Integer, default=0, nullable=False)
    urls_analyzed = Column(Integer, default=0, nullable=False)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship: each user has zero or one Statistics row
    user = relationship("User", back_populates="statistics")

    # Enforce that at most ONE row may have user_id IS NULL (the global singleton).
    # PostgreSQL allows multiple NULLs in a UNIQUE column by default, so we add
    # a partial unique index on a constant expression filtered to NULL rows.
    __table_args__ = (
        Index(
            "uq_statistics_global_singleton",
            text("(1)"),
            unique=True,
            postgresql_where=text("user_id IS NULL"),
        ),
    )

    def __repr__(self):
        scope = f"user={self.user_id}" if self.user_id is not None else "global"
        return f"<Statistics({scope}, total={self.total_analyses}, threats={self.threats_detected})>"
