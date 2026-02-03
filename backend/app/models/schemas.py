from typing import List, Optional
from pydantic import BaseModel, Field


# Request Models
class EmailAnalysisRequest(BaseModel):
    """Request model for email analysis"""
    content: str = Field(..., min_length=1, description="Email content to analyze")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "Dear user, Your account has been locked. Click here to verify: http://suspicious-link.com"
            }
        }


class URLAnalysisRequest(BaseModel):
    """Request model for URL analysis"""
    url: str = Field(..., min_length=1, description="URL to analyze")
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "http://paypa1-verify.com/account/login"
            }
        }


# Response Models
class AnalysisResponse(BaseModel):
    """Unified response model for analysis results"""
    type: str = Field(..., description="Type of analysis: 'email' or 'url'")
    content: str = Field(..., description="Preview of analyzed content")
    threatLevel: str = Field(..., description="Threat level: 'safe', 'suspicious', or 'dangerous'")
    confidence: float = Field(..., ge=0, le=100, description="Confidence score (0-100)")
    features: List[str] = Field(default_factory=list, description="Detected phishing patterns")
    recommendations: List[str] = Field(default_factory=list, description="Security recommendations")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "email",
                "content": "Dear user, Your account has been locked...",
                "threatLevel": "dangerous",
                "confidence": 92.5,
                "features": [
                    "Suspicious sender domain detected",
                    "Urgency language detected",
                    "Potential phishing keywords found"
                ],
                "recommendations": [
                    "Do not click any links in this email",
                    "Verify sender through official channels",
                    "Report to IT security team"
                ]
            }
        }


class StatsResponse(BaseModel):
    """Platform statistics response"""
    totalAnalyses: int = Field(..., description="Total number of analyses performed")
    accuracy: float = Field(..., description="Detection accuracy percentage")
    averageResponseTime: str = Field(..., description="Average analysis time")
    threatsDetected: int = Field(..., description="Total threats detected")
    
    class Config:
        json_schema_extra = {
            "example": {
                "totalAnalyses": 15420,
                "accuracy": 99.2,
                "averageResponseTime": "<2s",
                "threatsDetected": 8934
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str = "PhishGuard AI is running"


class BulkEmailAnalysisRequest(BaseModel):
    """Request model for bulk email analysis"""
    emails: List[str] = Field(..., min_length=1, max_length=50, description="List of email contents to analyze")
    
    class Config:
        json_schema_extra = {
            "example": {
                "emails": [
                    "Dear user, Your account has been locked...",
                    "Hello, Your package is ready for delivery...",
                    "Urgent: Verify your payment information..."
                ]
            }
        }


class BulkAnalysisResult(BaseModel):
    """Individual result in bulk analysis"""
    index: int = Field(..., description="Index of the email in the batch")
    content_preview: str = Field(..., description="Preview of analyzed content")
    threat_level: str = Field(..., description="Threat level")
    confidence: float = Field(..., ge=0, le=100, description="Confidence score")
    features: List[str] = Field(default_factory=list, description="Detected features")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")


class BulkAnalysisResponse(BaseModel):
    """Response model for bulk email analysis"""
    total: int = Field(..., description="Total number of emails analyzed")
    results: List[BulkAnalysisResult] = Field(..., description="Individual analysis results")
    summary: dict = Field(..., description="Summary statistics")
    processing_time: float = Field(..., description="Total processing time in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 3,
                "results": [
                    {
                        "index": 0,
                        "content_preview": "Dear user, Your account...",
                        "threat_level": "dangerous",
                        "confidence": 92.5,
                        "features": ["Urgency language detected"],
                        "recommendations": ["Delete this email immediately"]
                    }
                ],
                "summary": {
                    "safe": 1,
                    "suspicious": 1,
                    "dangerous": 1,
                    "average_confidence": 85.3
                },
                "processing_time": 2.45
            }
        }
