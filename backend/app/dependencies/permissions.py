from fastapi import Depends, HTTPException, status
from app.models.organization.user import User
from app.dependencies.auth import get_current_user
from app.core.logger import logger

class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if not current_user.role or current_user.role.name not in self.allowed_roles:
            logger.warning(
                f"Permission denied: User {current_user.email} with role "
                f"'{current_user.role.name if current_user.role else 'None'}' "
                f"attempted to access restricted resource. Allowed roles: {self.allowed_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action."
            )
        return current_user
