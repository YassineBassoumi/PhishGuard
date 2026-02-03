"""
Database models for storing analysis history
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.sql import func
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
    """Store platform statistics"""
    __tablename__ = "statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    total_analyses = Column(Integer, default=0)
    threats_detected = Column(Integer, default=0)
    emails_analyzed = Column(Integer, default=0)
    urls_analyzed = Column(Integer, default=0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Statistics(total={self.total_analyses}, threats={self.threats_detected})>"
