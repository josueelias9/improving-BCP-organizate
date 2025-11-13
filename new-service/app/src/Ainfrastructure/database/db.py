"""
Database initialization and population
"""
from sqlmodel import Session, SQLModel, select
from .connection import engine
from models import (
    User, Category, CustomerType
)
import logging

logger = logging.getLogger(__name__)


def create_db_and_tables():
    """Create database tables"""
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {e}")
        raise


def init_db(session: Session) -> None:
    """Initialize database with default data"""
    
    try:
        # Check if we already have data
        existing_users = session.exec(select(User)).first()
        if existing_users:
            logger.info("ℹ️ Database already initialized, skipping...")
            return
        
        logger.info("🚀 Initializing database with default data...")
        
        # Create default categories
        logger.info("📁 Creating default categories...")
        default_categories = [
            {
                "name": "Alimentación", 
                "description": "Gastos relacionados con comida y bebidas",
                "children": [
                    {"name": "Restaurantes", "description": "Comidas en restaurantes"},
                    {"name": "Supermercado", "description": "Compras de alimentos"},
                    {"name": "Delivery", "description": "Pedidos a domicilio"}
                ]
            },
            {
                "name": "Transporte", 
                "description": "Gastos de movilidad y transporte",
                "children": [
                    {"name": "Combustible", "description": "Gasolina y combustible"},
                    {"name": "Taxi/Uber", "description": "Servicios de transporte"},
                    {"name": "Transporte Público", "description": "Bus, metro, tren"}
                ]
            },
            {
                "name": "Entretenimiento", 
                "description": "Gastos de ocio y entretenimiento",
                "children": [
                    {"name": "Cine", "description": "Boletos de cine"},
                    {"name": "Streaming", "description": "Netflix, Spotify, etc."},
                    {"name": "Juegos", "description": "Videojuegos y entretenimiento"}
                ]
            },
            {
                "name": "Salud", 
                "description": "Gastos médicos y de salud",
                "children": [
                    {"name": "Farmacia", "description": "Medicamentos"},
                    {"name": "Consultas", "description": "Consultas médicas"},
                    {"name": "Seguros", "description": "Seguros de salud"}
                ]
            },
            {
                "name": "Servicios", 
                "description": "Pagos de servicios básicos",
                "children": [
                    {"name": "Electricidad", "description": "Recibo de luz"},
                    {"name": "Agua", "description": "Recibo de agua"},
                    {"name": "Internet", "description": "Servicio de internet"},
                    {"name": "Telefonía", "description": "Servicios telefónicos"}
                ]
            },
            {
                "name": "Otros",
                "description": "Gastos no categorizados",
                "children": []
            }
        ]
        
        # Create categories with subcategories
        created_categories_count = 0
        for cat_data in default_categories:
            # Create parent category
            parent_category = Category(
                name=cat_data["name"],
                description=cat_data["description"]
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
                        parent_id=parent_category.id
                    )
                    session.add(child_category)
                    created_categories_count += 1
        
        # Create default admin user
        logger.info("👤 Creating default admin user...")
        default_user = User(
            email="admin@bcpextractor.com",
            name="Administrator",
            is_active=True,
            customer_type=CustomerType.INDIVIDUAL
        )
        session.add(default_user)
        
        # Create test user
        test_user = User(
            email="test@bcpextractor.com",
            name="Test User",
            is_active=True,
            customer_type=CustomerType.INDIVIDUAL
        )
        session.add(test_user)
        
        session.commit()
        logger.info(f"✅ Database initialized successfully!")
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