from models.course_feedback import CourseFeedback
from sqlalchemy.orm import Session

class CourseFeedbackRepository:
    @staticmethod
    def create_feedback(db: Session, feedback: CourseFeedback):
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback

    @staticmethod
    def get_feedbacks_by_course(db: Session, course_id: int):
        return db.query(CourseFeedback).filter(CourseFeedback.course_id == course_id).all()

    @staticmethod
    def get_feedbacks_by_professor(db: Session, professor_id: int):
        # Join Course to filter by professor
        return db.query(CourseFeedback).join("course").filter_by(professor_id=professor_id).all()
