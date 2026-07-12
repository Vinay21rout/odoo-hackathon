from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.exceptions.handlers import http_exception_handler, validation_exception_handler
from app.middleware.request_logger import RequestLoggerMiddleware
from app.routers.organization.department import router as department_router
from app.routers.organization.employee import router as employee_router
from app.routers.organization.statistics import router as statistics_router
from app.routers.environmental.metric import router as environmental_router
from app.routers.social.metric import router as social_router
from app.routers.governance.metric import router as governance_router
from app.routers.gamification.gamification import router as gamification_router
from app.routers.reports.reports import router as reports_router
from app.routers.ai.ai import router as ai_router
from app.routers.organization.settings import router as settings_router
from app.routers.organization.notification import router as notification_router
from app.routers.gamification.reward import router as reward_router
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError

from app.database.database import SessionLocal
from app.models.auth.role import Role
from app.models.organization.department import Department
from app.models.organization.user import User

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.on_event("startup")
def seed_default_developer_data():
    db = SessionLocal()
    try:
        # Check if roles table is empty
        role = db.query(Role).first()
        if not role:
            admin_role = Role(
                id="c1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
                name="Admin Privilege",
                description="Administrative access to ESG indicators and configs"
            )
            employee_role = Role(
                id="a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
                name="Standard Employee",
                description="General corporate user"
            )
            db.add(admin_role)
            db.add(employee_role)
            db.commit()
            
        # Check if department is empty
        dept = db.query(Department).first()
        if not dept:
            default_dept = Department(
                id="d1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
                name="Sustainability & ESG",
                code="SUS",
                description="Coordinates corporate climate and waste reduction targets."
            )
            db.add(default_dept)
            db.commit()
            
        # Check if default admin user is empty
        admin_user = db.query(User).filter(User.firebase_uid == "admin-uid").first()
        if not admin_user:
            role_id = "c1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d"
            dept_id = "d1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d"
            
            default_admin = User(
                firebase_uid="admin-uid",
                full_name="Administrator",
                email="admin@ecosphere.ai",
                role_id=role_id,
                department_id=dept_id
            )
            db.add(default_admin)
            db.commit()

        # Check if SystemSettings is empty
        from app.models.organization.settings import SystemSettings
        s_settings = db.query(SystemSettings).first()
        if not s_settings:
            default_settings = SystemSettings(
                auto_emission_calculation=True,
                evidence_requirement=False,
                badge_auto_award=True,
                email_notifications=True,
                in_app_notifications=True
            )
            db.add(default_settings)
            db.commit()

        # Check if Rewards are empty
        from app.models.gamification.reward import Reward
        reward = db.query(Reward).first()
        if not reward:
            db.add(Reward(name="Eco-Friendly Water Flask", description="Double-walled stainless steel flask to reduce plastic usage.", points_required=150, stock=20))
            db.add(Reward(name="Tree Planting Contribution", description="Sponsor a tree in the corporate community forest.", points_required=200, stock=999))
            db.add(Reward(name="Organic Cotton Tote Bag", description="EcoSphere branded canvas shopping tote.", points_required=100, stock=50))
            db.add(Reward(name="Premium Green Coffee Cup", description="Reusable cup made from organic bamboo fibers.", points_required=250, stock=15))
            db.commit()

        # Check if Badges are empty
        from app.models.gamification.badge import Badge
        badge = db.query(Badge).first()
        if not badge:
            db.add(Badge(name="Carbon Zero Rookie", description="Logged first carbon emissions reduction metric.", icon_url="fa-leaf", points_target=50))
            db.add(Badge(name="Green Champion", description="Acquired 200+ points in environmental challenges.", icon_url="fa-seedling", points_target=200))
            db.add(Badge(name="Social Advocate", description="Logged 10+ hours in social responsibility efforts.", icon_url="fa-users", points_target=150))
            db.add(Badge(name="Governance Guardian", description="Maintained perfect compliance audit reporting.", icon_url="fa-shield-halved", points_target=300))
            db.commit()
    except Exception as e:
        print(f"Error seeding default developer data: {e}")
        db.rollback()
    finally:
        db.close()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Logging Middleware
app.add_middleware(RequestLoggerMiddleware)

# Exception Handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Routers
app.include_router(department_router, prefix=settings.API_V1_STR)
app.include_router(employee_router, prefix=settings.API_V1_STR)
app.include_router(statistics_router, prefix=settings.API_V1_STR)
app.include_router(environmental_router, prefix=settings.API_V1_STR)
app.include_router(social_router, prefix=settings.API_V1_STR)
app.include_router(governance_router, prefix=settings.API_V1_STR)
app.include_router(gamification_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)
app.include_router(ai_router, prefix=settings.API_V1_STR)
app.include_router(settings_router, prefix=settings.API_V1_STR)
app.include_router(notification_router, prefix=settings.API_V1_STR)
app.include_router(reward_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "EcoSphere AI API Running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
