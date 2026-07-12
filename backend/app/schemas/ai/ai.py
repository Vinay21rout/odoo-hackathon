from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    message: str = Field(..., description="Query message for the ESG chatbot")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional system or user metadata context")

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI generated response text")

class ReportGenerateRequest(BaseModel):
    report_type: str = Field(..., description="Focus audit type (environmental, social, governance, full)")
    timeframe: Optional[str] = Field("Q3", description="Financial or calendar quarter focus timeframe")

class ReportGenerateResponse(BaseModel):
    narrative: str = Field(..., description="Formal executive narrative summary")
    metrics_summarized: Dict[str, Any] = Field(..., description="Key database aggregates compiled")

class RecommendationRequest(BaseModel):
    focus_area: Optional[str] = Field(None, description="Specific ESG column to target")

class RecommendationItem(BaseModel):
    title: str
    description: str
    impact: str
    difficulty: str
    points_estimate: int

class RecommendationResponse(BaseModel):
    focus_area: str
    recommendations: List[RecommendationItem] = Field(..., description="List of action items")

class DashboardInsightItem(BaseModel):
    metric: str
    insight: str
    type: str  # positive, warning, info

class DashboardInsightResponse(BaseModel):
    insights: List[DashboardInsightItem]
    warnings: List[str]
