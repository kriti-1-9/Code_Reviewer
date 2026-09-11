from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class CodeSnippet(BaseModel):
    language: Optional[str] = None
    filename: Optional[str] = None
    content: str
    diff: Optional[str] = None


class ReviewRequest(BaseModel):
    code: CodeSnippet
    repo: Optional[str] = None
    pr_number: Optional[int] = None
    context: Optional[str] = None  # extra team conventions / past notes


class Finding(BaseModel):
    severity: Literal["critical", "high", "medium", "low", "suggestion"]
    category: str  # security | correctness | performance | maintainability | style
    line: Optional[int] = None
    message: str
    suggestion: Optional[str] = None


class QualityScore(BaseModel):
    overall: float = Field(..., ge=0, le=100)
    correctness: float = Field(..., ge=0, le=100)
    security: float = Field(..., ge=0, le=100)
    performance: float = Field(..., ge=0, le=100)
    maintainability: float = Field(..., ge=0, le=100)
    style: float = Field(..., ge=0, le=100)


class ReviewResponse(BaseModel):
    review_id: str
    language: str
    quality: QualityScore
    findings: List[Finding]
    summary: str
    created_at: datetime


class FeedbackRequest(BaseModel):
    review_id: str
    finding_index: int
    action: Literal["accepted", "dismissed", "severity_override"]
    new_severity: Optional[str] = None
    comment: Optional[str] = None