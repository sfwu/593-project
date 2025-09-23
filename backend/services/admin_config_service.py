from models.term_config import TermConfig
from models.grading_policy import GradingPolicy
from repositories.admin_config_repository import AdminConfigRepository
from schemas.admin_config_schemas import TermConfigCreate, GradingPolicyCreate
from sqlalchemy.orm import Session

class AdminConfigService:
    @staticmethod
    def configure_term(db: Session, config_data: TermConfigCreate):
        config = TermConfig(
            semester=config_data.semester,
            year=config_data.year
        )
        return AdminConfigRepository.create_term_config(db, config)

    @staticmethod
    def get_terms(db: Session):
        return AdminConfigRepository.get_terms(db)

    @staticmethod
    def configure_grading_policy(db: Session, policy_data: GradingPolicyCreate):
        policy = GradingPolicy(
            scale_name=policy_data.scale_name,
            details=policy_data.details
        )
        return AdminConfigRepository.create_grading_policy(db, policy)

    @staticmethod
    def get_grading_policies(db: Session):
        return AdminConfigRepository.get_grading_policies(db)
