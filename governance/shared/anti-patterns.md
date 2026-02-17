# ANTI-PATTERNS — Self-Learning Mistake Registry

**Rule:** ALL agents must read this document before starting ANY task.  
**Rule:** Repeat violations auto-escalate one severity level.  
**Maintained by:** Reviewer/QA + Orchestrator

---

## AP-001: Fast But Wrong
- **Detected:** 2026-02-16 (pre-loaded)
- **Project:** SYSTEM
- **Category:** process
- **Description:** Delivering work quickly at the expense of correctness
- **Root Cause:** Prioritizing speed over quality
- **Prevention:** Always verify, always test, always review. If unsure, ask.
- **Severity when violated:** BLOCKED

## AP-002: Working Without Project ID
- **Detected:** 2026-02-16 (pre-loaded)
- **Project:** SYSTEM
- **Category:** process
- **Description:** Performing any work without a registered Project ID
- **Root Cause:** Skipping governance to start faster
- **Prevention:** Verify PROJ-ID exists in PROJECT-REGISTRY.md before starting any task
- **Severity when violated:** CRITICAL

## AP-003: Coding Before Charter Approval
- **Detected:** 2026-02-16 (pre-loaded)
- **Project:** SYSTEM
- **Category:** process
- **Description:** Writing code or making system changes before charter is approved by Devin
- **Root Cause:** Impatience, assumption that charter will be approved as-is
- **Prevention:** Check charter approval status. Research is OK, implementation is not.
- **Severity when violated:** CRITICAL

## AP-004: Ignoring Conflict Detection
- **Detected:** 2026-02-16 (pre-loaded)
- **Project:** SYSTEM
- **Category:** process
- **Description:** Dispatching or starting work without running conflict detection
- **Root Cause:** Oversight or assumption that no conflicts exist
- **Prevention:** Orchestrator must run conflict check before EVERY dispatch
- **Severity when violated:** CRITICAL

## AP-005: Context Window Pollution
- **Detected:** 2026-02-16 (pre-loaded)
- **Project:** SYSTEM
- **Category:** architecture
- **Description:** Dumping large outputs, verbose logs, or unnecessary data into chat context
- **Root Cause:** Not designing output for LLM consumption
- **Prevention:** Log to files, print summaries only, use --fast flags for test runs. Keep Discord messages concise. Write details to project files.
- **Severity when violated:** WARN

## AP-006: Scope Creep Without Charter Amendment
- **Detected:** 2026-02-16 (pre-loaded)
- **Project:** SYSTEM
- **Category:** process
- **Description:** Expanding project scope beyond what the charter defines without getting approval
- **Root Cause:** Good intentions — "while I'm here I'll also fix X"
- **Prevention:** If work isn't in the charter scope-in section, it requires a charter amendment approved by Devin. No exceptions.
- **Severity when violated:** BLOCKED

## AP-007: Untested Deliverables
- **Detected:** 2026-02-16 (pre-loaded)
- **Project:** SYSTEM
- **Category:** code-quality
- **Description:** Submitting code for review without tests or verification
- **Root Cause:** Time pressure, assumption that reviewer will catch issues
- **Prevention:** Untested code is unreviewed code. Developer must verify before submitting.
- **Severity when violated:** BLOCKED
