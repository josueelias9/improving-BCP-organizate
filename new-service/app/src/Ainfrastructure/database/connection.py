"""
Database configuration and connection setup
"""
import os
from sqlmodel import Session, create_engine
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Database configuration
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# Construir URL de conexión
SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Crear engine de base de datos
engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    echo=True,  # Para debug, cambiar a False en producción
    pool_pre_ping=True,
)


def get_session():
    """Generator function to get database session"""
    with Session(engine) as session:
        yield session