"""
Unit Tests for Course Feedback Service
Tests course ratings and student feedback functionality
"""
import pytest
from unittest.mock import Mock, patch
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))
from backend.services.course_feedback_service import CourseFeedbackService
from backend.schemas.course_feedback_schemas import CourseFeedbackCreate

class TestCourseFeedbackService:
    """Unit tests for course feedback service"""
    def test_submit_feedback(self):
        mock_db = Mock()
        feedback_data = CourseFeedbackCreate(course_id=1, rating=5, feedback="Great course!")
        with patch("backend.services.course_feedback_service.CourseFeedbackRepository.create_feedback", return_value="feedback_obj") as mock_create:
            result = CourseFeedbackService.submit_feedback(mock_db, student_id=2, feedback_data=feedback_data)
            mock_create.assert_called_once()
            assert result == "feedback_obj"

    def test_get_course_feedbacks(self):
        mock_db = Mock()
        with patch("backend.services.course_feedback_service.CourseFeedbackRepository.get_feedbacks_by_course", return_value=[{"rating": 5, "feedback": "Excellent"}]) as mock_get:
            result = CourseFeedbackService.get_course_feedbacks(mock_db, course_id=1)
            mock_get.assert_called_once_with(mock_db, 1)
            assert result[0]["rating"] == 5

    def test_get_professor_feedbacks(self):
        mock_db = Mock()
        with patch("backend.services.course_feedback_service.CourseFeedbackRepository.get_feedbacks_by_professor", return_value=[{"rating": 4, "feedback": "Good"}]) as mock_get:
            result = CourseFeedbackService.get_professor_feedbacks(mock_db, professor_id=1)
            mock_get.assert_called_once_with(mock_db, 1)
            assert result[0]["rating"] == 4
