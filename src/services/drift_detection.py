from typing import List, Dict, Any
from src.models.decision import Decision
import yaml

def detect_drift(decisions: List[Decision], current_state: Dict[str, Any]) -> List[str]:
    """
    Compares authoritative decisions against current system state.
    Returns a list of drift descriptions.
    """
    drift_report = []
    
    # Convert current state to flat dict for easier comparison if needed
    # For now, we'll assume current_state has keys matching decision categories
    
    for decision in decisions:
        category = decision.category
        
        # Skip if category not in current state (might not be active)
        if category not in current_state:
            continue
            
        actual_state = current_state[category]
        expected_state = decision.content
        
        # Simple comparison for now - can be enhanced with deep diff
        if actual_state != expected_state:
            drift_report.append(
                f"Drift detected in {category}: Expected {expected_state}, found {actual_state}"
            )
            
    return drift_report
