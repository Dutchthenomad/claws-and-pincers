# Telegram 2FA Cleanup Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Remove debug logging from the working Telegram inline button implementation and verify the feature end-to-end.

**Architecture:** The Telegram 2FA feature is complete and working. This plan removes 13 debug console.log statements added during development across 3 files, rebuilds the runtime, and performs live verification.

**Tech Stack:** TypeScript, SSH to VPS (srv1216617 / 72.62.160.2), systemd

---

## Current State (Verified)

| Component | Status | Evidence |
|-----------|--------|----------|
| `sendPayload` in Telegram adapter | ✅ Working | Line 285 in `channel.ts` |
| Callback handler for `approve:*` | ✅ Working | Lines 167, 449 in `bot-handlers.ts` |
| Buttons appearing in Telegram | ✅ Working | Gateway logs show button payloads delivered |
| Button taps resolving approvals | ✅ Working | Logs show "Resolved by Telegram button" |
| Auth directory cleanup | ✅ Already done | `/opt/openclaw/auth/` does not exist |
| Auth services cleanup | ✅ Already done | No `openclaw-auth` or `openclaw-webhook` services |

---

## Task 1: Remove Debug Logs from exec-approval-forwarder.ts

**Files:**
- Modify: `/opt/openclaw/runtime/src/infra/exec-approval-forwarder.ts` (lines 226, 311)

**Step 1: View current debug lines**

Run:
```bash
ssh vps "grep -n 'console.log.*APPROVAL_DEBUG' /opt/openclaw/runtime/src/infra/exec-approval-forwarder.ts"
```

Expected output (2 lines):
```
226:      console.log("[APPROVAL_DEBUG] deliverToTargets payload:", ...
311:    console.log("[APPROVAL_DEBUG] buttons generated:", ...
```

**Step 2: Remove the debug lines**

Run:
```bash
ssh vps "sed -i '/\[APPROVAL_DEBUG\]/d' /opt/openclaw/runtime/src/infra/exec-approval-forwarder.ts"
```

**Step 3: Verify removal**

Run:
```bash
ssh vps "grep -c 'APPROVAL_DEBUG' /opt/openclaw/runtime/src/infra/exec-approval-forwarder.ts"
```

Expected: `0`

---

## Task 2: Remove Debug Logs from deliver.ts

**Files:**
- Modify: `/opt/openclaw/runtime/src/infra/outbound/deliver.ts` (lines 95, 322, 323, 333, 335, 339)

**Step 1: View current debug lines**

Run:
```bash
ssh vps "grep -n 'console.log.*\(HANDLER_DEBUG\|DELIVER_DEBUG\)' /opt/openclaw/runtime/src/infra/outbound/deliver.ts"
```

Expected output (6 lines):
```
95:  console.log("[HANDLER_DEBUG] channel:", ...
322:  console.log("[DELIVER_DEBUG] normalizedPayloads channelData check:", ...
323:  console.log("[DELIVER_DEBUG] handler.sendPayload exists:", ...
333:      console.log("[DELIVER_DEBUG] loop - payload.channelData:", ...
335:        console.log("[DELIVER_DEBUG] calling handler.sendPayload with buttons!");
339:      console.log("[DELIVER_DEBUG] NOT using sendPayload - falling through to sendTextChunks");
```

**Step 2: Remove the debug lines**

Run:
```bash
ssh vps "sed -i '/\[HANDLER_DEBUG\]/d; /\[DELIVER_DEBUG\]/d' /opt/openclaw/runtime/src/infra/outbound/deliver.ts"
```

**Step 3: Verify removal**

Run:
```bash
ssh vps "grep -cE '(HANDLER_DEBUG|DELIVER_DEBUG)' /opt/openclaw/runtime/src/infra/outbound/deliver.ts"
```

Expected: `0`

---

## Task 3: Remove Debug Logs from load.ts

**Files:**
- Modify: `/opt/openclaw/runtime/src/channels/plugins/outbound/load.ts` (lines 45, 51, 53, 59, 61)

**Step 1: View current debug lines**

Run:
```bash
ssh vps "grep -n 'console.log.*LOAD_DEBUG' /opt/openclaw/runtime/src/channels/plugins/outbound/load.ts"
```

Expected output (5 lines):
```
45:    console.log("[LOAD_DEBUG] Using cached outbound for:", ...
51:  console.log("[LOAD_DEBUG] id:", ...
53:    console.log("[LOAD_DEBUG] Using REGISTRY outbound for:", ...
59:  console.log("[LOAD_DEBUG] Static adapter for:", ...
61:    console.log("[LOAD_DEBUG] Using STATIC outbound for:", ...
```

**Step 2: Remove the debug lines**

Run:
```bash
ssh vps "sed -i '/\[LOAD_DEBUG\]/d' /opt/openclaw/runtime/src/channels/plugins/outbound/load.ts"
```

**Step 3: Verify removal**

Run:
```bash
ssh vps "grep -c 'LOAD_DEBUG' /opt/openclaw/runtime/src/channels/plugins/outbound/load.ts"
```

Expected: `0`

---

## Task 4: Rebuild Runtime

**Step 1: Clean and rebuild**

Run:
```bash
ssh vps "cd /opt/openclaw/runtime && rm -rf dist && npm run build"
```

Expected: Build completes without errors, outputs to `dist/` directory.

**Step 2: Verify build succeeded**

Run:
```bash
ssh vps "ls -la /opt/openclaw/runtime/dist/src/infra/exec-approval-forwarder.js | head -1"
```

Expected: File exists with recent timestamp.

---

## Task 5: Restart Gateway

**Step 1: Restart service**

Run:
```bash
ssh vps "systemctl restart openclaw"
```

**Step 2: Verify service is running**

Run:
```bash
ssh vps "systemctl is-active openclaw"
```

Expected: `active`

**Step 3: Check for startup errors**

Run:
```bash
ssh vps "journalctl -u openclaw -n 20 --no-pager"
```

Expected: No errors, gateway started successfully.

---

## Task 6: End-to-End Verification

**Step 1: Trigger an approval request**

Use browser automation to open Telegram and observe in real-time. Then run a command that requires approval (via a sandbox session or directly).

Run:
```bash
ssh vps "cd /opt/openclaw/workspace && /opt/openclaw/runtime/dist/cli.js exec 'rm -rf /tmp/test-approval-cleanup' --ask 'Testing cleanup verification'"
```

**Step 2: Verify in Telegram**

Using browser automation (mcp__claude-in-chrome tools):
1. Open Telegram conversation with OpenClaw bot
2. Observe: Message appears with inline buttons [✅ Allow Once] [✅ Always] [❌ Deny]
3. Tap one of the buttons
4. Observe: Message updates to show resolution status

**Step 3: Verify no debug logs in output**

Run:
```bash
ssh vps "tail -20 /opt/openclaw/data/logs/gateway.log | grep -E '(DEBUG|console)' || echo 'NO_DEBUG_OUTPUT_FOUND'"
```

Expected: `NO_DEBUG_OUTPUT_FOUND`

**Step 4: Commit verification screenshot**

Take a screenshot of the working Telegram UI showing inline buttons and save as evidence.

---

## Verification Checklist

After completing all tasks, confirm:

- [ ] No `APPROVAL_DEBUG` in exec-approval-forwarder.ts
- [ ] No `HANDLER_DEBUG` or `DELIVER_DEBUG` in deliver.ts
- [ ] No `LOAD_DEBUG` in load.ts
- [ ] Runtime builds without errors
- [ ] Gateway restarts successfully
- [ ] Telegram messages show inline buttons
- [ ] Button taps resolve approvals
- [ ] Gateway logs are clean (no debug output)

---

## Rollback

If something breaks:

```bash
# Check git status for uncommitted changes
ssh vps "cd /opt/openclaw/runtime && git status"

# Restore from git if needed
ssh vps "cd /opt/openclaw/runtime && git checkout -- src/"

# Rebuild and restart
ssh vps "cd /opt/openclaw/runtime && npm run build && systemctl restart openclaw"
```
