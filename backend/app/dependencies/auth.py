from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import firebase_admin
from firebase_admin import auth as firebase_auth

from app.dependencies.database import get_db
from app.models.organization.user import User
from app.core.logger import logger
from app.core.config import settings

# Initialize Firebase Admin if not already initialized
try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app()

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    try:
        if settings.DEBUG and token.startswith("mock-"):
            firebase_uid = token.replace("mock-", "")
            logger.info(f"Using mock authentication for firebase_uid: {firebase_uid}")
        else:
            decoded_token = firebase_auth.verify_id_token(token)
            firebase_uid = decoded_token["uid"]

        user = db.query(User).filter(User.firebase_uid == firebase_uid, User.is_active == True).first()
        if not user:
            logger.warning(f"Firebase UID '{firebase_uid}' authenticated but user profile does not exist in DB.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in organization."
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
