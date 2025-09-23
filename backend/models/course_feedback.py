from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from config.database import Base
from datetime import datetime

class CourseFeedback(Base):
    __tablename__ = "course_feedback"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    feedback = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", backref="feedbacks")
    student = relationship("Student")
