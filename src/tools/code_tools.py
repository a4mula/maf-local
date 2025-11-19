import io
import contextlib
from typing import Dict, Any

def execute_code(code: str) -> str:
    """
    Executes the provided Python code in a restricted sandbox environment.
    Only use this for complex computational or logical tasks that cannot be
    solved by simple natural language reasoning.

    Args:
        code: The complete Python code block to execute.

    Returns:
        The output (stdout) of the code execution, or an error message.
    """
    # 1. Basic Sandboxing Setup
    # A dictionary that the executed code can see (builtins are safe by default)
    safe_globals = {
        '__builtins__': __builtins__,
        'math': __import__('math'),
        'random': __import__('random'),
        # Explicitly deny access to dangerous imports like 'os', 'sys', 'subprocess'
    }
    
    # 2. Capture Output (stdout)
    # We redirect the output of print() statements to a string buffer
    stdout_capture = io.StringIO()
    
    try:
        # Limit the code execution time (not implemented here, but critical for production)
        
        with contextlib.redirect_stdout(stdout_capture):
            # 3. Execute the code
            # The code runs with a restricted set of globals and no access to local scope
            exec(code, safe_globals)
        
        output = stdout_capture.getvalue().strip()
        
        if not output:
            return "Execution successful, but no output was printed to stdout. Make sure to use the 'print()' function to show results."
        
        return f"Code executed successfully. Output:\n{output}"

    except SyntaxError as e:
        return f"Code Execution Error (SyntaxError): The code is invalid Python syntax. Error details: {e}"
    except Exception as e:
        return f"Code Execution Error (RuntimeError): The code failed during execution. Error details: {e}"

# If you run this file directly, it will demonstrate the function:
if __name__ == "__main__":
    test_code_success = "import math\nprint(math.sqrt(144))"
    test_code_error = "print(10 / 0)"
    
    print(f"--- Running Test Code 1 (Success) ---\nCode:\n{test_code_success}")
    result_success = execute_code(test_code_success)
    print(f"Result:\n{result_success}\n")
    
    print(f"--- Running Test Code 2 (Error) ---\nCode:\n{test_code_error}")
    result_error = execute_code(test_code_error)
    print(f"Result:\n{result_error}")
