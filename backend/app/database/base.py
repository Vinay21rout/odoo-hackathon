from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Import models package to register all models with Base.metadata
import app.models