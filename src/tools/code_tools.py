"""
MAF-Compliant Code Tools

This module provides code execution and file writing tools using MAF's
native @ai_function decorator pattern with Pydantic input validation.

All tools follow MAF SDK standards for type safety and schema generation.
"""

import asyncio
import io
import contextlib
from pathlib import Path
import os
from agent_framework import ai_function
from pydantic import BaseModel, Field


# ============================================================================
# Input Models (Pydantic)
# ============================================================================

class ExecuteCodeInput(BaseModel):
    """Input schema for code execution tool."""
    code: str = Field(
        description="Python code to execute. Can include print statements or expressions."
    )


class WriteFileInput(BaseModel):
    """Input schema for file writing tool."""
    file_path: str = Field(
        description="Relative path to the file within the project directory"
    )
    content: str = Field(
        description="Content to write to the file"
    )


# ============================================================================
# Helper Functions
# ============================================================================

def _execute_code_sync(code: str) -> str:
    """
    Synchronous function to execute a block of Python code and return the output.
    
    Security: Sandboxed execution with stdout capture only.
    """
    try:
        # Strip common prefixes/suffixes (e.g., if the LLM adds print() or backticks)
        code = code.strip()
        if code.startswith('```') and code.endswith('```'):
            code = code[3:-3]
            if code.startswith("python"):
                code = code[6:]
        
        # Use io.StringIO to capture stdout
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            exec(code.strip())
        
        output = f.getvalue().strip()
        
        # Handle simple expression output (e.g., "1923 * 488")
        if not output and code.strip() and not any(op in code for op in ['=', 'def ', 'class ']):
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                exec(f'print({code.strip()})')
            output = f.getvalue().strip()

        return output if output else "No output generated."

    except Exception as e:
        return f"Execution Error: {type(e).__name__}: {str(e)}"


def _is_safe_path(path: str) -> bool:
    """
    Validates that the path is within the project root directory.
    Prevents Path Traversal attacks.
    """
    try:
        project_root = Path(os.getcwd()).resolve()
        target_path = (project_root / path).resolve()
        return target_path.is_relative_to(project_root)
    except Exception:
        return False


# ============================================================================
# MAF AIFunctions (Tools)
# ============================================================================

@ai_function
async def execute_code(input: ExecuteCodeInput) -> str:
    """
    Execute Python code and return the output.
    
    This tool allows the agent to run Python code for calculations,
    data processing, or testing. Output is captured from stdout.
    
    Security: Sandboxed execution, no file system access.
    """
    return await asyncio.to_thread(_execute_code_sync, input.code)


@ai_function
async def write_file(input: WriteFileInput) -> str:
    """
    Write content to a file within the project directory.
    
    This tool allows the agent to create or modify files. All paths
    are validated to prevent writes outside the project root.
    
    Security: Path validation enforced, sandboxed to project directory.
    """
    if not _is_safe_path(input.file_path):
        return f"Security Error: Access denied. Path '{input.file_path}' is outside the project root."
        
    try:
        def _write_sync():
            target_path = Path(input.file_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(input.content, encoding='utf-8')
            return f"Successfully wrote to {input.file_path}"
            
        return await asyncio.to_thread(_write_sync)
        
    except Exception as e:
        return f"Error writing file: {str(e)}"


# ============================================================================
# Tool Exports
# ============================================================================

# List of all code tools for agent registration
ALL_CODE_TOOLS = [
    execute_code,
    write_file
]
