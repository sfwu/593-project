"""
Unit Tests for Admin Config Service
Tests academic term configuration and grading policy management
"""
import pytest
from unittest.mock import Mock, patch
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))
from services.admin_config_service import AdminConfigService
from schemas.admin_config_schemas import TermConfigCreate, GradingPolicyCreate

class TestAdminConfigService:
    """Unit tests for admin config service"""
    def test_configure_term(self):
        mock_db = Mock()
        config_data = TermConfigCreate(semester="Spring", year=2026)
        with patch("services.admin_config_service.AdminConfigRepository.create_term_config", return_value="term_obj") as mock_create:
            result = AdminConfigService.configure_term(mock_db, config_data)
            mock_create.assert_called_once()
            assert result == "term_obj"

    def test_get_terms(self):
        mock_db = Mock()
        with patch("services.admin_config_service.AdminConfigRepository.get_terms", return_value=[{"semester": "Spring", "year": 2026}]) as mock_get:
            result = AdminConfigService.get_terms(mock_db)
            mock_get.assert_called_once_with(mock_db)
            assert result[0]["semester"] == "Spring"

    def test_configure_grading_policy(self):
        mock_db = Mock()
        policy_data = GradingPolicyCreate(scale_name="A-F", details="Standard scale")
        with patch("services.admin_config_service.AdminConfigRepository.create_grading_policy", return_value="policy_obj") as mock_create:
            result = AdminConfigService.configure_grading_policy(mock_db, policy_data)
            mock_create.assert_called_once()
            assert result == "policy_obj"

    def test_get_grading_policies(self):
        mock_db = Mock()
        with patch("services.admin_config_service.AdminConfigRepository.get_grading_policies", return_value=[{"scale_name": "A-F", "details": "Standard scale"}]) as mock_get:
            result = AdminConfigService.get_grading_policies(mock_db)
            mock_get.assert_called_once_with(mock_db)
            assert result[0]["scale_name"] == "A-F"
