from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import DB_URL, POOL_SIZE, MAX_OVERFLOW

engine = create_engine(
    DB_URL,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    future=True
)

# фабрика сессий
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,  # выгодно для передачи объектов дальше
    future=True,
)