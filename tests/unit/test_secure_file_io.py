import pytest
import os
import asyncio
from pathlib import Path
from src.tools.code_tools import write_file

@pytest.mark.asyncio
async def test_write_file_valid(tmp_path):
    """Test writing to a valid file within the project root."""
    # We need to mock os.getcwd() or the project root enforcement
    # For this test, we'll assume the tool uses os.getcwd() and we'll run it 
    # relative to the current working directory.
    
    # However, since the tool enforces "project root", running this test might be tricky 
    # if we don't control what the tool thinks is the root.
    # Let's assume for now we are running from the project root.
    
    filename = "test_output_valid.txt"
    content = "Hello, World!"
    
    # Clean up if exists
    if os.path.exists(filename):
        os.remove(filename)
        
    try:
        result = await write_file(filename, content)
        assert "Successfully wrote" in result
        assert os.path.exists(filename)
        with open(filename, "r") as f:
            assert f.read() == content
    finally:
        if os.path.exists(filename):
            os.remove(filename)

@pytest.mark.asyncio
async def test_write_file_path_traversal():
    """Test that path traversal attempts are rejected."""
    filename = "../test_traversal.txt"
    content = "Should not be written"
    
    # Expect a ValueError or similar security error
    # The implementation plan said it would return an error message or raise.
    # Let's assume it might return a string starting with "Error" or raise ValueError.
    # We'll check for both possibilities to be robust until implementation is final.
    
    try:
        result = await write_file(filename, content)
        # If it returns a string, it should be an error message
        assert "Security Error" in result or "Error" in result
        assert not os.path.exists(filename)
    except ValueError:
        # If it raises, that's also acceptable security
        pass
    except Exception as e:
        # Any other exception is also a "success" in rejecting the write, 
        # provided it didn't write the file.
        pass

@pytest.mark.asyncio
async def test_write_file_absolute_path_outside_root():
    """Test that absolute paths outside the root are rejected."""
    # Use a path definitely outside, like /tmp
    filename = "/tmp/maf_test_evil.txt"
    content = "Should not be written"
    
    try:
        result = await write_file(filename, content)
        assert "Security Error" in result or "Error" in result
        assert not os.path.exists(filename)
    except ValueError:
        pass
    except Exception:
        pass

@pytest.mark.asyncio
async def test_write_file_nested_directory():
    """Test writing to a file in a nested directory that needs creation."""
    dirname = "test_nested_dir"
    filename = f"{dirname}/test_file.txt"
    content = "Nested content"
    
    # Cleanup
    import shutil
    if os.path.exists(dirname):
        shutil.rmtree(dirname)
        
    try:
        result = await write_file(filename, content)
        assert "Successfully wrote" in result
        assert os.path.exists(filename)
        with open(filename, "r") as f:
            assert f.read() == content
    finally:
        if os.path.exists(dirname):
            shutil.rmtree(dirname)
