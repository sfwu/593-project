from sqlalchemy import Column, Integer, String, DateTime
from config.database import Base
from datetime import datetime

class TermConfig(Base):
    __tablename__ = "term_config"
    id = Column(Integer, primary_key=True, index=True)
    semester = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
