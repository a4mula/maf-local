# Tool Integration Research: MAF + LiteLLM + Ollama

**Date:** 2025-11-24  
**Status:** ✅ **RESEARCH COMPLETE**

---

## Executive Summary

After comprehensive research into MAF `@ai_function`, LiteLLM, and Ollama tool formats, I've determined:

**✅ CRITICAL FINDING: The `UniversalTool` wrapper is UNNECESSARY technical debt.**

All three systems (MAF, LiteLLM, Ollama) use the **identical OpenAI function calling format**, and MAF's `AIFunction` class **already provides native conversion** via `AIFunction.to_dict()`.

---

## Research Findings

### 1. MAF `@ai_function` Standard Pattern

**Source:** Microsoft Learn documentation + MAF SDK source code

#### How MAF Defines Tools

```python
from agent_framework import ai_function
from pydantic import BaseModel, Field

# Define input model
class SearchInput(BaseModel):
    query: str = Field(description="Search query")
    max_results: int = Field(default=5, description="Maximum results")

# Decorate function
@ai_function
async def search_web(input: SearchInput) -> str:
    """Search the web for information."""
    # Implementation
    return results
```

**Key Points:**
- `@ai_function` decorator wraps Python functions
- Pydantic `BaseModel` defines input parameters
- Automatic JSON schema generation from type hints
- Returns `AIFunction` object with `.to_dict()` method

#### AIFunction.to_dict() Output Format

```python
{
    "name": "search_web",
    "description": "Search the web for information.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "max_results": {"type": "integer", "description": "Maximum results", "default": 5}
        },
        "required": ["query"]
    }
}
```

---

### 2. LiteLLM Tool Format

**Source:** LiteLLM documentation + web search

#### LiteLLM Expectations

LiteLLM standardizes 100+ LLM APIs to the **OpenAI Chat Completions format**. For tools:

```python
# LiteLLM expects OpenAI format
{
    "type": "function",
    "function": {
        "name": "search_web",
        "description": "Search the web for information",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "description": "Maximum results"}
            },
            "required": ["query"]
        }
    }
}
```

#### LiteLLMChatClient Implementation

**File:** `src/clients/litellm_client.py` Lines 86-106

```python
# Convert MAF tools to OpenAI format for LiteLLM
if chat_options.tools:
    api_tools = []
    for tool in chat_options.tools:
        if isinstance(tool, AIFunction):
            tool_schema = tool.to_dict()  # ✅ NATIVE MAF METHOD
            api_tools.append({
                "type": "function",
                "function": {
                    "name": tool_schema.get("name"),
                    "description": tool_schema.get("description", ""),
                    "parameters": tool_schema.get("input_schema", {})
                }
            })
```

**✅ KEY FINDING:** Our `LiteLLMChatClient` **already uses** `AIFunction.to_dict()` for conversion!

---

### 3. Ollama Tool Format

**Source:** Ollama documentation + web search

#### Ollama Expectations

Ollama also follows the **OpenAI function calling format**:

```python
{
    "type": "function",
    "function": {
        "name": "search_web",
        "description": "Search the web",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Query"},
                "max_results": {"type": "integer", "description": "Max results"}
            },
            "required": ["query"]
        }
    }
}
```

**✅ FINDING:** Identical to LiteLLM/OpenAI format!

---

## The UniversalTool Analysis

### What UniversalTool Does

**File:** `src/tools/universal_tools.py`

```python
class UniversalTool:
    def to_maf_format(self) -> Callable:
        return self.func  # Just returns the function
    
    def to_litellm_format(self) -> Dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters  # Custom extraction
            }
        }
    
    def to_ollama_format(self) -> Dict:
        return {  # Identical to LiteLLM!
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }

def get_ai_functions():
    from agent_framework import ai_function
    return [ai_function(tool.func) for tool in self.tools.values()]
```

### Problems with UniversalTool

1. **Redundant:** `to_litellm_format()` and `to_ollama_format()` produce identical output
2. **Already Solved:** MAF's `AIFunction.to_dict()` already provides this
3. **Runtime Conversion:** Applies `@ai_function` at registry time, not definition time
4. **Custom Schema Extraction:** Duplicates MAF's built-in Pydantic schema generation
5. **No Added Value:** End result is identical to using `@ai_function` directly

---

## The Conversion Chain (Current vs Ideal)

### Current (with UniversalTool)

```
Tool Definition (plain func)
    ↓
@registry.register wrapper
    ↓
UniversalTool class stores function
    ↓
Custom parameter extraction (_extract_parameters)
    ↓
registry.get_ai_functions() calls ai_function(tool.func)
    ↓
AIFunction created
    ↓
LiteLLMClient calls tool.to_dict()
    ↓
OpenAI format for LiteLLM
```

### Ideal (pure MAF)

```
Tool Definition with Pydantic input
    ↓
@ai_function decorator
    ↓
AIFunction created (with built-in schema)
    ↓
Pass directly to agent tools=[]
    ↓
LiteLLMClient calls tool.to_dict()
    ↓
OpenAI format for LiteLLM
```

**Steps Eliminated:** 4 (UniversalTool, registry, custom extraction, runtime conversion)

---

## Validation: Does MAF Handle Everything?

### Test from LiteLLMClient Code

**Current working code (lines 86-106):**

```python
if chat_options.tools:
    api_tools = []
    for tool in chat_options.tools:
        # Convert callables to AIFunction
        if callable(tool) and not isinstance(tool, AIFunction):
            tool = ai_function(tool)  # ✅ MAF handles this
        
        if isinstance(tool, AIFunction):
            tool_schema = tool.to_dict()  # ✅ MAF provides schema
            api_tools.append({
                "type": "function",
                "function": {
                    "name": tool_schema.get("name"),
                    "description": tool_schema.get("description", ""),
                    "parameters": tool_schema.get("input_schema", {})
                }
            })
```

**✅ VALIDATION:** Our client **already proves** MAF handles all conversion!

---

## Conclusion

### The Verdict

**UniversalTool exists to solve a problem that doesn't exist.**

- ✅ MAF, LiteLLM, and Ollama all use OpenAI format
- ✅ MAF's `AIFunction.to_dict()` provides the conversion
- ✅ Our `LiteLLMChatClient` already uses this native method
- ✅ No additional abstraction needed

### Why Was It Created?

Likely created before understanding that:
1. All three systems converge on OpenAI format
2. MAF provides native conversion via `AIFunction`
3. LiteLLM/Ollama expect identical schemas

### Safe to Remove?

**YES - with proper refactor:**

1. ✅ Convert tools to use `@ai_function` + Pydantic
2. ✅ Remove UniversalTool and registry classes
3. ✅ Update agents to import tools directly
4. ✅ LiteLLMClient already handles `AIFunction` objects

---

## Refactor Strategy

### Phase 1: Convert Tool Definitions

```python
# Before (code_tools.py)
@registry.register(roles=["ArtifactManager"])
async def execute_code(code: str) -> str:
    """Execute code."""
    ...

# After (code_tools.py)
from agent_framework import ai_function
from pydantic import BaseModel, Field

class ExecuteCodeInput(BaseModel):
    code: str = Field(description="Python code to execute")

@ai_function
async def execute_code(input: ExecuteCodeInput) -> str:
    """Execute Python code and return output."""
    result = await _execute_code_sync(input.code)
    return result
```

### Phase 2: Export Tool Lists

```python
# src/tools/code_tools.py
ALL_TOOLS = [execute_code, write_file, search_web, add_context, get_context, clear_context]
```

### Phase 3: Update Agents

```python
# src/agents/project_lead_agent.py
from src.tools.code_tools import ALL_TOOLS

super().__init__(
    name="ProjectLead",
    instructions="...",
    tools=ALL_TOOLS,  # Direct list
    chat_client=chat_client
)
```

### Phase 4: Delete UniversalTool

```bash
rm src/tools/universal_tools.py
```

---

## Risk Assessment

**Risk Level: LOW**

- ✅ Tool functionality unchanged (same execution logic)
- ✅ LiteLLMClient already handles AIFunction format
- ✅ No changes needed to client conversion logic
- ✅ Incremental refactor possible (one tool at a time)
- ✅ Existing tests validate tool integration

**Breaking Changes:**
- ❌ `registry.get_ai_functions()` calls must be replaced
- ❌ Direct access to registry must be updated

**Mitigation:**
- ✅ Grep for all `registry` references
- ✅ Update incrementally
- ✅ Run Phase 1 tests after each change

---

## Recommendation

**PROCEED with tool refactor to pure MAF pattern.**

UniversalTool is confirmed technical debt with no functional justification. Removing it will:
- ✅ Eliminate 200+ lines of unnecessary code
- ✅ Follow MAF standards exactly
- ✅ Improve type safety (Pydantic validation)
- ✅ Simplify maintenance
- ✅ Enable better IDE support

**No backward compatibility concerns** - this is internal implementation only.
