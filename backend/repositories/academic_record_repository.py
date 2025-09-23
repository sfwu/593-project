"""
Academic Record Repository - Data access layer for academic records
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from models.academic_record import AcademicRecord, Transcript, AcademicProgress, SemesterGPA, GradeStatus, TranscriptStatus
from models.student import Student
from models.course import Course
from schemas.academic_record_schemas import (
    AcademicRecordCreate, AcademicRecordUpdate,
    TranscriptCreate, TranscriptUpdate,
    AcademicProgressCreate, AcademicProgressUpdate,
    SemesterGPACreate, SemesterGPAUpdate
)
from datetime import datetime
import json

class AcademicRecordRepository:
    """Repository for academic record data access operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Academic Record Operations
    def create_academic_record(self, record_data: AcademicRecordCreate, student_id: int) -> AcademicRecord:
        """Create a new academic record"""
        record = AcademicRecord(
            student_id=student_id,
            **record_data.dict()
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record
    
    def get_academic_record_by_id(self, record_id: int) -> Optional[AcademicRecord]:
        """Get academic record by ID"""
        return self.db.query(AcademicRecord).options(
            joinedload(AcademicRecord.course),
            joinedload(AcademicRecord.student)
        ).filter(AcademicRecord.id == record_id).first()
    
    def get_student_academic_records(
        self, 
        student_id: int, 
        semester: Optional[str] = None,
        year: Optional[int] = None,
        status: Optional[GradeStatus] = None
    ) -> List[AcademicRecord]:
        """Get all academic records for a student with optional filters"""
        query = self.db.query(AcademicRecord).options(
            joinedload(AcademicRecord.course),
            joinedload(AcademicRecord.student)
        ).filter(AcademicRecord.student_id == student_id)
        
        if semester:
            query = query.filter(AcademicRecord.semester == semester)
        if year:
            query = query.filter(AcademicRecord.year == year)
        if status:
            query = query.filter(AcademicRecord.status == status)
        
        return query.order_by(desc(AcademicRecord.year), desc(AcademicRecord.semester)).all()
    
    def update_academic_record(self, record_id: int, record_data: AcademicRecordUpdate) -> Optional[AcademicRecord]:
        """Update an academic record"""
        record = self.db.query(AcademicRecord).filter(AcademicRecord.id == record_id).first()
        if not record:
            return None
        
        for field, value in record_data.dict(exclude_unset=True).items():
            setattr(record, field, value)
        
        record.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(record)
        return record
    
    def delete_academic_record(self, record_id: int) -> bool:
        """Delete an academic record"""
        record = self.db.query(AcademicRecord).filter(AcademicRecord.id == record_id).first()
        if not record:
            return False
        
        self.db.delete(record)
        self.db.commit()
        return True
    
    # Transcript Operations
    def create_transcript(self, transcript_data: TranscriptCreate, student_id: int) -> Transcript:
        """Create a new transcript"""
        transcript = Transcript(
            student_id=student_id,
            **transcript_data.dict()
        )
        self.db.add(transcript)
        self.db.commit()
        self.db.refresh(transcript)
        return transcript
    
    def get_transcript_by_id(self, transcript_id: int) -> Optional[Transcript]:
        """Get transcript by ID"""
        return self.db.query(Transcript).options(
            joinedload(Transcript.student)
        ).filter(Transcript.id == transcript_id).first()
    
    def get_student_transcripts(self, student_id: int, status: Optional[TranscriptStatus] = None) -> List[Transcript]:
        """Get all transcripts for a student"""
        query = self.db.query(Transcript).options(
            joinedload(Transcript.student)
        ).filter(Transcript.student_id == student_id)
        
        if status:
            query = query.filter(Transcript.status == status)
        
        return query.order_by(desc(Transcript.generated_date)).all()
    
    def update_transcript(self, transcript_id: int, transcript_data: TranscriptUpdate) -> Optional[Transcript]:
        """Update a transcript"""
        transcript = self.db.query(Transcript).filter(Transcript.id == transcript_id).first()
        if not transcript:
            return None
        
        for field, value in transcript_data.dict(exclude_unset=True).items():
            setattr(transcript, field, value)
        
        transcript.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(transcript)
        return transcript
    
    # Academic Progress Operations
    def create_academic_progress(self, progress_data: AcademicProgressCreate, student_id: int) -> AcademicProgress:
        """Create academic progress record"""
        progress = AcademicProgress(
            student_id=student_id,
            **progress_data.dict()
        )
        self.db.add(progress)
        self.db.commit()
        self.db.refresh(progress)
        return progress
    
    def get_academic_progress_by_student_id(self, student_id: int) -> Optional[AcademicProgress]:
        """Get academic progress for a student"""
        return self.db.query(AcademicProgress).options(
            joinedload(AcademicProgress.student)
        ).filter(AcademicProgress.student_id == student_id).first()
    
    def update_academic_progress(self, student_id: int, progress_data: AcademicProgressUpdate) -> Optional[AcademicProgress]:
        """Update academic progress"""
        progress = self.db.query(AcademicProgress).filter(AcademicProgress.student_id == student_id).first()
        if not progress:
            return None
        
        for field, value in progress_data.dict(exclude_unset=True).items():
            setattr(progress, field, value)
        
        progress.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(progress)
        return progress
    
    # Semester GPA Operations
    def create_semester_gpa(self, gpa_data: SemesterGPACreate, student_id: int) -> SemesterGPA:
        """Create semester GPA record"""
        gpa = SemesterGPA(
            student_id=student_id,
            **gpa_data.dict()
        )
        self.db.add(gpa)
        self.db.commit()
        self.db.refresh(gpa)
        return gpa
    
    def get_semester_gpa(self, student_id: int, semester: str, year: int) -> Optional[SemesterGPA]:
        """Get semester GPA for specific semester"""
        return self.db.query(SemesterGPA).filter(
            and_(
                SemesterGPA.student_id == student_id,
                SemesterGPA.semester == semester,
                SemesterGPA.year == year
            )
        ).first()
    
    def get_student_semester_gpas(self, student_id: int) -> List[SemesterGPA]:
        """Get all semester GPAs for a student"""
        return self.db.query(SemesterGPA).filter(
            SemesterGPA.student_id == student_id
        ).order_by(desc(SemesterGPA.year), desc(SemesterGPA.semester)).all()
    
    def update_semester_gpa(self, gpa_id: int, gpa_data: SemesterGPAUpdate) -> Optional[SemesterGPA]:
        """Update semester GPA"""
        gpa = self.db.query(SemesterGPA).filter(SemesterGPA.id == gpa_id).first()
        if not gpa:
            return None
        
        for field, value in gpa_data.dict(exclude_unset=True).items():
            setattr(gpa, field, value)
        
        gpa.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(gpa)
        return gpa
    
    # GPA Calculation Operations
    def calculate_cumulative_gpa(self, student_id: int) -> Dict[str, Any]:
        """Calculate cumulative GPA for a student"""
        # Get all graded records
        records = self.db.query(AcademicRecord).filter(
            and_(
                AcademicRecord.student_id == student_id,
                AcademicRecord.status == GradeStatus.GRADED,
                AcademicRecord.numeric_grade.isnot(None)
            )
        ).all()
        
        total_quality_points = 0.0
        total_credits_attempted = 0
        total_credits_earned = 0
        grade_distribution = {}
        
        for record in records:
            if record.numeric_grade is not None and record.credits_attempted > 0:
                quality_points = record.numeric_grade * record.credits_attempted
                total_quality_points += quality_points
                total_credits_attempted += record.credits_attempted
                
                if record.numeric_grade >= 1.0:  # Passing grade
                    total_credits_earned += record.credits_earned
                
                # Grade distribution
                letter_grade = record.letter_grade or "Unknown"
                grade_distribution[letter_grade] = grade_distribution.get(letter_grade, 0) + 1
        
        cumulative_gpa = total_quality_points / total_credits_attempted if total_credits_attempted > 0 else 0.0
        
        return {
            "cumulative_gpa": round(cumulative_gpa, 3),
            "total_quality_points": total_quality_points,
            "total_credits_attempted": total_credits_attempted,
            "total_credits_earned": total_credits_earned,
            "grade_distribution": grade_distribution
        }
    
    def calculate_major_gpa(self, student_id: int, major: str) -> Dict[str, Any]:
        """Calculate major GPA for a student"""
        # Get academic progress to determine major courses
        progress = self.get_academic_progress_by_student_id(student_id)
        if not progress:
            return {"major_gpa": 0.0, "total_quality_points": 0.0, "total_credits_attempted": 0}
        
        # Get records for major courses (this is simplified - in reality, you'd need course categorization)
        records = self.db.query(AcademicRecord).join(Course).filter(
            and_(
                AcademicRecord.student_id == student_id,
                AcademicRecord.status == GradeStatus.GRADED,
                AcademicRecord.numeric_grade.isnot(None),
                Course.department == major  # Simplified major course identification
            )
        ).all()
        
        total_quality_points = 0.0
        total_credits_attempted = 0
        
        for record in records:
            if record.numeric_grade is not None and record.credits_attempted > 0:
                quality_points = record.numeric_grade * record.credits_attempted
                total_quality_points += quality_points
                total_credits_attempted += record.credits_attempted
        
        major_gpa = total_quality_points / total_credits_attempted if total_credits_attempted > 0 else 0.0
        
        return {
            "major_gpa": round(major_gpa, 3),
            "total_quality_points": total_quality_points,
            "total_credits_attempted": total_credits_attempted
        }
    
    def get_grade_history(self, student_id: int) -> List[Dict[str, Any]]:
        """Get complete grade history for a student"""
        records = self.db.query(AcademicRecord).join(Course).filter(
            AcademicRecord.student_id == student_id
        ).order_by(desc(AcademicRecord.year), desc(AcademicRecord.semester)).all()
        
        grade_history = []
        for record in records:
            grade_history.append({
                "id": record.id,
                "course_code": record.course.course_code if record.course else "Unknown",
                "course_title": record.course.title if record.course else "Unknown",
                "semester": record.semester,
                "year": record.year,
                "credits": record.credits_attempted,
                "letter_grade": record.letter_grade,
                "numeric_grade": record.numeric_grade,
                "percentage_grade": record.percentage_grade,
                "status": record.status,
                "grade_date": record.grade_date,
                "credits_earned": record.credits_earned
            })
        
        return grade_history
    
    def get_academic_summary(self, student_id: int) -> Dict[str, Any]:
        """Get comprehensive academic summary for a student"""
        # Get basic stats
        total_records = self.db.query(AcademicRecord).filter(AcademicRecord.student_id == student_id).count()
        completed_records = self.db.query(AcademicRecord).filter(
            and_(
                AcademicRecord.student_id == student_id,
                AcademicRecord.status == GradeStatus.GRADED
            )
        ).count()
        incomplete_records = self.db.query(AcademicRecord).filter(
            and_(
                AcademicRecord.student_id == student_id,
                AcademicRecord.status == GradeStatus.INCOMPLETE
            )
        ).count()
        withdrawn_records = self.db.query(AcademicRecord).filter(
            and_(
                AcademicRecord.student_id == student_id,
                AcademicRecord.status == GradeStatus.WITHDRAWN
            )
        ).count()
        
        # Calculate GPAs
        cumulative_gpa_data = self.calculate_cumulative_gpa(student_id)
        
        # Get semester breakdown
        semester_gpas = self.get_student_semester_gpas(student_id)
        
        return {
            "total_courses": total_records,
            "courses_completed": completed_records,
            "courses_incomplete": incomplete_records,
            "courses_withdrawn": withdrawn_records,
            "cumulative_gpa": cumulative_gpa_data["cumulative_gpa"],
            "total_credits_earned": cumulative_gpa_data["total_credits_earned"],
            "total_credits_attempted": cumulative_gpa_data["total_credits_attempted"],
            "grade_distribution": cumulative_gpa_data["grade_distribution"],
            "semester_breakdown": [
                {
                    "semester": gpa.semester,
                    "year": gpa.year,
                    "gpa": gpa.semester_gpa,
                    "credits_earned": gpa.credits_earned,
                    "credits_attempted": gpa.credits_attempted
                }
                for gpa in semester_gpas
            ]
        }

