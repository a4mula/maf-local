"""
Unit Tests for Data Contracts
"""

import pytest
from src.models.data_contracts import TaskMetadata
from datetime import datetime

class TestTaskMetadata:
    
    def test_create_valid_metadata(self):
        """Should create valid TaskMetadata."""
        now = datetime.now().isoformat()
        metadata = TaskMetadata(
            created_at=now,
            updated_at=now,
            priority="high",
            tags=["bug", "urgent"],
            source="user"
        )
        
        assert metadata.priority == "high"
        assert "bug" in metadata.tags
        assert metadata.source == "user"

    def test_invalid_priority(self):
        """Should raise error for invalid priority."""
        now = datetime.now().isoformat()
        with pytest.raises(ValueError):
            TaskMetadata(
                created_at=now,
                updated_at=now,
                priority="super_high"  # Invalid
            )

    def test_defaults(self):
        """Should use default values."""
        now = datetime.now().isoformat()
        metadata = TaskMetadata(
            created_at=now,
            updated_at=now
        )
        
        assert metadata.priority == "medium"
        assert metadata.tags == []
        assert metadata.source is None
