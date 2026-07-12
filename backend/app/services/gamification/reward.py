from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.gamification.reward import Reward, RewardRedemption
from app.models.organization.user import User
from app.services.common.crud import CRUDBase
from app.services.organization.notification import notification_service
from uuid import UUID

class CRUDReward(CRUDBase[Reward]):
    pass

class CRUDRewardRedemption(CRUDBase[RewardRedemption]):
    def redeem_reward(self, db: Session, *, user_id: UUID, reward_id: UUID) -> RewardRedemption:
        # Get user
        user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # Get reward
        reward = db.query(Reward).filter(Reward.id == reward_id, Reward.is_active == True).first()
        if not reward:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reward not found")
        
        # Check stock
        if reward.stock <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reward is out of stock")
            
        # Get user's total points (completed challenges points)
        from app.services.gamification.gamification_service import get_leaderboard
        leaderboard = get_leaderboard(db)
        user_points = 0
        for entry in leaderboard:
            if entry.user_id == user_id:
                user_points = entry.total_points
                break
                
        # Count spent points
        redeemed_query = db.query(RewardRedemption).filter(
            RewardRedemption.user_id == user_id,
            RewardRedemption.is_active == True
        ).all()
        spent_points = sum(r.reward.points_required for r in redeemed_query)
        available_points = user_points - spent_points
        
        if available_points < reward.points_required:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient points. Required: {reward.points_required}, Available: {available_points}"
            )
            
        # Deduct stock
        reward.stock -= 1
        db.add(reward)
        
        # Create redemption
        redemption = RewardRedemption(
            user_id=user_id,
            reward_id=reward_id
        )
        db.add(redemption)
        db.commit()
        db.refresh(redemption)
        
        # Trigger notification
        notification_service.trigger_notification(
            db,
            user_id=user_id,
            message=f"You successfully redeemed '{reward.name}' for {reward.points_required} XP points!",
            notification_type="challenge"
        )
        
        return redemption

reward_service = CRUDReward(Reward)
reward_redemption_service = CRUDRewardRedemption(RewardRedemption)
