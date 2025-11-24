"""
Unit tests for PermissionFilter middleware (Phase 1 U.B.E.)

Tests Principle of Least Authority (PoLA) enforcement:
- Only DocumentationAgent and ProjectLeadAgent can call FileWriter
- Other agents are blocked with GovernanceException
"""

import pytest
from src.governance.permission_filter import PermissionFilter, GovernanceException


class TestPermissionFilter:
    """Unit tests for PermissionFilter middleware."""
    
    @pytest.mark.asyncio
    async def test_authorized_project_lead_can_write_files(self):
        """Test that ProjectLeadAgent is authorized to write files."""
        filter_instance = PermissionFilter()
        
        # Mock context with authorized agent (ProjectLeadAgent)
        class MockFunction:
            name = "FileWriter"
        
        class MockContext:
            function = MockFunction()
            metadata = {"agent_name": "ProjectLeadAgent"}  # MAF injects agent name here
            kwargs = {}
        
        context = MockContext()
        
        # Track that next handler was called
        called = False
        async def next_handler(ctx):
            nonlocal called
            called = True
        
        # Should not raise GovernanceException
        await filter_instance.process(context, next_handler)
        assert called, "Next handler should be called for authorized agent"
    
    @pytest.mark.asyncio
    async def test_authorized_documentation_agent_can_write_files(self):
        """Test that DocumentationAgent is authorized to write files."""
        filter_instance = PermissionFilter()
        
        # Mock context with authorized agent (DocumentationAgent)
        class MockFunction:
            name = "FileWriter"
        
        class MockContext:
            function = MockFunction()
            metadata = {"agent_name": "DocumentationAgent"}
            kwargs = {}
        
        context = MockContext()
        
        # Track that next handler was called
        called = False
        async def next_handler(ctx):
            nonlocal called
            called = True
        
        # Should not raise GovernanceException
        await filter_instance.process(context, next_handler)
        assert called, "Next handler should be called for authorized agent"
    
    @pytest.mark.asyncio
    async def test_unauthorized_agent_blocked_from_writing_files(self):
        """Test that unauthorized agents cannot call FileWriter."""
        filter_instance = PermissionFilter()
        
        # Mock context with UNAUTHORIZED agent
        class MockFunction:
            name = "FileWriter"
        
        class MockContext:
            function = MockFunction()
            metadata = {"agent_name": "MaliciousAgent"}
            kwargs = {}
        
        context = MockContext()
        
        # Should raise GovernanceException
        with pytest.raises(GovernanceException) as exc_info:
            await filter_instance.process(context, lambda ctx: None)
        
        assert "Unauthorized disk access" in str(exc_info.value)
        assert "MaliciousAgent" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_non_filewriter_functions_pass_through(self):
        """Test that non-FileWriter functions are not blocked."""
        filter_instance = PermissionFilter()
        
        # Mock context with different function (not FileWriter)
        class MockFunction:
            name = "read_file"  # Not FileWriter
        
        class MockContext:
            function = MockFunction()
            metadata = {"agent_name": "AnyAgent"}
            kwargs = {}
        
        context = MockContext()
        
        # Track that next handler was called
        called = False
        async def next_handler(ctx):
            nonlocal called
            called = True
        
        # Should pass through without checking authorization
        await filter_instance.process(context, next_handler)
        assert called, "Next handler should be called for non-FileWriter functions"
    
    @pytest.mark.asyncio
    async def test_write_file_alias_also_blocked(self):
        """Test that 'write_file' function name is also checked (alias)."""
        filter_instance = PermissionFilter()
        
        # Mock context with write_file alias
        class MockFunction:
            name = "write_file"
        
        class MockContext:
            function = MockFunction()
            metadata = {"agent_name": "UnauthorizedAgent"}
            kwargs = {}
        
        context = MockContext()
        
        # Should raise GovernanceException
        with pytest.raises(GovernanceException) as exc_info:
            await filter_instance.process(context, lambda ctx: None)
        
        assert "Unauthorized disk access" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
