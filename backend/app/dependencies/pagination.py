from fastapi import Query
from app.core.constants import DEFAULT_PAGE, DEFAULT_LIMIT

class PaginationParams:
    def __init__(
        self,
        page: int = Query(DEFAULT_PAGE, ge=1, description="Page number"),
        limit: int = Query(DEFAULT_LIMIT, ge=1, description="Number of items per page")
    ):
        self.page = page
        self.limit = limit
