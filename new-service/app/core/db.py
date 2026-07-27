from sqlmodel import Session, create_engine, SQLModel, select
from core.config import settings

# Import all models so SQLModel can detect them and create all tables
from models import User, Category, DocumentType, Transaction, Document
import logging
from core.data import (
    default_categories,
    default_document_types,
    default_users,
    default_documents,
    default_transactions,
)

logger = logging.getLogger(__name__)

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db(session: Session) -> None:
    """Initialize database with default data"""

    SQLModel.metadata.create_all(engine)
    logger.info("✅ Database tables created successfully")

    try:
        # Check if we already have data
        statement = select(User)
        existing_users = session.exec(statement).first()
        if existing_users:
            logger.info("ℹ️ Database already initialized, skipping...")
            return

        logger.info("🚀 Initializing database with default data...")

        # ================= Create default document types
        logger.info("📄 Creating default document types...")
        for doc_type_data in default_document_types:
            doc_type = DocumentType(id=doc_type_data["id"], name=doc_type_data["name"])
            session.add(doc_type)
        session.flush()  # Flush to ensure document types are created before categories

        # ================= Create default categories
        logger.info("📁 Creating default categories...")
        for cat_data in default_categories:
            category = Category(
                id=cat_data["id"],
                name=cat_data["name"],
                description=cat_data["description"],
                parent_id=cat_data["parent_id"],
            )
            session.add(category)
        session.flush()  # Flush to ensure categories are created before users

        # ================= Create default admin user
        logger.info("👤 Creating default admin user...")
        for user_data in default_users:
            user = User(
                id=user_data["id"],
                email=user_data["email"],
                name=user_data["name"],
                is_active=user_data["is_active"],
            )
            session.add(user)
        session.flush()

        # ================== Create default documents
        logger.info("📄 Creating default documents...")
        for document_data in default_documents:
            document = Document(
                id=document_data["id"],
                processed=document_data["processed"],
                unique_identifier=document_data["unique_identifier"],
                data=document_data["data"],
                document_type_id=document_data["document_type_id"],
                user_id=document_data["user_id"],
            )
            session.add(document)
        session.flush()

        # ================= Create default transactions
        logger.info("💰 Creating default transactions...")
        for transaction_data in default_transactions:
            transaction = Transaction(
                id=transaction_data["id"],
                description=transaction_data["description"],
                amount=transaction_data["amount"],
                order=transaction_data["order"],
                transaction_type=transaction_data["transaction_type"],
                category_id=transaction_data["category_id"],
                document_id=transaction_data["document_id"],
                currency=transaction_data["currency"],
                history=transaction_data["history"],
                unique_identifier=transaction_data["unique_identifier"],
            )
            session.add(transaction)

        session.commit()
        logger.info(f"✅ Database initialized successfully!")
        logger.info(f"   📄 Created {len(default_document_types)} document types")
        logger.info(f"   📁 Created {len(default_categories)} categories")
        logger.info(f"   👥 Created {len(default_users)} users")
        logger.info(f"   📄 Created {len(default_documents)} documents")
        logger.info(f"   💰 Created {len(default_transactions)} transactions")

    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        session.rollback()
        raise


def get_session():
    """Get database session"""
    with Session(engine) as session:
        yield session
