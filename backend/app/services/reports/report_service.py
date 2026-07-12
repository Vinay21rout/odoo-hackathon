from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from typing import Dict, Any

from app.models.reports.report import SavedReport
from app.models.organization.user import User
from app.models.environmental.metric import EnvironmentalRecord
from app.models.social.metric import SocialRecord
from app.models.governance.metric import GovernanceRecord
from app.schemas.reports.report import ReportCreate, ReportUpdate
from app.services.common.crud import CRUDBase
from app.core.logger import logger

class CRUDReport(CRUDBase[SavedReport]):
    def create(self, db: Session, *, obj_in: ReportCreate) -> SavedReport:
        user = db.query(User).filter(User.id == obj_in.user_id, User.is_active == True).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with ID '{obj_in.user_id}' does not exist or is inactive."
            )
        logger.info(f"Saving compiled report '{obj_in.title}' for user {obj_in.user_id}")
        return super().create(db, obj_in=obj_in)

    def generate_dynamic_esg_report(self, db: Session) -> Dict[str, Any]:
        logger.info("Generating dynamic ESG report summary")
        
        # Environmental aggregation (carbon emissions, energy, etc.)
        env_breakdown = (
            db.query(EnvironmentalRecord.metric_type, func.sum(EnvironmentalRecord.value))
            .filter(EnvironmentalRecord.is_active == True)
            .group_by(EnvironmentalRecord.metric_type)
            .all()
        )
        environmental_summary = {
            "carbon": 0.0,
            "energy": 0.0,
            "water": 0.0,
            "waste": 0.0
        }
        for metric_type, total in env_breakdown:
            environmental_summary[metric_type] = total or 0.0

        # Social aggregation (training hours, incidents, etc.)
        social_breakdown = (
            db.query(SocialRecord.metric_type, func.sum(SocialRecord.value))
            .filter(SocialRecord.is_active == True)
            .group_by(SocialRecord.metric_type)
            .all()
        )
        social_summary = {
            "training_hours": 0.0,
            "health_safety_incidents": 0.0,
            "diversity_ratio": 0.0,
            "community_hours": 0.0
        }
        for metric_type, total in social_breakdown:
            social_summary[metric_type] = total or 0.0

        # Governance aggregation (whistleblower reports, etc.)
        gov_breakdown = (
            db.query(GovernanceRecord.metric_type, func.count(GovernanceRecord.id))
            .filter(GovernanceRecord.is_active == True)
            .group_by(GovernanceRecord.metric_type)
            .all()
        )
        governance_summary = {
            "whistleblower_reports": 0,
            "policy_violations": 0,
            "board_diversity": 0
        }
        for metric_type, count in gov_breakdown:
            governance_summary[metric_type] = count or 0

        return {
            "environmental": environmental_summary,
            "social": social_summary,
            "governance": governance_summary,
            "generated_at": datetime.utcnow().isoformat()
        }

report_service = CRUDReport(SavedReport)
