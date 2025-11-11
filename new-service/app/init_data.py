import logging

from sqlmodel import Session

from src.infrastructure.database.connection import engine
from src.infrastructure.database.db import init_db, create_db_and_tables

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    # First create tables
    logger.info("Creating database tables...")
    create_db_and_tables()
    
    # Then initialize with data
    logger.info("Initializing database with default data...")
    with Session(engine) as session:
        init_db(session)


def main() -> None:
    logger.info("Creating database tables and initial data")
    init()
    logger.info("Database initialization completed successfully")


if __name__ == "__main__":
    main()