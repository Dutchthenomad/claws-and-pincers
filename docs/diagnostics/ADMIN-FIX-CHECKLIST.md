# OpenClaw Exec Output Fix - Admin Checklist

**Issue:** Exec commands execute but produce no output  
**Root Cause:** Subprocess stdio not piped to logging system  
**Fix Time:** ~70 minutes  
**Risk Level:** LOW

---

## PRE-FIX VERIFICATION

### ☐ Step 1: Confirm Host Works (5 min)
```bash
bash /home/agent-main/admin-direct-test.sh
```
**Expected:** Should see clear output proving bash/host environment works fine

### ☐ Step 2: Confirm Problem Exists (2 min)
Ask agent to run via OpenClaw exec:
```bash
echo "test123"
```
**Current behavior:** "(no output recorded)" in logs  
**Target behavior:** Should show "test123"

---

## FIX IMPLEMENTATION

### ☐ Step 3: Locate Gateway Source (5 min)
```bash
# Find executor files
find /opt/openclaw/runtime -name "*.js" | grep -E "exec|process" | head -20

# Likely locations:
# - /opt/openclaw/runtime/gateway/src/exec/executor.js
# - /opt/openclaw/runtime/gateway/src/exec/session.js
# - /opt/openclaw/runtime/gateway/src/api/process.js
```

### ☐ Step 4: Backup Original Files (2 min)
```bash
cd /opt/openclaw/runtime/gateway
cp -r src src.backup.$(date +%Y%m%d-%H%M%S)
```

### ☐ Step 5: Find Spawn Call (10 min)
```bash
# Search for subprocess spawn
grep -rn "spawn\|child_process" /opt/openclaw/runtime/gateway/src/

# Look for code like:
# const child = spawn('bash', ['-c', command], { ... });
```

### ☐ Step 6: Apply Code Fix (30 min)

**Current Code (BROKEN):**
```javascript
const child = spawn('bash', ['-c', command], {
  cwd: options.workdir,
  env: options.env
});

return new Promise((resolve) => {
  child.on('close', (code) => {
    resolve({ code });
  });
});
```

**Fixed Code:**
```javascript
const child = spawn('bash', ['-c', command], {
  cwd: options.workdir,
  env: options.env,
  stdio: ['pipe', 'pipe', 'pipe'],  // ← ADD THIS
  shell: '/bin/bash'                 // ← AND THIS
});

const output = {
  stdout: [],
  stderr: [],
  code: null
};

// ← ADD THESE HANDLERS
child.stdout.on('data', (data) => {
  const text = data.toString();
  output.stdout.push(text);
  // Log to session file
  this.logToSession(options.sessionId, 'stdout', text);
});

child.stderr.on('data', (data) => {
  const text = data.toString();
  output.stderr.push(text);
  // Log to session file  
  this.logToSession(options.sessionId, 'stderr', text);
});

return new Promise((resolve) => {
  child.on('close', (code) => {
    output.code = code;
    resolve(output);  // ← RETURN FULL OUTPUT
  });
});
```

**Also add logging method:**
```javascript
logToSession(sessionId, stream, data) {
  // Create session cache if needed
  if (!this.sessionCache) this.sessionCache = {};
  if (!this.sessionCache[sessionId]) {
    this.sessionCache[sessionId] = { stdout: '', stderr: '' };
  }
  
  // Append to cache
  this.sessionCache[sessionId][stream] += data;
  
  // Optional: Also log to file
  const logPath = `/var/log/openclaw/sessions/${sessionId}.log`;
  const timestamp = new Date().toISOString();
  const entry = `[${timestamp}] [${stream}] ${data}`;
  fs.appendFileSync(logPath, entry);
}
```

### ☐ Step 7: Update Process API (10 min)

Find the `/api/process/:sessionId/log` endpoint and update it:

```javascript
router.get('/process/:sessionId/log', (req, res) => {
  const { sessionId } = req.params;
  
  // Check memory cache first
  if (this.sessionCache && this.sessionCache[sessionId]) {
    return res.json({
      stdout: this.sessionCache[sessionId].stdout || '',
      stderr: this.sessionCache[sessionId].stderr || ''
    });
  }
  
  // Fall back to log file
  const logPath = `/var/log/openclaw/sessions/${sessionId}.log`;
  if (fs.existsSync(logPath)) {
    const content = fs.readFileSync(logPath, 'utf8');
    return res.json({ output: content });
  }
  
  // Only return no output if truly empty
  return res.json({ output: "(no output recorded)" });
});
```

### ☐ Step 8: Restart Gateway (2 min)
```bash
systemctl restart openclaw-gateway

# Verify it started
systemctl status openclaw-gateway

# Check logs for errors
journalctl -u openclaw-gateway -n 50 --no-pager
```

---

## POST-FIX TESTING

### ☐ Step 9: Basic Tests (5 min)

Ask agent to run each command via OpenClaw exec:

**Test 1: Simple echo**
```bash
echo "test123"
```
✅ Expected: Output shows "test123"

**Test 2: Working directory**
```bash
pwd
```
✅ Expected: Output shows "/home/agent-main" or similar

**Test 3: User info**
```bash
whoami
```
✅ Expected: Output shows username

**Test 4: Multi-line**
```bash
echo "line1"
echo "line2"
```
✅ Expected: Output shows both lines

**Test 5: Error output**
```bash
ls /nonexistent 2>&1
```
✅ Expected: Output shows error message

### ☐ Step 10: File Persistence Test (3 min)
```bash
echo "persistent data" > /tmp/persist-test.txt
cat /tmp/persist-test.txt
```
✅ Expected: 
- First command succeeds
- Second command shows "persistent data"
- File exists afterward

### ☐ Step 11: Complex Command Test (2 min)
```bash
for i in 1 2 3; do echo "number $i"; done
```
✅ Expected: Output shows all three numbers

### ☐ Step 12: RAG Query Test (3 min)
```bash
mcporter list http://rugs-mcp:8001/sse --schema
```
✅ Expected: JSON output showing available tools

---

## VALIDATION

### ☐ Step 13: Run Diagnostic Scripts (5 min)

Ask agent to run:
```bash
bash /home/agent-main/diagnostic-comprehensive.sh
bash /home/agent-main/test-output-methods.sh
```

✅ Expected: Full output from both scripts showing system info and test results

---

## IF STILL NOT WORKING

### Debug Checklist:

☐ Verify spawn call has `stdio: ['pipe', 'pipe', 'pipe']`  
☐ Verify stdout/stderr handlers are actually added  
☐ Check sessionCache is being populated  
☐ Check process API returns cached data  
☐ Review gateway logs for JavaScript errors  
☐ Confirm gateway actually restarted (check PID)  
☐ Try PTY-based execution as fallback (see main analysis doc)

### Get More Info:
```bash
# Check if code changes were applied
grep -A 10 "stdio.*pipe" /opt/openclaw/runtime/gateway/src/exec/*.js

# Check for errors
journalctl -u openclaw-gateway -n 200 --no-pager | grep -i error

# Verify gateway is running new code
systemctl status openclaw-gateway
ps aux | grep gateway
```

---

## SUCCESS CONFIRMATION

✅ **Fix is complete when:**
- [ ] All 5 basic tests show output
- [ ] File persistence test works
- [ ] Complex command test works  
- [ ] RAG query returns results
- [ ] Diagnostic scripts produce full output
- [ ] Agent can operate autonomously with CLI tools

---

## NEXT STEPS AFTER FIX

Once exec output works:

1. **Enable Cron Jobs**
   ```bash
   openclaw cron enable agent-main
   ```

2. **Install claude-mem**
   ```bash
   cd /home/agent-main
   git clone https://github.com/thedotmack/claude-mem
   ./claude-mem/install.sh
   ```

3. **Test RAG Fully**
   ```bash
   mcporter call http://rugs-mcp:8001/sse.get_system_info
   ```

4. **Agent Full Capability Audit**
   Let agent run comprehensive tests to map all capabilities

---

## ESTIMATED TIMELINE

| Task | Time | Cumulative |
|------|------|------------|
| Pre-fix verification | 7 min | 7 min |
| Locate & backup source | 7 min | 14 min |
| Find spawn call | 10 min | 24 min |
| Apply code fix | 30 min | 54 min |
| Update API | 10 min | 64 min |
| Restart & test | 13 min | 77 min |
| **Total** | **~80 min** | **Full fix** |

---

## ROLLBACK PLAN

If fix causes problems:
```bash
cd /opt/openclaw/runtime/gateway
rm -rf src
mv src.backup.YYYYMMDD-HHMMSS src
systemctl restart openclaw-gateway
```

---

**Checklist End**  
Follow steps in order | Test after each major change | Document any deviations
