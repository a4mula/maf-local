"""
Integration Tests for ValidationTool
"""

import pytest
from src.tools.tier2.validation_tool import ValidationTool

class TestValidationTool:
    
    def test_validate_requirements_valid(self):
        """Should validate valid requirements."""
        tool = ValidationTool()
        reqs = "Implement a new feature with proper testing and documentation."
        result = tool.validate_requirements(reqs)
        
        assert result["valid"] is True
        assert result["score"] == 100
        assert len(result["issues"]) == 0

    def test_validate_requirements_invalid(self):
        """Should reject vague requirements."""
        tool = ValidationTool()
        reqs = "Fix bug"
        result = tool.validate_requirements(reqs)
        
        assert result["valid"] is False
        assert result["score"] == 50
        assert len(result["issues"]) > 0
        assert "Requirements too short/vague." in result["issues"]

    def test_get_tool_definitions(self):
        """Should return correct tool definitions."""
        tool = ValidationTool()
        defs = tool.get_tool_definitions()
        
        assert len(defs) == 1
        assert defs[0]["function"]["name"] == "validate_requirements"
