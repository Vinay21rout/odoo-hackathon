from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.schemas.ai.ai import (
    ChatRequest, ChatResponse,
    ReportGenerateRequest, ReportGenerateResponse,
    RecommendationRequest, RecommendationResponse,
    DashboardInsightResponse
)
from app.services.ai.ai_service import ai_service
from app.services.common.response import success_response

router = APIRouter(prefix="/ai", tags=["AI Intelligence Engine"])

@router.post("/chat", response_model=None, status_code=status.HTTP_200_OK)
async def chat_with_esg_assistant(payload: ChatRequest, db: Session = Depends(get_db)):
    ai_reply = await ai_service.chat_assistant(db, payload.message)
    data = ChatResponse(response=ai_reply)
    return success_response(data=data, message="AI response generated successfully")

@router.post("/report", response_model=None, status_code=status.HTTP_200_OK)
async def generate_esg_narrative(payload: ReportGenerateRequest, db: Session = Depends(get_db)):
    report_text = await ai_service.generate_narrative_report(db, payload.report_type, payload.timeframe)
    esg_data = ai_service._get_esg_data(db)
    data = ReportGenerateResponse(narrative=report_text, metrics_summarized=esg_data)
    return success_response(data=data, message="AI Narrative report generated successfully")

@router.post("/recommendations", response_model=None, status_code=status.HTTP_200_OK)
async def get_esg_recommendations(payload: RecommendationRequest, db: Session = Depends(get_db)):
    focus = payload.focus_area or "general"
    recs = await ai_service.get_recommendations(db, focus)
    data = RecommendationResponse(focus_area=focus, recommendations=recs)
    return success_response(data=data, message="Actionable recommendations generated successfully")

@router.get("/insights", response_model=None, status_code=status.HTTP_200_OK)
async def get_dashboard_insights(db: Session = Depends(get_db)):
    insights_data = await ai_service.get_dashboard_insights(db)
    data = DashboardInsightResponse(
        insights=insights_data["insights"],
        warnings=insights_data["warnings"]
    )
    return success_response(data=data, message="Dashboard ESG insights generated successfully")
