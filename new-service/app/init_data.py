import logging

from sqlmodel import Session

from core.db import engine, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:

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
