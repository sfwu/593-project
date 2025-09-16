"""
Professor model
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base

class Professor(Base):
    """Professor model"""
    __tablename__ = "professors"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    professor_id = Column(String(20), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    office_location = Column(String(100))
    office_hours = Column(Text)
    department = Column(String(100), nullable=False)
    title = Column(String(100))  # Assistant Professor, Associate Professor, etc.
    specialization = Column(Text)
    
    # Relationships
    user = relationship("User", backref="professor_profile")
    courses = relationship("Course", back_populates="professor")
