"""
Validation Tool (Tier 2)

Allows ProjectLeadAgent to validate user requirements against architectural constraints.
"""

from typing import List, Dict, Any

class ValidationTool:
    """Tool for validating requirements and plans."""
    
    def validate_requirements(self, requirements: str) -> Dict[str, Any]:
        """
        Validate user requirements for completeness and feasibility.
        
        Args:
            requirements: The user requirements text.
            
        Returns:
            Validation result dictionary.
        """
        # Simple validation logic for now
        issues = []
        if len(requirements) < 10:
            issues.append("Requirements too short/vague.")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "score": 100 if len(issues) == 0 else 50
        }

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Return the JSON schema definitions for the LLM.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "validate_requirements",
                    "description": "Validate user requirements for completeness and feasibility.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "requirements": {
                                "type": "string",
                                "description": "The user requirements text to validate."
                            }
                        },
                        "required": ["requirements"]
                    }
                }
            }
        ]
