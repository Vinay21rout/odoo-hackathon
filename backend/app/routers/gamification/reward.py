from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.schemas.gamification.reward import (
    RewardCreate, RewardResponse,
    RewardRedeemRequest, RewardRedemptionResponse
)
from app.services.gamification.reward import reward_service, reward_redemption_service
from app.services.common.response import success_response
from app.services.common.pagination import paginate_query
from app.dependencies.pagination import PaginationParams

router = APIRouter(prefix="/gamification", tags=["Gamification Rewards"])

@router.get("/rewards", response_model=None, status_code=status.HTTP_200_OK)
def read_rewards(
    params: PaginationParams = Depends(PaginationParams),
    db: Session = Depends(get_db)
):
    query = reward_service.get_query(db)
    paginated_data = paginate_query(query, params.page, params.limit)
    paginated_data["items"] = [
        RewardResponse.model_validate(item) for item in paginated_data["items"]
    ]
    return success_response(data=paginated_data, message="Reward catalog retrieved successfully")

@router.post("/rewards", response_model=None, status_code=status.HTTP_201_CREATED)
def create_reward(obj_in: RewardCreate, db: Session = Depends(get_db)):
    db_obj = reward_service.create(db, obj_in=obj_in)
    data = RewardResponse.model_validate(db_obj)
    return success_response(data=data, message="Reward item created successfully")

@router.post("/rewards/redeem", response_model=None, status_code=status.HTTP_201_CREATED)
def redeem_reward(payload: RewardRedeemRequest, db: Session = Depends(get_db)):
    db_obj = reward_redemption_service.redeem_reward(db, user_id=payload.user_id, reward_id=payload.reward_id)
    data = RewardRedemptionResponse.model_validate(db_obj)
    return success_response(data=data, message="Reward redeemed successfully")
