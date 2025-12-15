from sqlmodel import Session, create_engine, SQLModel, select
from core.config import settings

# Import all models so SQLModel can detect them and create all tables
from models import User, Category, CustomerType, DocumentType, Document, Transaction
import logging
from core.data import default_categories, default_document_types

logger = logging.getLogger(__name__)

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db(session: Session) -> None:
    """Initialize database with default data"""

    SQLModel.metadata.create_all(engine)
    logger.info("✅ Database tables created successfully")

    try:
        # Check if we already have data
        existing_users = session.exec(select(User)).first()
        if existing_users:
            logger.info("ℹ️ Database already initialized, skipping...")
            return

        logger.info("🚀 Initializing database with default data...")

        # Create default document types
        logger.info("📄 Creating default document types...")
        created_doc_types_count = 0
        for doc_type_data in default_document_types:
            doc_type = DocumentType(name=doc_type_data["name"])
            session.add(doc_type)
            created_doc_types_count += 1

        session.flush()  # Flush to ensure document types are created before categories

        # Create default categories
        logger.info("📁 Creating default categories...")

        # Create categories with subcategories
        created_categories_count = 0
        for cat_data in default_categories:
            # Create parent category
            parent_category = Category(
                name=cat_data["name"], description=cat_data["description"]
            )
            session.add(parent_category)
            session.flush()  # To get the ID
            created_categories_count += 1

            # Create subcategories
            if "children" in cat_data and cat_data["children"]:
                for child_data in cat_data["children"]:
                    child_category = Category(
                        name=child_data["name"],
                        description=child_data["description"],
                        parent_id=parent_category.id,
                    )
                    session.add(child_category)
                    created_categories_count += 1

        # Create default admin user
        logger.info("👤 Creating default admin user...")
        default_user = User(
            email="admin@bcpextractor.com",
            name="Administrator",
            is_active=True,
            customer_type=CustomerType.INDIVIDUAL,
        )
        session.add(default_user)

        # Create test user
        test_user = User(
            email="test@bcpextractor.com",
            name="Test User",
            is_active=True,
            customer_type=CustomerType.INDIVIDUAL,
        )
        session.add(test_user)

        session.commit()
        logger.info(f"✅ Database initialized successfully!")
        logger.info(f"   📄 Created {created_doc_types_count} document types")
        logger.info(f"   📁 Created {created_categories_count} categories")
        logger.info(f"   👥 Created 2 users")

    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        session.rollback()
        raise


def get_session():
    """Get database session"""
    with Session(engine) as session:
        yield session
