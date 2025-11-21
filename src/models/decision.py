from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import UUID, uuid4
import yaml

class Decision(BaseModel):
    """
    Represents an authoritative architectural decision.
    """
    id: UUID = Field(default_factory=uuid4)
    category: str = Field(..., description="Category: 'architecture', 'constraint', 'vision'")
    content: Dict[str, Any] = Field(..., description="Structured content of the decision")
    created_by: str = Field(..., description="Agent ID who made the decision (usually ProjectLead)")
    created_at: datetime = Field(default_factory=datetime.now)
    immutable: bool = Field(default=True, description="Whether this decision is immutable")

    def to_yaml(self) -> str:
        """Convert decision content to YAML for storage/diffing"""
        return yaml.dump(self.content, sort_keys=True)
