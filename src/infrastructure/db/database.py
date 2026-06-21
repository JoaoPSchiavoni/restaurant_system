from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from src.config import settings

# Engine initialization
# Check if using sqlite to pass check_same_thread exception
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args
)

# Session factory configuration
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Modern SQLAlchemy 2.0 Declarative Base
class Base(DeclarativeBase):
    pass
