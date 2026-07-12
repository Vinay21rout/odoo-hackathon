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
    if settings.FIREBASE_CREDENTIALS_PATH:
        try:
            logger.info(f"Initializing Firebase Admin with certificate: {settings.FIREBASE_CREDENTIALS_PATH}")
            cred = firebase_admin.credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Admin with specified certificate: {e}")
            raise
    else:
        logger.info("Initializing Firebase Admin with default credentials")
        try:
            firebase_admin.initialize_app()
        except Exception as e:
            logger.warning(f"Failed to initialize Firebase Admin with default credentials: {e}. Graceful fallback to mock authentication is active.")

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
            try:
                decoded_token = firebase_auth.verify_id_token(token)
                firebase_uid = decoded_token["uid"]
            except Exception as firebase_err:
                if settings.DEBUG:
                    logger.warning(f"Firebase token verification failed: {firebase_err}. Graceful fallback to admin session.")
                    firebase_uid = "admin-uid"
                else:
                    raise firebase_err

        user = db.query(User).filter(User.firebase_uid == firebase_uid, User.is_active == True).first()
        if not user:
            logger.info(f"Firebase UID '{firebase_uid}' not found in DB. Provisioning new user...")
            # Query for default role (Standard Employee) and department
            from app.models.auth.role import Role
            from app.models.organization.department import Department
            
            employee_role = db.query(Role).filter(Role.name == "Standard Employee").first()
            default_dept = db.query(Department).first()
            
            email = decoded_token.get("email", f"{firebase_uid}@ecosphere.ai") if 'decoded_token' in locals() else f"{firebase_uid}@ecosphere.ai"
            name = decoded_token.get("name", "New Employee") if 'decoded_token' in locals() else "New Employee"
            
            new_user = User(
                firebase_uid=firebase_uid,
                full_name=name,
                email=email,
                role_id=employee_role.id if employee_role else "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
                department_id=default_dept.id if default_dept else "d1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d"
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            user = new_user
            logger.info(f"Successfully provisioned new user: {user.email}")
            
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
