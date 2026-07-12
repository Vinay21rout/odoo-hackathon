from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.organization.department import Department
from app.models.organization.user import User
from app.core.logger import logger

class OrganizationService:
    @staticmethod
    def get_organization_stats(db: Session) -> dict:
        logger.info("Calculating organization stats in OrganizationService")
        
        # Count of active departments
        total_departments = db.query(Department).filter(Department.is_active == True).count()
        
        # Count of employees (users)
        total_employees = db.query(User).count()
        active_employees = db.query(User).filter(User.is_active == True).count()
        inactive_employees = db.query(User).filter(User.is_active == False).count()
        
        # Department breakdown (uses outer join to include departments with 0 active employees)
        breakdown_query = (
            db.query(Department.name, func.count(User.id))
            .outerjoin(User, (User.department_id == Department.id) & (User.is_active == True))
            .filter(Department.is_active == True)
            .group_by(Department.id, Department.name)
            .all()
        )
        
        department_breakdown = [
            {"department_name": name, "employee_count": count}
            for name, count in breakdown_query
        ]
        
        logger.info(
            f"Calculated stats: {total_departments} depts, "
            f"{total_employees} employees ({active_employees} active, {inactive_employees} inactive)"
        )
        
        return {
            "total_departments": total_departments,
            "total_employees": total_employees,
            "active_employees": active_employees,
            "inactive_employees": inactive_employees,
            "department_breakdown": department_breakdown
        }

organization_service = OrganizationService()
