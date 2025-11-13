"""
Database health check script
"""
import logging
from sqlmodel import Session, select

from src.Ainfrastructure.database.connection import engine
from models import User, Category, Document, Transaction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_database_status() -> None:
    """Check database connection and data status"""
    try:
        with Session(engine) as session:
            # Test connection
            logger.info("Testing database connection...")
            
            # Check tables and data
            users_count = session.exec(select(User)).all()
            categories_count = session.exec(select(Category)).all()
            documents_count = session.exec(select(Document)).all()
            transactions_count = session.exec(select(Transaction)).all()
            
            logger.info("=== Database Status ===")
            logger.info(f"✅ Database connection: OK")
            logger.info(f"📊 Users: {len(users_count)}")
            logger.info(f"📊 Categories: {len(categories_count)}")
            logger.info(f"📊 Documents: {len(documents_count)}")
            logger.info(f"📊 Transactions: {len(transactions_count)}")
            
            if users_count:
                logger.info("👥 Users:")
                for user in users_count:
                    logger.info(f"   - {user.name} ({user.email}) - Active: {user.is_active}")
            
            if categories_count:
                logger.info("🏷️ Categories:")
                for cat in categories_count:
                    logger.info(f"   - {cat.name}")
            
            logger.info("=== End Status ===")
            
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise


def main() -> None:
    logger.info("Checking database status...")
    check_database_status()


if __name__ == "__main__":
    main()