# OpenClaw Exec Output Fix - Revised Analysis

**Date:** 2026-02-03
**Status:** REVISED - Original diagnosis was PARTIALLY CORRECT

---

## Executive Summary

After deep code analysis, the original Clawbot diagnosis was **partially correct** but identified the wrong root cause:

### What Clawbot Got Right:
- Commands execute but output isn't reaching the agent
- The problem IS in how exec results are handled
- Files created by exec don't persist

### What Clawbot Got Wrong:
- The stdio piping IS correctly implemented in the source code
- The code DOES have `stdio: ['pipe', 'pipe', 'pipe']` (lines 210, 277, 305 in bash-tools.exec.js)
- Output handlers ARE implemented (`child.stdout.on("data", handleStdout)`)

---

## ACTUAL ROOT CAUSE

The agent (Clawbot) runs in a **sandboxed environment**:
- Sandbox path: `/opt/openclaw/sandboxes/agent-main-main-20ceb99b/`
- Files outside this sandbox are rejected with "Path escapes sandbox root"

### Evidence from Logs:
```
[tools] read failed: Path escapes sandbox root (/opt/openclaw/sandboxes/agent-main-main-20ceb99b): /opt/openclaw/runtime/docs
[tools] write failed: Path escapes sandbox root (/opt/openclaw/sandboxes/agent-main-main-20ceb99b): ~/.config/moltbook/credentials.json
```

### The Real Issue:
When exec runs with `host=gateway` and `elevated=true`:
1. Commands DO execute on the host (outside sandbox)
2. Files ARE created on the host filesystem
3. BUT the agent (sandboxed) can't READ those files afterward
4. The agent's working directory is inside the sandbox
5. So `/home/agent-main/` from the agent's perspective maps to the sandbox, not the real host path

---

## Proof

When Clawbot runs `ls /home/agent-main/`:
- The exec command runs on the HOST
- Files get created at the REAL `/home/agent-main/` on the HOST
- But when Clawbot tries to read them, the READ tool is sandboxed
- The sandboxed read tool looks for `/opt/openclaw/sandboxes/agent-main-main-20ceb99b/home/agent-main/`
- That path doesn't exist, hence ENOENT errors

---

## Solution Options

### Option 1: Disable Sandbox for agent-main (Recommended for Development)
Configure the agent to run without sandbox:

```yaml
agents:
  list:
    - id: agent-main
      sandbox:
        enabled: false
```

**Risk:** High - agent has full host access
**Benefit:** Full functionality immediately

### Option 2: Configure Sandbox Mounts
Mount the real `/home/agent-main` into the sandbox:

```yaml
agents:
  defaults:
    sandbox:
      mounts:
        - host: /home/agent-main
          container: /home/agent-main
          mode: rw
```

**Risk:** Medium - controlled access
**Benefit:** Maintains security boundary

### Option 3: Use Gateway-Only for Exec + Read
When exec runs on gateway, subsequent reads should also use gateway.
This requires changes to how the agent handles file access after exec.

---

## Immediate Fix Checklist

1. **Find the agent configuration:**
   ```bash
   grep -r "agent-main" /opt/openclaw/
   ```

2. **Check current sandbox settings:**
   ```bash
   grep -r "sandbox" /opt/openclaw/config/ /opt/openclaw/data/
   ```

3. **Apply fix (Option 1 - disable sandbox):**
   Edit the agent config to add:
   ```yaml
   sandbox:
     mode: "off"
   ```
   Or set environment variable:
   ```bash
   OPENCLAW_SANDBOX_MODE=off
   ```

4. **Restart gateway:**
   ```bash
   systemctl restart openclaw-gateway
   # Or if running via pnpm:
   # Kill and restart the gateway process
   ```

5. **Test:**
   ```bash
   # Via Clawbot/agent:
   echo "test" > /tmp/test-output.txt && cat /tmp/test-output.txt
   ```

---

## Why Output Shows "(no output recorded)"

The output capture IS working, but:
1. Elevated exec commands run async with approval workflow
2. After approval, command runs in background
3. System event notifies agent: "Exec finished (gateway id=..., code 0)"
4. But agent can't then read files created because of sandbox isolation

For simple commands like `echo "test"`:
- Output SHOULD appear directly in the result
- If it's still missing, check if the approval workflow is interfering

---

## Files to Examine

1. `/opt/openclaw/config/` - Check for agent sandbox settings
2. `/opt/openclaw/data/gateway/` - Runtime configuration
3. Gateway logs at `/opt/openclaw/data/logs/gateway.log`

---

## Summary

| Item | Original Diagnosis | Actual Issue |
|------|-------------------|--------------|
| Root Cause | Missing stdio piping | Sandbox isolation |
| Fix Location | bash-tools.exec.js | Agent configuration |
| Fix Effort | Code changes | Config change |
| Risk | Medium | Low |

The original analysis identified symptoms correctly but attributed them to the wrong cause. The exec subsystem is working; the problem is the agent's sandboxed environment preventing access to host-created files.

---

**Action Required:** Configure sandbox settings for the agent, not code changes to the exec implementation.
