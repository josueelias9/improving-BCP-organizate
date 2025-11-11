"""
Database dependencies for FastAPI
"""
from typing import Annotated, Generator
from fastapi import Depends
from sqlmodel import Session
from src.infrastructure.database.connection import get_session


def get_db_session() -> Generator[Session, None, None]:
    """Get database session"""
    session = next(get_session())
    try:
        yield session
    finally:
        session.close()


# FastAPI dependency annotation
SessionDep = Annotated[Session, Depends(get_db_session)]