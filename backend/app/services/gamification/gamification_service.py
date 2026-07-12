from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from uuid import UUID

from app.models.gamification.challenge import Challenge
from app.models.gamification.badge import Badge
from app.models.gamification.user_challenge import UserChallenge
from app.models.gamification.user_badge import UserBadge
from app.models.organization.user import User
from app.schemas.gamification.gamification import (
    ChallengeCreate, ChallengeUpdate,
    BadgeCreate, BadgeUpdate,
    UserChallengeCreate, UserChallengeUpdate,
    UserBadgeCreate, LeaderboardEntry
)
from app.services.common.crud import CRUDBase
from app.core.logger import logger

class CRUDChallenge(CRUDBase[Challenge]):
    pass

class CRUDBadge(CRUDBase[Badge]):
    pass

class CRUDUserChallenge(CRUDBase[UserChallenge]):
    def create(self, db: Session, *, obj_in: UserChallengeCreate) -> UserChallenge:
        user = db.query(User).filter(User.id == obj_in.user_id, User.is_active == True).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with ID '{obj_in.user_id}' does not exist or is inactive."
            )
        challenge = db.query(Challenge).filter(Challenge.id == obj_in.challenge_id, Challenge.is_active == True).first()
        if not challenge:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Challenge with ID '{obj_in.challenge_id}' does not exist or is inactive."
            )
        
        exists = db.query(UserChallenge).filter(
            UserChallenge.user_id == obj_in.user_id,
            UserChallenge.challenge_id == obj_in.challenge_id,
            UserChallenge.is_active == True
        ).first()
        if exists:
            return exists
            
        logger.info(f"User {obj_in.user_id} joining challenge {obj_in.challenge_id}")
        return super().create(db, obj_in=obj_in)

    def complete_challenge(self, db: Session, *, user_challenge_id: UUID) -> UserChallenge:
        uc = db.query(UserChallenge).filter(UserChallenge.id == user_challenge_id, UserChallenge.is_active == True).first()
        if not uc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User challenge progress record not found")
        
        uc.status = "completed"
        uc.completed_at = datetime.utcnow()
        db.add(uc)
        db.commit()
        db.refresh(uc)
        logger.info(f"User challenge progress {user_challenge_id} completed successfully")
        
        # Trigger notification
        from app.services.organization.notification import notification_service
        notification_service.trigger_notification(
            db,
            user_id=uc.user_id,
            message=f"You successfully completed the challenge '{uc.challenge.title}'! (+{uc.challenge.points_reward} XP)",
            notification_type="challenge"
        )
        
        # Check settings for badge auto-award
        from app.services.organization.settings import settings_service
        settings_obj = settings_service.get_active_settings(db)
        if settings_obj.badge_auto_award:
            leaderboard = get_leaderboard(db)
            user_points = 0
            for entry in leaderboard:
                if entry.user_id == uc.user_id:
                    user_points = entry.total_points
                    break
            
            from app.models.gamification.badge import Badge
            from app.models.gamification.user_badge import UserBadge
            badges = db.query(Badge).filter(Badge.is_active == True).all()
            earned_badge_ids = {ub.badge_id for ub in db.query(UserBadge).filter(
                UserBadge.user_id == uc.user_id,
                UserBadge.is_active == True
            ).all()}
            
            for badge in badges:
                if badge.id not in earned_badge_ids and user_points >= badge.points_target:
                    user_badge = UserBadge(user_id=uc.user_id, badge_id=badge.id)
                    db.add(user_badge)
                    notification_service.trigger_notification(
                        db,
                        user_id=uc.user_id,
                        message=f"Congratulations! You unlocked the '{badge.name}' badge!",
                        notification_type="badge"
                    )
            db.commit()
            db.refresh(uc)
            
        return uc

class CRUDUserBadge(CRUDBase[UserBadge]):
    def create(self, db: Session, *, obj_in: UserBadgeCreate) -> UserBadge:
        user = db.query(User).filter(User.id == obj_in.user_id, User.is_active == True).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with ID '{obj_in.user_id}' does not exist or is inactive."
            )
        badge = db.query(Badge).filter(Badge.id == obj_in.badge_id, Badge.is_active == True).first()
        if not badge:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Badge with ID '{obj_in.badge_id}' does not exist or is inactive."
            )
            
        exists = db.query(UserBadge).filter(
            UserBadge.user_id == obj_in.user_id,
            UserBadge.badge_id == obj_in.badge_id,
            UserBadge.is_active == True
        ).first()
        if exists:
            return exists
            
        logger.info(f"Assigning badge {obj_in.badge_id} to user {obj_in.user_id}")
        return super().create(db, obj_in=obj_in)

challenge_service = CRUDChallenge(Challenge)
badge_service = CRUDBadge(Badge)
user_challenge_service = CRUDUserChallenge(UserChallenge)
user_badge_service = CRUDUserBadge(UserBadge)

def get_leaderboard(db: Session) -> List[LeaderboardEntry]:
    logger.info("Retrieving gamification leaderboard")
    query = (
        db.query(
            User.id.label("user_id"),
            User.full_name.label("full_name"),
            User.email.label("email"),
            func.coalesce(func.sum(Challenge.points_reward), 0).label("total_points")
        )
        .outerjoin(
            UserChallenge,
            (UserChallenge.user_id == User.id) & (UserChallenge.status == "completed") & (UserChallenge.is_active == True)
        )
        .outerjoin(
            Challenge,
            (Challenge.id == UserChallenge.challenge_id) & (Challenge.is_active == True)
        )
        .filter(User.is_active == True)
        .group_by(User.id, User.full_name, User.email)
        .order_by(func.coalesce(func.sum(Challenge.points_reward), 0).desc())
        .all()
    )
    
    return [
        LeaderboardEntry(user_id=row.user_id, full_name=row.full_name, email=row.email, total_points=row.total_points)
        for row in query
    ]
