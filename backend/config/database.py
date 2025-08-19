"""
Database configuration and setup
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Database URL - SQLite database in data/ directory
# Use environment variable for testing, default to main database
DB_NAME = os.getenv("DB_NAME", "academic_management.db")
DATABASE_URL = f"sqlite:///./data/{DB_NAME}"

# Create engine
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Only needed for SQLite
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

def init_db():
    """Initialize database - create all tables"""
    import models  # Import here to avoid circular imports
    Base.metadata.create_all(bind=engine)
