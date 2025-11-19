import asyncio
import io
import contextlib
import traceback
from typing import Awaitable

# We define the function as synchronous here for simplicity, but use an async wrapper
# to satisfy the async CoreAgent requirement, which allows it to be called from the
# main async loop in CoreAgent.py.
def _execute_code_sync(code: str) -> str:
    """
    Synchronous function to execute a block of Python code and return the output.
    """
    try:
        # 1. Strip common prefixes/suffixes (e.g., if the LLM adds print() or backticks)
        code = code.strip()
        if code.startswith('```') and code.endswith('```'):
            code = code[3:-3]
            if code.startswith("python"):
                code = code[6:]
        
        # 2. Use io.StringIO to capture stdout
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            # Compile and execute the code
            exec(code.strip())
        
        # 3. Get the captured output
        output = f.getvalue().strip()
        
        # 4. Handle simple expression output (e.g., if the LLM just sends "1923 * 488")
        if not output and code.strip() and not any(op in code for op in ['=', 'def ', 'class ']):
            # If the code was just a simple expression without an explicit 'print', force capture
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                exec(f'print({code.strip()})')
            output = f.getvalue().strip()

        return output if output else "No output generated."

    except Exception as e:
        # Return a concise error message for the LLM to process
        return f"Execution Error: {type(e).__name__}: {str(e)}"

# The 'execute_code' function signature must match the tool registry.
async def execute_code(code: str) -> str:
    """
    A robust, asynchronous wrapper for the code execution tool.
    
    Args:
        code: The Python code block to execute.
    
    Returns:
        The clean stdout output or a concise error message.
    """
    # Use asyncio.to_thread to run the synchronous execution function 
    # in a separate thread, preventing it from blocking the main event loop.
    return await asyncio.to_thread(_execute_code_sync, code)
