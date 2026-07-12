from typing import Any, Dict
from sqlalchemy.orm import Query
from app.core.constants import DEFAULT_PAGE, DEFAULT_LIMIT, MAX_LIMIT

def paginate_query(query: Query, page: int = DEFAULT_PAGE, limit: int = DEFAULT_LIMIT) -> Dict[str, Any]:
    if page < 1:
        page = DEFAULT_PAGE
    if limit < 1:
        limit = DEFAULT_LIMIT
    elif limit > MAX_LIMIT:
        limit = MAX_LIMIT

    offset = (page - 1) * limit
    total = query.count()
    items = query.offset(offset).limit(limit).all()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit if limit > 0 else 0
    }
