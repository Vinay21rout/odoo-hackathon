from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.dependencies.database import get_db
from app.dependencies.pagination import PaginationParams
from app.schemas.gamification.gamification import (
    ChallengeCreate, ChallengeUpdate, ChallengeResponse,
    BadgeCreate, BadgeUpdate, BadgeResponse,
    UserChallengeCreate, UserChallengeResponse,
    UserBadgeCreate, UserBadgeResponse,
    LeaderboardEntry
)
from app.services.gamification.gamification_service import (
    challenge_service, badge_service,
    user_challenge_service, user_badge_service,
    get_leaderboard
)
from app.services.common.response import success_response
from app.services.common.pagination import paginate_query
from app.core.logger import logger

router = APIRouter(prefix="/gamification", tags=["Gamification"])

# --- Challenges Routes ---

@router.get("/challenges", status_code=status.HTTP_200_OK)
def read_challenges(
    params: PaginationParams = Depends(PaginationParams),
    db: Session = Depends(get_db)
):
    logger.info(f"Retrieving challenges (page: {params.page}, limit: {params.limit})")
    query = challenge_service.get_query(db)
    paginated_data = paginate_query(query, params.page, params.limit)
    paginated_data["items"] = [
        ChallengeResponse.model_validate(item) for item in paginated_data["items"]
    ]
    return success_response(data=paginated_data, message="Challenges retrieved successfully")

@router.post("/challenges", status_code=status.HTTP_201_CREATED)
def create_challenge(obj_in: ChallengeCreate, db: Session = Depends(get_db)):
    db_obj = challenge_service.create(db, obj_in=obj_in)
    data = ChallengeResponse.model_validate(db_obj)
    return success_response(data=data, message="Challenge created successfully")

# --- Badges Routes ---

@router.get("/badges", status_code=status.HTTP_200_OK)
def read_badges(
    params: PaginationParams = Depends(PaginationParams),
    db: Session = Depends(get_db)
):
    logger.info(f"Retrieving badges (page: {params.page}, limit: {params.limit})")
    query = badge_service.get_query(db)
    paginated_data = paginate_query(query, params.page, params.limit)
    paginated_data["items"] = [
        BadgeResponse.model_validate(item) for item in paginated_data["items"]
    ]
    return success_response(data=paginated_data, message="Badges retrieved successfully")

@router.post("/badges", status_code=status.HTTP_201_CREATED)
def create_badge(obj_in: BadgeCreate, db: Session = Depends(get_db)):
    db_obj = badge_service.create(db, obj_in=obj_in)
    data = BadgeResponse.model_validate(db_obj)
    return success_response(data=data, message="Badge created successfully")

# --- Progress Tracking Routes ---

@router.post("/user-challenges", status_code=status.HTTP_201_CREATED)
def join_challenge(obj_in: UserChallengeCreate, db: Session = Depends(get_db)):
    db_obj = user_challenge_service.create(db, obj_in=obj_in)
    data = UserChallengeResponse.model_validate(db_obj)
    return success_response(data=data, message="User joined challenge successfully")

@router.put("/user-challenges/{id}/complete", status_code=status.HTTP_200_OK)
def complete_user_challenge(id: UUID, db: Session = Depends(get_db)):
    db_obj = user_challenge_service.complete_challenge(db, user_challenge_id=id)
    data = UserChallengeResponse.model_validate(db_obj)
    return success_response(data=data, message="User challenge completed successfully")

@router.post("/user-badges", status_code=status.HTTP_201_CREATED)
def assign_user_badge(obj_in: UserBadgeCreate, db: Session = Depends(get_db)):
    db_obj = user_badge_service.create(db, obj_in=obj_in)
    data = UserBadgeResponse.model_validate(db_obj)
    return success_response(data=data, message="Badge assigned to user successfully")

# --- Leaderboard Route ---

@router.get("/leaderboard", status_code=status.HTTP_200_OK)
def read_leaderboard(db: Session = Depends(get_db)):
    data = get_leaderboard(db)
    return success_response(data=data, message="Leaderboard retrieved successfully")
