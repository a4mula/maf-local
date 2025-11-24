---

# **UNIFIED BOOTSTRAP MANDATE (UBM)**

Version: 1.0 (Merged DAR/ARR)

Target Agent: Bootstrap Agent (DOCS/GPT-120B)

Purpose: Single source of truth for System Initialization, Documentation Alignment, and Architectural Planning.

---

## **SECTION 1: IMMEDIATE BOOTSTRAP ACTIONS (Execute Now)**

You (The Bootstrap Agent) must execute these steps physically during this session.

### **1.1. Reality Establishment**

* **Create .agentignore:** Must include .venv/, .env, \_\_pycache\_\_/, \*.log, node\_modules/, .git/, and meta/agents/\*/working\_container/.  
* **Generate meta/agents/The\_Real\_Index.md:** Parse the file system (respecting ignore rules) and generate the LOD-1 index (Path | Hash | Size | Modified).

### **1.2. Structural Implementation**

* **Create Directory Tree:** meta/agents/{docs, src, upp}/{input, working\_container}/.  
* **Create ADD Files:** Write the \*\_DOMAIN\_DEF.md files using the content defined in **Section 3**.  
* **Create Role Prompts:** Write the role.md files using the templates in **Section 4**.  
* **Create Manifest:** Initialize meta/agents/PROJECT\_MANIFEST.md with the three required sections.

### **1.3. Documentation Debt Resolution (Merged DAR Mandates)**

* **Target:** docs/architecture/CURRENT.md  
  * **Action:** Update Implementation Status table. Change "OLB Workflow" and "Domain Leads" from 🚧 Planned to ✅ Implemented and Active.  
* **Target:** docs/meta/IDEAL\_AGENT\_ARCHITECTURE.md  
  * **Action:** Delete all references to "2-tier MVP". Update Current State to "Phase 2 UBE (4-Tier)".  
* **Target:** docs/feedback/feedback\_full.md  
  * **Action:** **DELETE** this file (Redundant/Anti-pattern).

---

## **SECTION 2: DEFERRED ARCHITECTURAL MANDATES (Write to Manifest)**

Do **not** execute these changes now. You must write these instructions into the \# Project.Planner.State section of the PROJECT\_MANIFEST.md as the initial plan for the **UPP Agent**.

**Mandate ID: ARCH-REFACTOR-01**

1. **Refactor ProjectLeadAgent:** Split monolithic agent into ProjectPlanner (Logic) and ProjectManager (Execution). (Source: ARR Step 2.1).  
2. **Implement PoLA Governance:** Update OLBWorkflow to enforce routing checks based on originating\_agent\_role. (Source: ARR Step 1.3).  
3. **Create DocsDomainLead:** Implement the missing DocsDomainLead agent to support the DOCS workflow. (Source: ARR Step 3.1).

---

## **SECTION 3: AGENT DOMAIN DEFINITIONS (ADD Content)**

Use this exact content to generate the \*\_DOMAIN\_DEF.md files.

### **3.1. UPP\_DOMAIN\_DEF.md**

* **Role:** Project Planner.  
* **Client:** Claude 4.5 Sonnet.  
* **Authority:** Conceptual Scope & Human Interface.  
* **Write Access:** meta/agents/PROJECT\_MANIFEST.md, src/input/SESSION\_TOKEN.md.  
* **Read Access:** All LOD-1 Files (Manifest, The\_Real, docs/).

### **3.2. SRC\_DOMAIN\_DEF.md**

* **Role:** Implementation Manager.  
* **Client:** Gemini 3 Pro.  
* **Authority:** Codebase State & Execution.  
* **Write Access:** src/\*, meta/agents/PROJECT\_MANIFEST.md, docs/input/SESSION\_TOKEN.md.  
* **Read Access:** All LOD-1 Files.

### **3.3. DOCS\_DOMAIN\_DEF.md**

* **Role:** Synchronization Agent.  
* **Client:** GPT-120B.  
* **Authority:** Documentation, Audit & Governance.  
* **Write Access:** docs/\*, meta/agents/PROJECT\_MANIFEST.md, upp/input/SESSION\_TOKEN.md.  
* **Read Access:** All LOD-1 Files.

---

## **SECTION 4: ROLE PROMPT TEMPLATES (The Session Guardrails)**

**CRITICAL INSTRUCTION:** When generating the role.md files, you **MUST** include the "TERMINAL PROTOCOL" section exactly as written below. This ensures agents never forget how to end their session.

### **4.1. Template for meta/agents/upp/role.md**

Markdown  
\# ROLE: Project Planner (UPP)  
\*\*Context:\*\* You are the Conceptual Control implementation.  
\*\*Directives:\*\* Read \`../UPP\_DOMAIN\_DEF.md\` for your strict boundaries.

\*\*TERMINAL PROTOCOL (HOW TO END SESSION):\*\*  
When your planning task is complete:  
1\. \*\*WRITE STATE:\*\* Update \`\# Project.Planner.State\` in \`PROJECT\_MANIFEST.md\` with the new \`StrategicPlan\`.  
2\. \*\*TRIGGER HANDOFF:\*\* Create/Overwrite file \`src/input/SESSION\_TOKEN.md\`.  
   \* Content: \`status: READY\_FOR\_IMPLEMENTATION, plan\_id: \[ID\]\`  
3\. \*\*STOP:\*\* Output "HANDOFF COMPLETE" and terminate.

### **4.2. Template for meta/agents/src/role.md**

Markdown  
\# ROLE: Implementation Manager (SRC)  
\*\*Context:\*\* You are the Code Execution Engine.  
\*\*Directives:\*\* Read \`../SRC\_DOMAIN\_DEF.md\` for your strict boundaries.

\*\*TERMINAL PROTOCOL (HOW TO END SESSION):\*\*  
When your execution is complete:  
1\. \*\*WRITE STATE:\*\* Update \`\# Implementation.Feedback\` in \`PROJECT\_MANIFEST.md\` with your \`CodeCommitReport\` summary.  
2\. \*\*TRIGGER HANDOFF:\*\* Create/Overwrite file \`docs/input/SESSION\_TOKEN.md\`.  
   \* Content: \`status: CODE\_COMPLETE, commit: \[HASH\]\`  
3\. \*\*STOP:\*\* Output "HANDOFF COMPLETE" and terminate.

### **4.3. Template for meta/agents/docs/role.md**

Markdown  
\# ROLE: Synchronization Agent (DOCS)  
\*\*Context:\*\* You are the Audit and Governance Engine.  
\*\*Directives:\*\* Read \`../DOCS\_DOMAIN\_DEF.md\` for your strict boundaries.

\*\*TERMINAL PROTOCOL (HOW TO END SESSION):\*\*  
When your audit and updates are complete:  
1\. \*\*WRITE STATE:\*\* Update \`\# Documentation.Governance\` in \`PROJECT\_MANIFEST.md\` with your \`ProjectSessionReport\` summary.  
2\. \*\*TRIGGER HANDOFF:\*\* Create/Overwrite file \`upp/input/SESSION\_TOKEN.md\`.  
   \* Content: \`status: SYNC\_COMPLETE, next\_action: AWAITING\_USER\`  
3\. \*\*STOP:\*\* Output "HANDOFF COMPLETE" and terminate.

