from models.term_config import TermConfig
from models.grading_policy import GradingPolicy
from sqlalchemy.orm import Session

class AdminConfigRepository:
    @staticmethod
    def create_term_config(db: Session, config: TermConfig):
        db.add(config)
        db.commit()
        db.refresh(config)
        return config

    @staticmethod
    def get_terms(db: Session):
        return db.query(TermConfig).all()

    @staticmethod
    def create_grading_policy(db: Session, policy: GradingPolicy):
        db.add(policy)
        db.commit()
        db.refresh(policy)
        return policy

    @staticmethod
    def get_grading_policies(db: Session):
        return db.query(GradingPolicy).all()
