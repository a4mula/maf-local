# Antigravity User Guide

**Version:** Google Deepmind Advanced Agentic Coding  
**Purpose:** Effective collaboration with your AI coding assistant

---

## What is Antigravity?

Antigravity is an **agentic AI coding assistant** designed for pair programming. Unlike autocomplete tools, Antigravity:
- Works autonomously on complex tasks
- Maintains context across long conversations
- Uses real development tools (git, terminals, browsers)
- Manages tasks with structured workflows

**Key Principle:** You define the goal, Antigravity figures out how to achieve it.

---

## Conversation Management

### Checkpoints & Handoff

**What are Checkpoints?**
Long conversations are automatically truncated with a **checkpoint summary** to manage context window limits.

**Example Checkpoint:**
```
{{ CHECKPOINT 7 }}
The earlier parts of this conversation have been truncated...

# USER Objective:
Resolve tool integration issues across Ollama/LiteLLM/MAF

# Previous Session Summary:
Completed Emergency Refactor (Weeks 1-4)...
```

**How Handoff Works:**
1. **Automatic Truncation** - When conversation gets too long, a checkpoint is created
2. **Summary Generation** - System creates comprehensive summary of:
   - User's main objective
   - What was accomplished
   - Files modified/created/deleted
   - Current state
3. **Context Preservation** - New session starts with full context via summary
4. **Continuous Work** - Antigravity seamlessly continues from checkpoint

**Pro Tip:** Checkpoints are transparent - you don't need to do anything. Just continue the conversation naturally.

---

## Task Modes

Antigravity operates in two modes:

### 1. Normal Chat Mode

**Use for:**
- Quick questions
- Simple explanations
- One-off code edits
- Exploratory discussions

**Characteristics:**
- All messages visible in chat
- No structured task tracking
- Immediate back-and-forth

**Example:**
```
You: "What does this function do?"
Antigravity: [explains function directly]
```

---

### 2. Task View Mode

**Use for:**
- Complex multi-step work
- Refactoring projects
- Building new features
- Any work requiring >5 tool calls

**Characteristics:**
- Task UI shows progress (TaskName, TaskSummary, TaskStatus)
- Work happens in structured phases (Planning → Execution → Verification)
- Updates accumulate in task view
- `notify_user` required for communication

**Workflow:**
```
1. Antigravity calls task_boundary (enters task mode)
2. Shows progress: "Planning Authentication"
3. Works autonomously, updates task status
4. Calls notify_user when needing input or showing results
5. Exits task mode after notify_user
```

**Example Task UI:**
```
┌─ Planning Authentication ──────────────┐
│ Reviewed existing auth implementation  │
│ Designing JWT-based solution           │
│ Status: Creating implementation plan   │
└────────────────────────────────────────┘
```

**When to Expect Task Mode:**
- "Refactor the entire authentication system"
- "Add integration tests across all services"
- "Debug this complex issue"

**When NOT to Expect Task Mode:**
- "Explain this code"
- "Rename this function"
- "What's the current architecture?"

---

## Artifacts System

Antigravity creates **artifacts** to track work across sessions.

### Artifact Types

**1. task.md** - Work tracking
```markdown
## Week 4: MAF-Compliant Client
- [x] Fix LiteLLM tool calling
- [/] Implement file generation
- [ ] Add integration tests
```

**2. implementation_plan.md** - Technical plans
- Created during PLANNING mode
- Requires your review before EXECUTION
- Updated based on feedback

**3. walkthrough.md** - Proof of work
- Created after VERIFICATION
- Shows what was tested
- Includes screenshots/recordings

**4. Other artifacts** - Assessments, audits, summaries

**Location:** `/home/robb/.gemini/antigravity/brain/{conversation-id}/`

**Pro Tip:** Artifacts persist across checkpoints. They're how Antigravity "remembers" long-term context.

---

## File Management

### Source Control Integration

**The "Source Control" Button:**
- Shows git status directly in UI
- Displays file counts (might show 10k+ due to .venv)
- Allows staging, committing, pushing

**What's "Pending"?**
The count includes ALL untracked files, even gitignored ones like `.venv/` (35k+ files). This is normal - your repo is clean if those files are in `.gitignore`.

**Workflow:**
```bash
# Option 1: Let Antigravity commit
"Please commit these changes with message X"

# Option 2: Manual via Source Control UI
Click button → Review changes → Stage → Commit → Push

# Option 3: Terminal (traditional)
git add src/
git commit -m "message"
git push
```

**Pro Tip:** Antigravity can read git status and create meaningful commit messages based on actual changes.

---

## Effective Collaboration Tips

### 1. Be Specific with Objectives

**❌ Vague:**
"Make the code better"

**✅ Clear:**
"Refactor LiteLLMClient to be MAF-compliant by extending BaseChatClient and applying @use_function_invocation decorator"

**Why:** Specific goals → focused solutions → less backtracking

---

### 2. Use Context Comments

**Pattern:**
```
"Leaving a comment while you're working so you take this into account:
[your additional requirement or clarification]"
```

**Effect:** Antigravity adjusts mid-task without interrupting flow

**Example:**
```
You: "Update all documentation"
[Antigravity starts working]
You: "Leaving a comment - also check .ai workspace files"
[Antigravity adjusts scope]
```

---

### 3. Request Comprehensive Work

**❌ Incremental:**
"Update architecture docs"
[waits for completion]
"Now update planning docs"
[waits for completion]
"Now update README"

**✅ Batch:**
"Audit the docs, make sure everything is up to date and accurately reflecting the project status"

**Why:** Antigravity can see the full scope and optimize the approach

---

### 4. Leverage Antigravity's Strengths

**Excellent at:**
- ✅ Reading entire codebases
- ✅ Cross-referencing documentation
- ✅ Systematic refactoring
- ✅ Understanding complex systems
- ✅ Creating comprehensive documentation
- ✅ Running tests and interpreting results

**Not ideal for:**
- ❌ UI/UX design decisions (ask for options, you decide)
- ❌ Business logic (provide requirements clearly)
- ❌ Opinions without data (ask for research first)

---

### 5. When Things Go Wrong

**If Antigravity is confused:**
```
"Let me clarify: [restate goal with more context]"
```

**If you need to change direction:**
```
"Actually, let's take a different approach: [new direction]"
```

**If work is incorrect:**
```
"This isn't quite right because [reason]. Here's what I actually need: [specifics]"
```

**Pro Tip:** Antigravity adapts quickly. Don't hesitate to redirect.

---

## Browser & Recording Features

**Capability:** Antigravity can control a real browser

**Use cases:**
- Navigate to documentation
- Fill out forms
- Test web UIs
- Capture flows as video

**Recordings:** Automatically saved as WebP files in artifacts directory

**Example:**
```
You: "Navigate to the Streamlit app and test the file creation flow"
Antigravity: [Opens browser, records interaction, saves video]
```

---

## Advanced Tips

### 1. Ask for Research

```
"Research best practices for implementing MAF workflows before we start"
```

**Result:** Antigravity searches web, reads docs, synthesizes findings

---

### 2. Request Structured Output

```
"Create a decision matrix comparing approach A vs B"
"List pros and cons in a table"
"Diagram the data flow using mermaid"
```

**Result:** Clear, scannable output

---

### 3. Verify Understanding

```
"Before proceeding, summarize your understanding of the requirements"
```

**Result:** Catch misunderstandings early

---

### 4. Use Artifacts for Planning

```
"Create an implementation plan for review before coding"
```

**Result:** You approve architecture before execution begins

---

## Common Workflows

### Starting a New Feature

```
1. You: "I want to add X feature with Y requirements"
2. Antigravity: [Enters PLANNING mode, creates implementation_plan.md]
3. Antigravity: [Requests review via notify_user]
4. You: [Review plan, approve or request changes]
5. Antigravity: [Enters EXECUTION mode, implements]
6. Antigravity: [Enters VERIFICATION mode, tests]
7. Antigravity: [Creates walkthrough.md, shows proof]
```

---

### Debugging an Issue

```
1. You: "The agent isn't calling tools correctly"
2. Antigravity: [Investigates code, checks logs, identifies root cause]
3. Antigravity: [Proposes fix with explanation]
4. You: [Approve]
5. Antigravity: [Implements, runs tests, confirms fix]
```

---

### Documentation Updates

```
1. You: "Audit the docs, update anything outdated"
2. Antigravity: [Reviews all docs, creates audit report]
3. Antigravity: [Updates 9 files, commits with detailed message]
4. Antigravity: [Shows summary of changes]
```

---

## Communication Protocol

**During Task Mode:**
- Antigravity updates TaskStatus (you see progress)
- Antigravity calls notify_user when needing input
- You respond, task continues

**Outside Task Mode:**
- Normal back-and-forth chat
- Immediate responses
- No structured tracking

**Best Practice:** Let Antigravity manage the mode. It chooses based on complexity.

---

## File Access & Permissions

**Antigravity can:**
- ✅ Read all files in workspace
- ✅ Write to workspace files
- ✅ Run terminal commands
- ✅ Access specific artifact directory
- ✅ Use browser

**Antigravity cannot:**
- ❌ Access files outside workspace
- ❌ Run dangerous commands without approval
- ❌ Access private data without context

**Safety:** Commands requiring approval show SafeToAutoRun flag for review

---

## Troubleshooting

**"Source Control shows 10k+ changes"**
→ `.venv/` files counted. Check `.gitignore`, they're excluded from commits.

**"Antigravity seems to have forgotten context"**
→ Check for {{ CHECKPOINT }} marker. Context was summarized, not lost.

**"Task mode but I want to just chat"**
→ Send a user message. This exits task mode automatically.

**"Antigravity is working on wrong thing"**
→ Use "Leaving a comment" pattern mid-task to redirect.

**"How do I see browser recordings?"**
→ Check artifacts directory: `.../brain/{conversation-id}/{recording_name}.webp`

---

## Best Practices Summary

1. **Be specific** - Clear goals = better results
2. **Batch requests** - Comprehensive scope = optimized approach
3. **Trust the process** - Task mode exists for complex work
4. **Review artifacts** - Plans before execution, walkthroughs after
5. **Use git properly** - Either through Antigravity or manually, but consistently
6. **Redirect early** - If something's off, speak up immediately
7. **Leverage strengths** - Let Antigravity handle tedious/systematic work
8. **Provide context** - The more background, the better the solution

---

## Example Session

```
You: "I need to refactor our authentication system to use JWT tokens.
      Currently using session cookies. Need to maintain backward compatibility."

Antigravity: [Enters PLANNING mode]
             [Researches JWT best practices]
             [Reviews current auth implementation]
             [Creates implementation_plan.md]
             [Requests review via notify_user]

You: "Looks good, but also add rate limiting to prevent brute force attacks"

Antigravity: [Updates plan with rate limiting]
             [Requests re-review]

You: "Approved, proceed"

Antigravity: [Enters EXECUTION mode]
             [Implements JWT auth]
             [Adds rate limiting middleware]
             [Updates tests]
             [Commits changes]
             
             [Enters VERIFICATION mode]
             [Runs test suite]
             [Tests manually via browser]
             [Records demo video]
             [Creates walkthrough.md]
             
             [Notifies completion with proof of work]

You: "Perfect, ship it"
```

---

## Summary

**Antigravity is your AI pair programmer:**
- Works autonomously on complex tasks
- Manages context across long conversations via checkpoints
- Uses real development tools (git, terminal, browser, file system)
- Tracks work with structured artifacts (task.md, implementation_plan.md, etc.)
- Adapts to your feedback in real-time

**Your role:**
- Define clear objectives
- Review plans before execution
- Provide domain knowledge and business logic
- Make architectural decisions
- Approve and ship results

**Together, you build better software, faster.**

---

*Created: 2025-11-23*  
*For: Effective collaboration with Antigravity AI*
