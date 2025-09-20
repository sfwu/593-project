"""
Academic Record Service - Business logic layer for academic records
"""
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from repositories.academic_record_repository import AcademicRecordRepository
from schemas.academic_record_schemas import (
    AcademicRecordCreate, AcademicRecordUpdate, AcademicRecordResponse,
    TranscriptCreate, TranscriptUpdate, TranscriptResponse,
    AcademicProgressCreate, AcademicProgressUpdate, AcademicProgressResponse,
    SemesterGPACreate, SemesterGPAUpdate, SemesterGPAResponse,
    GPACalculationResponse, TranscriptGenerationRequest, TranscriptGenerationResponse,
    AcademicProgressSummary, StudentGradeHistory, GradeSummary
)
from models.academic_record import GradeStatus, TranscriptStatus
from models.student import Student
from datetime import datetime, timedelta
import json
import os
import hashlib

class AcademicRecordService:
    """Service layer for academic record business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = AcademicRecordRepository(db)
    
    # Academic Record Operations
    def create_academic_record(self, record_data: AcademicRecordCreate, student_id: int) -> AcademicRecordResponse:
        """Create a new academic record with validation"""
        # Validate the record data
        self._validate_academic_record(record_data)
        
        # Create the record
        record = self.repository.create_academic_record(record_data, student_id)
        
        # Update semester GPA if grade is final
        if record.status == GradeStatus.GRADED:
            self._update_semester_gpa(student_id, record.semester, record.year)
        
        # Update academic progress
        self._update_academic_progress(student_id)
        
        return AcademicRecordResponse.from_orm(record)
    
    def get_student_grades(
        self, 
        student_id: int, 
        semester: Optional[str] = None,
        year: Optional[int] = None,
        status: Optional[GradeStatus] = None
    ) -> List[AcademicRecordResponse]:
        """Get student grades with optional filtering"""
        records = self.repository.get_student_academic_records(student_id, semester, year, status)
        return [AcademicRecordResponse.from_orm(record) for record in records]
    
    def update_grade(self, record_id: int, grade_data: AcademicRecordUpdate, student_id: int) -> Optional[AcademicRecordResponse]:
        """Update a grade with validation and progress tracking"""
        # Get the existing record
        record = self.repository.get_academic_record_by_id(record_id)
        if not record or record.student_id != student_id:
            return None
        
        # Validate the update
        self._validate_grade_update(grade_data)
        
        # Update the record
        updated_record = self.repository.update_academic_record(record_id, grade_data)
        if not updated_record:
            return None
        
        # Update semester GPA if grade status changed
        if grade_data.status == GradeStatus.GRADED:
            self._update_semester_gpa(student_id, updated_record.semester, updated_record.year)
        
        # Update academic progress
        self._update_academic_progress(student_id)
        
        return AcademicRecordResponse.from_orm(updated_record)
    
    # GPA Calculation Operations
    def calculate_gpa(self, student_id: int) -> GPACalculationResponse:
        """Calculate comprehensive GPA information for a student"""
        # Get cumulative GPA data
        cumulative_data = self.repository.calculate_cumulative_gpa(student_id)
        
        # Get major GPA data
        student = self.db.query(Student).filter(Student.id == student_id).first()
        major = student.major if student else "Unknown"
        major_data = self.repository.calculate_major_gpa(student_id, major)
        
        # Get semester breakdown
        semester_gpas = self.repository.get_student_semester_gpas(student_id)
        semester_breakdown = [SemesterGPAResponse.from_orm(gpa) for gpa in semester_gpas]
        
        # Calculate current semester GPA
        current_semester_gpa = self._calculate_current_semester_gpa(student_id)
        
        return GPACalculationResponse(
            cumulative_gpa=cumulative_data["cumulative_gpa"],
            major_gpa=major_data["major_gpa"],
            semester_gpa=current_semester_gpa,
            total_credits_earned=cumulative_data["total_credits_earned"],
            total_credits_attempted=cumulative_data["total_credits_attempted"],
            total_quality_points=cumulative_data["total_quality_points"],
            semester_breakdown=semester_breakdown,
            grade_distribution=cumulative_data["grade_distribution"]
        )
    
    def get_semester_gpa_breakdown(self, student_id: int) -> List[SemesterGPAResponse]:
        """Get semester-wise GPA breakdown"""
        semester_gpas = self.repository.get_student_semester_gpas(student_id)
        return [SemesterGPAResponse.from_orm(gpa) for gpa in semester_gpas]
    
    # Transcript Operations
    def generate_transcript(
        self, 
        student_id: int, 
        request: TranscriptGenerationRequest
    ) -> TranscriptGenerationResponse:
        """Generate an official transcript"""
        # Get student information
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise ValueError("Student not found")
        
        # Calculate transcript data
        gpa_data = self.calculate_gpa(student_id)
        grade_history = self.repository.get_grade_history(student_id)
        
        # Create transcript record
        transcript_data = TranscriptCreate(
            transcript_type=request.transcript_type,
            status=TranscriptStatus.OFFICIAL
        )
        transcript = self.repository.create_transcript(transcript_data, student_id)
        
        # Update transcript with calculated data
        transcript.total_credits_earned = gpa_data.total_credits_earned
        transcript.total_credits_attempted = gpa_data.total_credits_attempted
        transcript.cumulative_gpa = gpa_data.cumulative_gpa
        transcript.major_gpa = gpa_data.major_gpa
        
        # Generate file (simplified - in production, you'd generate a PDF)
        file_path = self._generate_transcript_file(transcript.id, student, grade_history, gpa_data)
        file_hash = self._calculate_file_hash(file_path) if file_path else None
        
        # Update transcript with file information
        self.repository.update_transcript(transcript.id, TranscriptUpdate(
            file_path=file_path,
            file_hash=file_hash
        ))
        
        return TranscriptGenerationResponse(
            transcript_id=transcript.id,
            status="generated",
            file_path=file_path,
            download_url=f"/transcripts/{transcript.id}/download" if file_path else None,
            generated_at=transcript.generated_date
        )
    
    def get_student_transcripts(self, student_id: int) -> List[TranscriptResponse]:
        """Get all transcripts for a student"""
        transcripts = self.repository.get_student_transcripts(student_id)
        return [TranscriptResponse.from_orm(transcript) for transcript in transcripts]
    
    # Academic Progress Operations
    def get_academic_progress(self, student_id: int) -> Optional[AcademicProgressResponse]:
        """Get academic progress for a student"""
        progress = self.repository.get_academic_progress_by_student_id(student_id)
        if not progress:
            return None
        
        return AcademicProgressResponse.from_orm(progress)
    
    def update_academic_progress(self, student_id: int, progress_data: AcademicProgressUpdate) -> Optional[AcademicProgressResponse]:
        """Update academic progress"""
        progress = self.repository.update_academic_progress(student_id, progress_data)
        if not progress:
            return None
        
        return AcademicProgressResponse.from_orm(progress)
    
    def get_academic_progress_summary(self, student_id: int) -> AcademicProgressSummary:
        """Get comprehensive academic progress summary"""
        progress = self.repository.get_academic_progress_by_student_id(student_id)
        if not progress:
            raise ValueError("Academic progress not found for student")
        
        # Calculate completion percentage
        completion_percentage = (progress.total_credits_earned / progress.total_credits_required) * 100 if progress.total_credits_required > 0 else 0
        
        # Calculate credits remaining
        credits_remaining = progress.total_credits_required - progress.total_credits_earned
        
        # Determine if on track
        is_on_track = self._assess_academic_progress(progress)
        
        # Parse requirements status
        requirements_status = self._parse_requirements_status(progress)
        
        return AcademicProgressSummary(
            student_id=student_id,
            degree_program=progress.degree_program,
            major=progress.major,
            catalog_year=progress.catalog_year,
            total_credits_earned=progress.total_credits_earned,
            total_credits_required=progress.total_credits_required,
            credits_remaining=credits_remaining,
            completion_percentage=round(completion_percentage, 2),
            cumulative_gpa=progress.cumulative_gpa,
            major_gpa=progress.major_gpa,
            is_on_track=is_on_track,
            expected_graduation_date=progress.expected_graduation_date,
            requirements_status=requirements_status
        )
    
    def get_grade_history(self, student_id: int) -> StudentGradeHistory:
        """Get complete grade history for a student"""
        # Get academic summary
        summary = self.repository.get_academic_summary(student_id)
        
        # Get grade history
        grade_history = self.repository.get_grade_history(student_id)
        
        # Convert to GradeSummary objects
        grade_summary = []
        for record in grade_history:
            grade_summary.append(GradeSummary(
                course_code=record["course_code"],
                course_title=record["course_title"],
                semester=record["semester"],
                year=record["year"],
                credits=record["credits"],
                letter_grade=record["letter_grade"] or "N/A",
                numeric_grade=record["numeric_grade"] or 0.0,
                percentage_grade=record["percentage_grade"],
                status=record["status"],
                grade_date=record["grade_date"]
            ))
        
        # Get semester breakdown
        semester_breakdown = self.get_semester_gpa_breakdown(student_id)
        
        return StudentGradeHistory(
            student_id=student_id,
            total_courses=summary["total_courses"],
            courses_completed=summary["courses_completed"],
            courses_incomplete=summary["courses_incomplete"],
            courses_withdrawn=summary["courses_withdrawn"],
            cumulative_gpa=summary["cumulative_gpa"],
            major_gpa=summary["cumulative_gpa"],  # Simplified - would need major-specific calculation
            grade_summary=grade_summary,
            semester_breakdown=semester_breakdown
        )
    
    # Private helper methods
    def _validate_academic_record(self, record_data: AcademicRecordCreate) -> None:
        """Validate academic record data"""
        if record_data.letter_grade and record_data.numeric_grade:
            # Validate grade consistency
            expected_numeric = self._letter_grade_to_numeric(record_data.letter_grade)
            if abs(record_data.numeric_grade - expected_numeric) > 0.1:
                raise ValueError("Letter grade and numeric grade do not match")
        
        if record_data.credits_earned > record_data.credits_attempted:
            raise ValueError("Credits earned cannot exceed credits attempted")
    
    def _validate_grade_update(self, grade_data: AcademicRecordUpdate) -> None:
        """Validate grade update data"""
        if grade_data.letter_grade and grade_data.numeric_grade:
            expected_numeric = self._letter_grade_to_numeric(grade_data.letter_grade)
            if abs(grade_data.numeric_grade - expected_numeric) > 0.1:
                raise ValueError("Letter grade and numeric grade do not match")
    
    def _letter_grade_to_numeric(self, letter_grade: str) -> float:
        """Convert letter grade to numeric grade"""
        grade_map = {
            'A+': 4.0, 'A': 4.0, 'A-': 3.7,
            'B+': 3.3, 'B': 3.0, 'B-': 2.7,
            'C+': 2.3, 'C': 2.0, 'C-': 1.7,
            'D+': 1.3, 'D': 1.0, 'D-': 0.7,
            'F': 0.0, 'P': 4.0, 'NP': 0.0
        }
        return grade_map.get(letter_grade.upper(), 0.0)
    
    def _update_semester_gpa(self, student_id: int, semester: str, year: int) -> None:
        """Update semester GPA for a student"""
        # Get all records for the semester
        records = self.repository.get_student_academic_records(student_id, semester, year, GradeStatus.GRADED)
        
        total_quality_points = 0.0
        total_credits_attempted = 0
        total_credits_earned = 0
        courses_completed = 0
        courses_attempted = len(records)
        
        for record in records:
            if record.numeric_grade is not None and record.credits_attempted > 0:
                quality_points = record.numeric_grade * record.credits_attempted
                total_quality_points += quality_points
                total_credits_attempted += record.credits_attempted
                
                if record.numeric_grade >= 1.0:  # Passing grade
                    total_credits_earned += record.credits_earned
                    courses_completed += 1
        
        semester_gpa = total_quality_points / total_credits_attempted if total_credits_attempted > 0 else 0.0
        
        # Check if semester GPA record exists
        existing_gpa = self.repository.get_semester_gpa(student_id, semester, year)
        
        gpa_data = SemesterGPACreate(
            semester=semester,
            year=year,
            semester_gpa=round(semester_gpa, 3),
            credits_earned=total_credits_earned,
            credits_attempted=total_credits_attempted,
            quality_points=total_quality_points,
            courses_completed=courses_completed,
            courses_attempted=courses_attempted
        )
        
        if existing_gpa:
            self.repository.update_semester_gpa(existing_gpa.id, SemesterGPAUpdate(**gpa_data.dict()))
        else:
            self.repository.create_semester_gpa(gpa_data, student_id)
    
    def _update_academic_progress(self, student_id: int) -> None:
        """Update academic progress for a student"""
        # Get current progress
        progress = self.repository.get_academic_progress_by_student_id(student_id)
        if not progress:
            return
        
        # Calculate updated values
        gpa_data = self.repository.calculate_cumulative_gpa(student_id)
        major_data = self.repository.calculate_major_gpa(student_id, progress.major)
        
        # Update progress record
        progress.total_credits_earned = gpa_data["total_credits_earned"]
        progress.cumulative_gpa = gpa_data["cumulative_gpa"]
        progress.major_gpa = major_data["major_gpa"]
        
        # Calculate major credits (simplified)
        major_records = self.repository.get_student_academic_records(student_id)
        major_credits = sum(
            record.credits_earned for record in major_records 
            if record.course and record.course.department == progress.major and record.status == GradeStatus.GRADED
        )
        progress.major_credits_earned = major_credits
        
        # Update semester GPA
        current_semester_gpa = self._calculate_current_semester_gpa(student_id)
        progress.semester_gpa = current_semester_gpa
        
        # Check if on track
        progress.is_on_track = self._assess_academic_progress(progress)
        
        self.db.commit()
    
    def _calculate_current_semester_gpa(self, student_id: int) -> float:
        """Calculate current semester GPA"""
        # Get current semester (simplified - would need proper semester detection)
        current_year = datetime.now().year
        current_semester = "Fall" if datetime.now().month >= 8 else "Spring"
        
        current_gpa = self.repository.get_semester_gpa(student_id, current_semester, current_year)
        return current_gpa.semester_gpa if current_gpa else 0.0
    
    def _assess_academic_progress(self, progress) -> bool:
        """Assess if student is on track for graduation"""
        # Simple assessment - could be more sophisticated
        credits_per_semester = 15  # Expected credits per semester
        credits_remaining = progress.total_credits_required - progress.total_credits_earned
        semesters_remaining = credits_remaining / credits_per_semester if credits_per_semester > 0 else 0
        
        # Check if GPA is above minimum (2.0)
        gpa_ok = progress.cumulative_gpa >= 2.0
        
        # Check if on track to graduate in reasonable time (max 6 semesters = 3 years)
        time_ok = semesters_remaining <= 6
        
        return gpa_ok and time_ok
    
    def _parse_requirements_status(self, progress) -> Dict[str, Any]:
        """Parse requirements status from JSON strings"""
        try:
            completed = json.loads(progress.completed_requirements) if progress.completed_requirements else []
            remaining = json.loads(progress.remaining_requirements) if progress.remaining_requirements else []
            warnings = json.loads(progress.warnings) if progress.warnings else []
        except (json.JSONDecodeError, TypeError):
            completed = []
            remaining = []
            warnings = []
        
        return {
            "completed_requirements": completed,
            "remaining_requirements": remaining,
            "warnings": warnings,
            "completion_rate": len(completed) / (len(completed) + len(remaining)) * 100 if (completed or remaining) else 0
        }
    
    def _generate_transcript_file(self, transcript_id: int, student: Student, grade_history: List[Dict], gpa_data: GPACalculationResponse) -> Optional[str]:
        """Generate transcript file (simplified implementation)"""
        # In a real implementation, this would generate a PDF
        # For now, we'll create a simple text file
        try:
            os.makedirs("data/transcripts", exist_ok=True)
            file_path = f"data/transcripts/transcript_{transcript_id}_{student.student_id}.txt"
            
            with open(file_path, 'w') as f:
                f.write(f"OFFICIAL TRANSCRIPT\n")
                f.write(f"Student: {student.first_name} {student.last_name}\n")
                f.write(f"Student ID: {student.student_id}\n")
                f.write(f"Major: {student.major}\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"Cumulative GPA: {gpa_data.cumulative_gpa}\n")
                f.write(f"Major GPA: {gpa_data.major_gpa}\n")
                f.write(f"Total Credits: {gpa_data.total_credits_earned}\n\n")
                f.write("COURSE HISTORY:\n")
                f.write("-" * 50 + "\n")
                
                for record in grade_history:
                    f.write(f"{record['course_code']} - {record['course_title']}\n")
                    f.write(f"  {record['semester']} {record['year']} - {record['letter_grade']} ({record['credits']} credits)\n")
            
            return file_path
        except Exception as e:
            print(f"Error generating transcript file: {e}")
            return None
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of a file"""
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256()
                for chunk in iter(lambda: f.read(4096), b""):
                    file_hash.update(chunk)
                return file_hash.hexdigest()
        except Exception:
            return ""

