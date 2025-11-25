"""
Documentation Update Planner Tool

This tool helps agents plan documentation updates by:
1. Reading feature_manifest.yaml to identify affected docs
2. Generating a structured checklist of changes
3. Providing templates for each update type

Used by Documentation Agent (Domain Lead for Docs) to efficiently
update documentation when features are added or modified.
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Optional
import yaml
import json
from datetime import datetime
from src.utils import get_logger

logger = get_logger(__name__)


class DocUpdatePlanner:
    """Plans documentation updates based on feature manifests."""
    
    def __init__(self, docs_root: Path = None):
        """
        Initialize the planner.
        
        Args:
            docs_root: Path to docs/ directory. Defaults to project root.
        """
        if docs_root is None:
            # Assume we're running from src/
            docs_root = Path(__file__).parent.parent.parent / "docs"
        
        self.docs_root = Path(docs_root)
        self.ai_dir = self.docs_root / ".ai"
        self.manifest_path = self.ai_dir / "feature_manifest.yaml"
        self.templates_path = self.ai_dir / "update_templates.yaml"
        
        self.manifest: Optional[Dict] = None
        self.templates: Optional[Dict] = None
    
    def load_manifest(self) -> Dict:
        """Load feature manifest from .ai/feature_manifest.yaml"""
        if not self.manifest_path.exists():
            raise FileNotFoundError(
                f"Feature manifest not found: {self.manifest_path}"
            )
        
        with open(self.manifest_path, 'r') as f:
            self.manifest = yaml.safe_load(f)
        
        return self.manifest
    
    def load_templates(self) -> Dict:
        """Load update templates from .ai/update_templates.yaml"""
        if not self.templates_path.exists():
            raise FileNotFoundError(
                f"Update templates not found: {self.templates_path}"
            )
        
        with open(self.templates_path, 'r') as f:
            self.templates = yaml.safe_load(f)
        
        return self.templates
    
    async def plan_updates_for_feature(
        self,
        feature_name: str
    ) -> Dict[str, any]:
        """
        Generate update plan for a specific feature.
        
        Args:
            feature_name: Name of feature from feature_manifest.yaml
        
        Returns:
            Dict containing:
            - feature_info: Metadata about the feature
            - affected_docs: List of docs to update with change details
            - checklist: Markdown checklist for tracking
            - estimated_time: Rough estimate in minutes
        """
        if self.manifest is None:
            self.load_manifest()
        if self.templates is None:
            self.load_templates()
        
        features = self.manifest.get('features', {})
        if feature_name not in features:
            raise ValueError(f"Feature '{feature_name}' not found in manifest")
        
        feature = features[feature_name]
        affected = feature.get('affects', {})
        
        # Build structured update plan
        update_plan = {
            'feature_name': feature_name,
            'feature_info': {
                'phase': feature.get('phase'),
                'status': feature.get('status'),
                'description': feature.get('description'),
            },
            'affected_docs': [],
            'checklist': '',
            'estimated_time': 0
        }
        
        # Process each doc type
        for doc_type, docs in affected.items():
            for doc in docs:
                doc_path = doc['path']
                change_type = doc['change_type']
                
                # Determine template
                template_category = self.templates.get(doc_type.rstrip('s'), {})
                template_info = template_category.get(change_type, {})
                
                # Estimate time (rough heuristic)
                time_estimate = {
                    'create_new': 20,
                    'add_step': 10,
                    'update_section': 5,
                    'update_table': 3,
                    'update_status': 2,
                }.get(change_type, 5)
                
                update_plan['affected_docs'].append({
                    'path': doc_path,
                    'type': doc_type,
                    'change_type': change_type,
                    'description': doc.get('description', ''),
                    'priority': doc.get('priority', 'medium'),
                    'template': template_info.get('description', ''),
                    'estimated_minutes': time_estimate,
                })
                
                update_plan['estimated_time'] += time_estimate
        
        # Generate checklist
        update_plan['checklist'] = self._generate_checklist(update_plan)
        
        return update_plan
    
    def _generate_checklist(self, plan: Dict) -> str:
        """Generate markdown checklist from update plan."""
        feature = plan['feature_name']
        phase = plan['feature_info']['phase']
        
        checklist = f"# Phase {phase} Documentation Updates: {feature}\n\n"
        checklist += f"**Status:** {plan['feature_info']['status']}\n"
        checklist += f"**Estimated Time:** {plan['estimated_time']} minutes\n\n"
        checklist += "## Required Changes\n\n"
        
        # Group by priority
        high_priority = [d for d in plan['affected_docs'] if d['priority'] == 'high']
        medium_priority = [d for d in plan['affected_docs'] if d['priority'] == 'medium']
        low_priority = [d for d in plan['affected_docs'] if d['priority'] == 'low']
        
        if high_priority:
            checklist += "### High Priority\n\n"
            for doc in high_priority:
                checklist += f"- [ ] **{doc['path']}** - {doc['description']}\n"
                checklist += f"  - Change: `{doc['change_type']}`\n"
                checklist += f"  - Est: {doc['estimated_minutes']}min\n\n"
        
        if medium_priority:
            checklist += "### Medium Priority\n\n"
            for doc in medium_priority:
                checklist += f"- [ ] {doc['path']} - {doc['description']}\n"
                checklist += f"  - Change: `{doc['change_type']}`\n\n"
        
        if low_priority:
            checklist += "### Low Priority\n\n"
            for doc in low_priority:
                checklist += f"- [ ] {doc['path']} - {doc['description']}\n\n"
        
        return checklist
    
    async def plan_updates_for_phase(self, phase: int) -> Dict:
        """
        Generate update plan for all features in a phase.
        
        Args:
            phase: Phase number (e.g., 10)
        
        Returns:
            Combined update plan for all features in the phase
        """
        if self.manifest is None:
            self.load_manifest()
        
        features = self.manifest.get('features', {})
        phase_features = {
            name: data for name, data in features.items()
            if data.get('phase') == phase
        }
        
        if not phase_features:
            return {
                'phase': phase,
                'features': [],
                'total_docs': 0,
                'total_time': 0,
                'checklist': f"# Phase {phase} Documentation Updates\n\nNo features found for this phase.\n"
            }
        
        # Combine plans for all features
        combined = {
            'phase': phase,
            'features': [],
            'total_docs': 0,
            'total_time': 0,
            'checklist': f"# Phase {phase} Documentation Updates\n\n"
        }
        
        for feature_name in phase_features:
            plan = await self.plan_updates_for_feature(feature_name)
            combined['features'].append(plan)
            combined['total_docs'] += len(plan['affected_docs'])
            combined['total_time'] += plan['estimated_time']
            combined['checklist'] += f"\n{plan['checklist']}\n"
        
        return combined
    
    async def get_template_for_change(
        self,
        doc_type: str,
        change_type: str
    ) -> Optional[str]:
        """
        Get the template for a specific change type.
        
        Args:
            doc_type: Type of doc (tutorial, how_to, reference, explanation)
            change_type: Type of change (create_new, add_step, etc.)
        
        Returns:
            Template string or None if not found
        """
        if self.templates is None:
            self.load_templates()
        
        template_category = self.templates.get(doc_type, {})
        template_info = template_category.get(change_type, {})
        
        return template_info.get('template')


# Tool function for agent use
async def plan_documentation_updates(
    feature_name: str = None,
    phase: int = None
) -> str:
    """
    Plan documentation updates for a feature or phase.
    
    Args:
        feature_name: Name of feature from manifest (e.g., 'multi_project_support')
        phase: Phase number (e.g., 10)
    
    Returns:
        Markdown checklist of required documentation updates
    
    Example:
        >>> result = await plan_documentation_updates(feature_name='multi_project_support')
        >>> print(result)
        # Phase 10 Documentation Updates: multi_project_support
        ...
    """
    planner = DocUpdatePlanner()
    
    try:
        if feature_name:
            plan = await planner.plan_updates_for_feature(feature_name)
            return plan['checklist']
        elif phase:
            plan = await planner.plan_updates_for_phase(phase)
            return plan['checklist']
        else:
            return "Error: Must provide either feature_name or phase"
    
    except Exception as e:
        return f"Error planning documentation updates: {str(e)}"


async def get_update_template(
    doc_type: str,
    change_type: str
) -> str:
    """
    Get template for a specific documentation update.
    
    Args:
        doc_type: Type of document (tutorial, how_to, reference, explanation)
        change_type: Type of change (create_new, add_step, update_section, etc.)
    
    Returns:
        Template string with placeholders like {variable_name}
    
    Example:
        >>> template = await get_update_template('how_to', 'create_new')
        >>> print(template)
        ---
        type: how-to
        ...
    """
    planner = DocUpdatePlanner()
    
    try:
        template = await planner.get_template_for_change(doc_type, change_type)
        if template:
            return template
        else:
            return f"Error: No template found for {doc_type}.{change_type}"
    
    except Exception as e:
        return f"Error retrieving template: {str(e)}"


# CLI for testing
if __name__ == "__main__":
    async def main():
        # Example: Plan updates for Phase 10
        logger.info("Planning documentation updates for Phase 10...")
        checklist = await plan_documentation_updates(phase=10)
        logger.info(checklist)
        
        logger.info("\n" + "="*80 + "\n")
        
        # Example: Get template for creating a new how-to guide
        logger.info("Getting template for new how-to guide...")
        template = await get_update_template('how_to', 'create_new')
        logger.info(template)
    
    asyncio.run(main())
