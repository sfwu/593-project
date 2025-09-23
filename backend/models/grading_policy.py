from sqlalchemy import Column, Integer, String, Text, DateTime
from config.database import Base
from datetime import datetime

class GradingPolicy(Base):
    __tablename__ = "grading_policy"
    id = Column(Integer, primary_key=True, index=True)
    scale_name = Column(String, nullable=False)
    details = Column(Text, nullable=False)  # JSON string or text
    created_at = Column(DateTime, default=datetime.utcnow)
