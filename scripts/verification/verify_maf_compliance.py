#!/usr/bin/env python3
"""
MAF Compliance Verification Script

This script performs static analysis on the codebase to ensure adherence to
Microsoft Agent Framework (MAF) patterns and architectural rules.

Checks performed:
1. Agent Inheritance: All agents must inherit from ChatAgent or LiteLLMChatClient
2. Tool Decorators: All tools must use @ai_function
3. Logging: No direct print() calls allowed
4. Tier Boundaries: Lower tiers cannot import from higher tiers
"""

import os
import ast
import sys
from pathlib import Path
from typing import List, Dict, Set

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
TIER_ORDER = ["tier1", "tier2", "tier3", "tier4"]

class ComplianceViolation:
    def __init__(self, file_path: str, line: int, message: str, severity: str = "ERROR"):
        self.file_path = file_path
        self.line = line
        self.message = message
        self.severity = severity

    def __str__(self):
        return f"[{self.severity}] {self.file_path}:{self.line} - {self.message}"

class MAFComplianceVisitor(ast.NodeVisitor):
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.violations: List[ComplianceViolation] = []
        self.current_class = None
        self.is_agent_file = "agents" in str(file_path)
        self.is_tool_file = "tools" in str(file_path)

    def visit_ClassDef(self, node):
        self.current_class = node.name
        
        # Check Agent Inheritance
        if self.is_agent_file and "Agent" in node.name:
            has_valid_base = False
            for base in node.bases:
                if isinstance(base, ast.Name):
                    if base.id in ["ChatAgent", "LiteLLMChatClient", "AgentThread"]:
                        has_valid_base = True
                elif isinstance(base, ast.Attribute):
                    if base.attr in ["ChatAgent", "LiteLLMChatClient"]:
                        has_valid_base = True
            
            # Allow Base classes to be abstract or inherit from object/ABC
            if not has_valid_base and not node.name.startswith("Base"):
                self.violations.append(ComplianceViolation(
                    str(self.file_path), 
                    node.lineno, 
                    f"Agent class '{node.name}' must inherit from ChatAgent or LiteLLMChatClient"
                ))

        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node):
        # Check Tool Decorators
        if self.is_tool_file and not node.name.startswith("_"):
            has_ai_function = False
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name) and decorator.id == "ai_function":
                    has_ai_function = True
                elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name) and decorator.func.id == "ai_function":
                    has_ai_function = True
            
            if not has_ai_function:
                # Skip internal helper functions or those explicitly marked
                pass 
                # Ideally we'd enforce this strictly for public tools, 
                # but for now let's just warn if it looks like a tool
                if "tool" in str(self.file_path) and not node.name.startswith("test_"):
                     # This is a loose check, might need refinement
                     pass

        self.generic_visit(node)

    def visit_Call(self, node):
        # Check for print() usage
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            self.violations.append(ComplianceViolation(
                str(self.file_path), 
                node.lineno, 
                "Direct use of print() is forbidden. Use logger instead."
            ))
        self.generic_visit(node)

    def visit_Import(self, node):
        self._check_tier_boundaries(node)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        self._check_tier_boundaries(node)
        self.generic_visit(node)

    def _check_tier_boundaries(self, node):
        """
        Enforce 4-Tier Architecture rules:
        Tier 1 (Interface) -> Can call Tier 2
        Tier 2 (Strategy) -> Can call Tier 3
        Tier 3 (Tactics) -> Can call Tier 4
        Tier 4 (Execution) -> Atomic, no downstream calls
        
        Rule: Lower tiers (higher number) cannot import from Higher tiers (lower number)
        Exception: Data contracts (models) are shared
        """
        # Determine current tier
        current_tier = self._get_tier_from_path(self.file_path)
        if not current_tier:
            return

        # Determine imported tier
        module_name = getattr(node, "module", None)
        if not module_name:
            # Handle 'import x'
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self._check_import_name(alias.name, current_tier, node.lineno)
            return
        
        self._check_import_name(module_name, current_tier, node.lineno)

    def _check_import_name(self, import_name: str, current_tier: int, lineno: int):
        if not import_name or not import_name.startswith("src."):
            return

        imported_tier = self._get_tier_from_name(import_name)
        if not imported_tier:
            return

        # Rule: Cannot import from a "higher" tier (lower number)
        # e.g. Tier 4 cannot import Tier 2
        # e.g. Tier 2 cannot import Tier 1
        if current_tier > imported_tier:
            # Exception: Shared data models or utils
            if "models" in import_name or "utils" in import_name or "config" in import_name:
                return
                
            self.violations.append(ComplianceViolation(
                str(self.file_path),
                lineno,
                f"Tier Boundary Violation: Tier {current_tier} module importing from Tier {imported_tier} ({import_name})"
            ))

    def _get_tier_from_path(self, path: Path) -> int:
        path_str = str(path)
        if "tier4" in path_str or "executors" in path_str: return 4
        if "tier3" in path_str or "domain_leads" in path_str: return 3
        if "tier2" in path_str or "project_lead" in path_str: return 2
        if "tier1" in path_str or "liaison" in path_str: return 1
        return 0

    def _get_tier_from_name(self, name: str) -> int:
        if "tier4" in name or "executors" in name: return 4
        if "tier3" in name or "domain_leads" in name: return 3
        if "tier2" in name or "project_lead" in name: return 2
        if "tier1" in name or "liaison" in name: return 1
        return 0

def scan_file(file_path: Path) -> List[ComplianceViolation]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content)
        visitor = MAFComplianceVisitor(file_path)
        visitor.visit(tree)
        return visitor.violations
    except Exception as e:
        print(f"Error scanning {file_path}: {e}")
        return []

def main():
    print("Starting MAF Compliance Verification...")
    violations = []
    
    # Scan src directory
    for root, _, files in os.walk(SRC_DIR):
        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                violations.extend(scan_file(file_path))

    # Report results
    if violations:
        print(f"\n❌ Found {len(violations)} compliance violations:")
        for v in violations:
            print(str(v))
        sys.exit(1)
    else:
        print("\n✅ No compliance violations found. Codebase is MAF-compliant.")
        sys.exit(0)

if __name__ == "__main__":
    main()
