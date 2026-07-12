import sys
import os
from datetime import date, timedelta
import random

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.database.database import SessionLocal
from app.models.organization.user import User
from app.models.environmental.metric import EnvironmentalRecord
from app.models.social.metric import SocialRecord
from app.models.governance.metric import GovernanceRecord
from app.main import seed_default_developer_data

def seed():
    # Ensure default roles, dept, and admin are created
    seed_default_developer_data()
    
    db = SessionLocal()
    try:
        # Get admin user
        user = db.query(User).filter(User.firebase_uid == "admin-uid").first()
        if not user:
            print("Admin user not found. Please run the backend first to seed the default admin.")
            return

        # Check if already seeded
        env_count = db.query(EnvironmentalRecord).count()
        if env_count > 0:
            print("Database already contains data.")
            return

        print("Generating dummy fallback data...")
        
        # Environmental Data
        env_types = [("carbon", "kgCO2e", 50, 200), ("energy", "kWh", 100, 500), ("water", "m3", 10, 50), ("waste", "kg", 5, 25)]
        
        # Social Data
        soc_types = [("training_hours", 2, 10), ("health_safety_incidents", 0, 2), ("community_hours", 1, 5)]

        # Governance Data
        gov_types = [("whistleblower_reports", 0, 1), ("policy_violations", 0, 1)]

        today = date.today()

        # Generate 30 days of past data
        for i in range(30):
            record_date = today - timedelta(days=i)
            
            # Env
            for m_type, unit, min_v, max_v in env_types:
                db.add(EnvironmentalRecord(
                    user_id=user.id,
                    metric_type=m_type,
                    value=random.uniform(min_v, max_v),
                    unit=unit,
                    description=f"Generated {m_type}",
                    recorded_date=record_date
                ))

            # Soc
            for m_type, min_v, max_v in soc_types:
                db.add(SocialRecord(
                    user_id=user.id,
                    metric_type=m_type,
                    value=random.uniform(min_v, max_v),
                    description=f"Generated {m_type}",
                    recorded_date=record_date
                ))

            # Gov
            for m_type, min_v, max_v in gov_types:
                val = random.randint(min_v, max_v)
                if val > 0:
                    db.add(GovernanceRecord(
                        user_id=user.id,
                        metric_type=m_type,
                        value=float(val),
                        status=random.choice(["pending", "resolved", "investigating"]),
                        description=f"Generated {m_type}",
                        recorded_date=record_date
                    ))

        db.commit()
        print("Successfully generated dummy data.")

    except Exception as e:
        print(f"Error seeding dummy data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
