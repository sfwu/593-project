from models.course_feedback import CourseFeedback
from repositories.course_feedback_repository import CourseFeedbackRepository
from schemas.course_feedback_schemas import CourseFeedbackCreate
from sqlalchemy.orm import Session

class CourseFeedbackService:
    @staticmethod
    def submit_feedback(db: Session, student_id: int, feedback_data: CourseFeedbackCreate):
        feedback = CourseFeedback(
            course_id=feedback_data.course_id,
            student_id=student_id,
            rating=feedback_data.rating,
            feedback=feedback_data.feedback
        )
        return CourseFeedbackRepository.create_feedback(db, feedback)

    @staticmethod
    def get_course_feedbacks(db: Session, course_id: int):
        return CourseFeedbackRepository.get_feedbacks_by_course(db, course_id)

    @staticmethod
    def get_professor_feedbacks(db: Session, professor_id: int):
        return CourseFeedbackRepository.get_feedbacks_by_professor(db, professor_id)
