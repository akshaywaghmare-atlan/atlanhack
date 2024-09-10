from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

@lru_cache(maxsize=None)
def get_engine():
    return create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False},
        pool_pre_ping=True
    )

def get_session():
    session = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())()
    try:
        yield session
    finally:
        session.close()

Base = declarative_base()