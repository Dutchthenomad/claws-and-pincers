# Phase 0: Foundation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Complete Phase 0 of the 30-day OpenClaw experiment - establishing 2FA, multi-model LLM support, and cost tracking infrastructure.

**Architecture:** WebAuthn-based fingerprint authentication via Telegram WebApp hosted on VPS (Tailscale-only access). Multi-model LLM routing through OpenClaw config with OpenAI/Google/Anthropic APIs. Cost tracking via YAML registry and TimescaleDB.

**Tech Stack:** Node.js, WebAuthn API, Nginx, Telegram Bot API, OpenClaw Gateway, TimescaleDB, YAML configuration.

---

## Prerequisites

- VPS accessible via `ssh vps`
- OpenClaw gateway running (`systemctl status openclaw`)
- Telegram bot active (@dutch_claws_bot)
- Tailscale VPN configured (100.113.138.27)

## Current State

| Item | Status |
|------|--------|
| Anthropic API Key | ✅ Configured |
| Google/Gemini API Key | ✅ Configured |
| OpenAI API Key | ❌ Pending (user needs account) |
| 2FA System | ❌ Not implemented |
| Cost Registry | ❌ Not created |
| Cost Tracking DB | ❌ Not configured |

---

## Task 1: OpenAI API Key Configuration

**Files:**
- Create: `/opt/openclaw/secrets/openai-api.env` (on VPS)
- Modify: `/root/.openclaw/openclaw.json` (on VPS)

**Step 1: User creates OpenAI account and API key**

Manual step - user must:
1. Go to https://platform.openai.com
2. Create account or sign in
3. Navigate to API Keys section
4. Generate new API key
5. Copy the key (starts with `sk-`)

**Step 2: Store API key on VPS**

Run:
```bash
ssh vps "cat > /opt/openclaw/secrets/openai-api.env << 'EOF'
OPENAI_API_KEY=sk-YOUR_KEY_HERE
EOF
chmod 600 /opt/openclaw/secrets/openai-api.env"
```

Expected: File created with 600 permissions

**Step 3: Verify key stored**

Run:
```bash
ssh vps "ls -la /opt/openclaw/secrets/openai-api.env && head -c 20 /opt/openclaw/secrets/openai-api.env"
```

Expected: File exists, starts with `OPENAI_API_KEY=sk-`

**Step 4: Commit documentation update**

```bash
# Update TODO.md to mark OpenAI as configured
git add TODO.md
git commit -m "docs: mark OpenAI API key as configured"
```

---

## Task 2: Cost Registry Configuration

**Files:**
- Create: `/opt/openclaw/config/cost-registry.yaml` (on VPS)

**Step 1: Create cost registry YAML**

Run:
```bash
ssh vps "cat > /opt/openclaw/config/cost-registry.yaml << 'EOF'
# OpenClaw Cost Registry
# Tracks all paid services for budget management
# Updated: 2026-02-01

paid_services:
  llm_apis:
    anthropic:
      type: per-token
      models:
        - claude-opus-4-5
        - claude-sonnet-4-5
        - claude-haiku-3-5
      billing: monthly
      dashboard: https://console.anthropic.com
      secret_ref: /opt/openclaw/secrets/anthropic-api.env
      budget_alert_usd: 100
      status: active

    openai:
      type: per-token
      models:
        - gpt-4o
        - gpt-4o-mini
        - gpt-4-turbo
      billing: monthly
      dashboard: https://platform.openai.com
      secret_ref: /opt/openclaw/secrets/openai-api.env
      budget_alert_usd: 50
      status: pending  # Update to 'active' when key added

    google:
      type: per-token
      models:
        - gemini-1.5-pro
        - gemini-1.5-flash
      billing: monthly
      dashboard: https://console.cloud.google.com
      secret_ref: /opt/openclaw/secrets/google-ai.env
      budget_alert_usd: 50
      status: active

  compute:
    runpod:
      type: per-second
      purpose: Ablated models (dolphin, deepseek)
      billing: prepaid_credits
      dashboard: https://runpod.io/console
      secret_ref: /opt/openclaw/secrets/runpod.env
      budget_alert_usd: 30
      scaling: zero-when-idle
      status: pending

  infrastructure:
    hostinger_vps:
      type: fixed_monthly
      cost_usd: 15
      purpose: OpenClaw host, Docker, RAG
      billing: monthly
      status: active

    tailscale:
      type: free_tier
      cost_usd: 0
      purpose: VPN access
      status: active

  financial:
    privacy_com:
      type: free_tier
      cost_usd: 0
      purpose: Virtual cards for purchases
      status: deferred

    base_network_gas:
      type: per_transaction
      estimated_monthly_usd: 1
      purpose: USDC transactions
      status: wallet_unfunded

budget_totals:
  monthly_estimate_usd: 250
  alert_threshold_percent: 80

tracking:
  database: timescaledb
  table: openclaw.cost_events
  retention_days: 90
EOF"
```

Expected: File created at `/opt/openclaw/config/cost-registry.yaml`

**Step 2: Verify cost registry**

Run:
```bash
ssh vps "cat /opt/openclaw/config/cost-registry.yaml | head -30"
```

Expected: YAML content displayed correctly

**Step 3: Commit**

```bash
git add -A
git commit -m "feat: add cost registry configuration"
```

---

## Task 3: TimescaleDB Cost Tracking Table

**Files:**
- Execute SQL on TimescaleDB (via VPS)

**Step 1: Check TimescaleDB is running**

Run:
```bash
ssh vps "docker ps | grep timescale"
```

Expected: Container running

**Step 2: Create cost_events table**

Run:
```bash
ssh vps "docker exec -i timescaledb psql -U postgres -d openclaw << 'EOF'
-- Cost tracking table for OpenClaw
CREATE TABLE IF NOT EXISTS cost_events (
    id SERIAL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    service VARCHAR(50) NOT NULL,
    model VARCHAR(100),
    tokens_in INTEGER,
    tokens_out INTEGER,
    cost_usd DECIMAL(10, 6),
    session_id VARCHAR(100),
    purpose_tag VARCHAR(100),
    metadata JSONB,
    PRIMARY KEY (id, timestamp)
);

-- Convert to hypertable for time-series optimization
SELECT create_hypertable('cost_events', 'timestamp', if_not_exists => TRUE);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_cost_events_service ON cost_events (service, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_cost_events_session ON cost_events (session_id, timestamp DESC);

-- Create daily rollup view
CREATE MATERIALIZED VIEW IF NOT EXISTS cost_daily_rollup AS
SELECT
    time_bucket('1 day', timestamp) AS day,
    service,
    model,
    SUM(tokens_in) AS total_tokens_in,
    SUM(tokens_out) AS total_tokens_out,
    SUM(cost_usd) AS total_cost_usd,
    COUNT(*) AS request_count
FROM cost_events
GROUP BY day, service, model
ORDER BY day DESC;

-- Grant permissions
GRANT ALL ON cost_events TO postgres;
GRANT ALL ON cost_daily_rollup TO postgres;

\\echo 'Cost tracking tables created successfully'
EOF"
```

Expected: Tables and indexes created, "Cost tracking tables created successfully"

**Step 3: Verify table exists**

Run:
```bash
ssh vps "docker exec -i timescaledb psql -U postgres -d openclaw -c '\\dt cost_*'"
```

Expected: `cost_events` table listed

**Step 4: Insert test record**

Run:
```bash
ssh vps "docker exec -i timescaledb psql -U postgres -d openclaw << 'EOF'
INSERT INTO cost_events (service, model, tokens_in, tokens_out, cost_usd, purpose_tag)
VALUES ('anthropic', 'claude-sonnet-4-5', 100, 500, 0.003, 'test_record');

SELECT * FROM cost_events ORDER BY timestamp DESC LIMIT 1;
EOF"
```

Expected: Test record inserted and displayed

**Step 5: Commit documentation**

```bash
git add -A
git commit -m "feat: configure TimescaleDB cost tracking tables"
```

---

## Task 4: WebAuthn 2FA Page Setup

**Files:**
- Create: `/opt/openclaw/web/auth/index.html` (on VPS)
- Create: `/opt/openclaw/web/auth/auth.js` (on VPS)
- Create: `/opt/openclaw/web/auth/style.css` (on VPS)

**Step 1: Create web directory structure**

Run:
```bash
ssh vps "mkdir -p /opt/openclaw/web/auth"
```

Expected: Directory created

**Step 2: Create WebAuthn HTML page**

Run:
```bash
ssh vps "cat > /opt/openclaw/web/auth/index.html << 'EOF'
<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>OpenClaw 2FA</title>
    <link rel=\"stylesheet\" href=\"style.css\">
</head>
<body>
    <div class=\"container\">
        <div class=\"card\">
            <div class=\"logo\">🦞</div>
            <h1>OpenClaw Authentication</h1>

            <div id=\"request-info\" class=\"request-info\">
                <p><strong>Action:</strong> <span id=\"action-type\">Loading...</span></p>
                <p><strong>Details:</strong> <span id=\"action-details\">Loading...</span></p>
                <p><strong>Tier:</strong> <span id=\"action-tier\">Loading...</span></p>
            </div>

            <div id=\"auth-section\">
                <button id=\"auth-btn\" class=\"auth-button\" onclick=\"authenticate()\">
                    🔓 Authenticate with Fingerprint
                </button>
                <p class=\"hint\">Touch your fingerprint sensor to approve</p>
            </div>

            <div id=\"status\" class=\"status\"></div>

            <div class=\"fallback\">
                <p>Can't use biometrics?</p>
                <button onclick=\"showPinInput()\" class=\"link-btn\">Use PIN instead</button>
            </div>

            <div id=\"pin-section\" class=\"hidden\">
                <input type=\"password\" id=\"pin-input\" placeholder=\"Enter 6-digit PIN\" maxlength=\"6\" pattern=\"[0-9]*\">
                <button onclick=\"verifyPin()\" class=\"pin-button\">Verify PIN</button>
            </div>
        </div>
    </div>
    <script src=\"auth.js\"></script>
</body>
</html>
EOF"
```

Expected: HTML file created

**Step 3: Create WebAuthn JavaScript**

Run:
```bash
ssh vps "cat > /opt/openclaw/web/auth/auth.js << 'EOF'
// OpenClaw WebAuthn Authentication
const params = new URLSearchParams(window.location.search);
const token = params.get('token');
const action = params.get('action') || 'Unknown action';
const details = params.get('details') || '';
const tier = params.get('tier') || '2';
const callbackUrl = params.get('callback') || 'http://127.0.0.1:18789/auth/callback';

// Display request info
document.getElementById('action-type').textContent = action;
document.getElementById('action-details').textContent = details;
document.getElementById('action-tier').textContent = 'Tier ' + tier;

function setStatus(message, isError = false) {
    const status = document.getElementById('status');
    status.textContent = message;
    status.className = 'status ' + (isError ? 'error' : 'success');
}

async function authenticate() {
    if (!window.PublicKeyCredential) {
        setStatus('WebAuthn not supported. Use PIN instead.', true);
        showPinInput();
        return;
    }

    try {
        setStatus('Requesting biometric authentication...');

        // Check if platform authenticator is available
        const available = await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
        if (!available) {
            setStatus('No biometric authenticator found. Use PIN instead.', true);
            showPinInput();
            return;
        }

        // Create credential for verification
        const challenge = new Uint8Array(32);
        crypto.getRandomValues(challenge);

        const credential = await navigator.credentials.get({
            publicKey: {
                challenge: challenge,
                timeout: 60000,
                userVerification: 'required',
                rpId: window.location.hostname,
            }
        });

        if (credential) {
            setStatus('Authentication successful! Approving action...');
            await sendApproval('biometric');
        }
    } catch (error) {
        if (error.name === 'NotAllowedError') {
            setStatus('Authentication cancelled or timed out.', true);
        } else {
            setStatus('Authentication failed: ' + error.message, true);
            console.error(error);
        }
    }
}

function showPinInput() {
    document.getElementById('pin-section').classList.remove('hidden');
    document.getElementById('pin-input').focus();
}

async function verifyPin() {
    const pin = document.getElementById('pin-input').value;
    if (pin.length !== 6 || !/^\\d+$/.test(pin)) {
        setStatus('PIN must be 6 digits', true);
        return;
    }

    setStatus('Verifying PIN...');
    await sendApproval('pin', pin);
}

async function sendApproval(method, pin = null) {
    try {
        const response = await fetch(callbackUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                token: token,
                method: method,
                pin: pin,
                timestamp: new Date().toISOString(),
                userAgent: navigator.userAgent
            })
        });

        const result = await response.json();

        if (result.success) {
            setStatus('✅ Action approved! You can close this window.');
            document.getElementById('auth-section').innerHTML = '<p class=\"approved\">✅ Approved</p>';
        } else {
            setStatus('❌ ' + (result.error || 'Approval failed'), true);
        }
    } catch (error) {
        setStatus('❌ Could not reach server: ' + error.message, true);
    }
}

// Handle Enter key in PIN input
document.getElementById('pin-input')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') verifyPin();
});
EOF"
```

Expected: JavaScript file created

**Step 4: Create CSS styles**

Run:
```bash
ssh vps "cat > /opt/openclaw/web/auth/style.css << 'EOF'
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
}

.container {
    width: 100%;
    max-width: 400px;
}

.card {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 16px;
    padding: 32px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    text-align: center;
}

.logo {
    font-size: 48px;
    margin-bottom: 16px;
}

h1 {
    color: #1a1a2e;
    font-size: 24px;
    margin-bottom: 24px;
}

.request-info {
    background: #f5f5f5;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 24px;
    text-align: left;
}

.request-info p {
    margin: 8px 0;
    color: #333;
}

.auth-button {
    background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
    color: white;
    border: none;
    padding: 16px 32px;
    font-size: 18px;
    border-radius: 8px;
    cursor: pointer;
    width: 100%;
    transition: transform 0.2s, box-shadow 0.2s;
}

.auth-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(231, 76, 60, 0.4);
}

.auth-button:active {
    transform: translateY(0);
}

.hint {
    color: #666;
    font-size: 14px;
    margin-top: 12px;
}

.status {
    margin-top: 20px;
    padding: 12px;
    border-radius: 8px;
    font-weight: 500;
}

.status.success {
    background: #d4edda;
    color: #155724;
}

.status.error {
    background: #f8d7da;
    color: #721c24;
}

.fallback {
    margin-top: 24px;
    padding-top: 24px;
    border-top: 1px solid #eee;
}

.fallback p {
    color: #666;
    font-size: 14px;
    margin-bottom: 8px;
}

.link-btn {
    background: none;
    border: none;
    color: #e74c3c;
    cursor: pointer;
    font-size: 14px;
    text-decoration: underline;
}

.hidden {
    display: none;
}

#pin-section {
    margin-top: 16px;
}

#pin-input {
    width: 100%;
    padding: 12px;
    font-size: 24px;
    text-align: center;
    letter-spacing: 8px;
    border: 2px solid #ddd;
    border-radius: 8px;
    margin-bottom: 12px;
}

.pin-button {
    background: #3498db;
    color: white;
    border: none;
    padding: 12px 24px;
    font-size: 16px;
    border-radius: 8px;
    cursor: pointer;
    width: 100%;
}

.approved {
    font-size: 24px;
    color: #27ae60;
    padding: 20px;
}
EOF"
```

Expected: CSS file created

**Step 5: Verify files created**

Run:
```bash
ssh vps "ls -la /opt/openclaw/web/auth/"
```

Expected: index.html, auth.js, style.css all present

**Step 6: Commit**

```bash
git add -A
git commit -m "feat: add WebAuthn 2FA authentication page"
```

---

## Task 5: Nginx Configuration for 2FA Page

**Files:**
- Create: `/etc/nginx/sites-available/openclaw-auth` (on VPS)

**Step 1: Check if Nginx is installed**

Run:
```bash
ssh vps "which nginx || apt install -y nginx"
```

Expected: Nginx path or installation success

**Step 2: Create Nginx site config**

Run:
```bash
ssh vps "cat > /etc/nginx/sites-available/openclaw-auth << 'EOF'
# OpenClaw 2FA Authentication Page
# Tailscale-only access (100.113.138.27)

server {
    listen 8443 ssl;
    server_name 100.113.138.27 srv1216617;

    # Self-signed cert for local/Tailscale use
    ssl_certificate /etc/nginx/ssl/openclaw.crt;
    ssl_certificate_key /etc/nginx/ssl/openclaw.key;

    # Only allow Tailscale network
    allow 100.64.0.0/10;
    deny all;

    root /opt/openclaw/web;
    index index.html;

    location /auth/ {
        alias /opt/openclaw/web/auth/;
        try_files \$uri \$uri/ =404;
    }

    # Proxy auth callbacks to gateway
    location /auth/callback {
        proxy_pass http://127.0.0.1:18789/auth/callback;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF"
```

Expected: Config file created

**Step 3: Generate self-signed SSL cert**

Run:
```bash
ssh vps "mkdir -p /etc/nginx/ssl && openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/nginx/ssl/openclaw.key -out /etc/nginx/ssl/openclaw.crt -subj '/CN=openclaw-auth/O=OpenClaw/C=US'"
```

Expected: Certificate and key generated

**Step 4: Enable site and test config**

Run:
```bash
ssh vps "ln -sf /etc/nginx/sites-available/openclaw-auth /etc/nginx/sites-enabled/ && nginx -t"
```

Expected: "syntax is ok", "test is successful"

**Step 5: Reload Nginx**

Run:
```bash
ssh vps "systemctl reload nginx && systemctl status nginx --no-pager | head -5"
```

Expected: Nginx active and running

**Step 6: Test 2FA page accessible**

Run (from local machine with Tailscale):
```bash
curl -k https://100.113.138.27:8443/auth/
```

Expected: HTML content of auth page

**Step 7: Commit**

```bash
git add -A
git commit -m "feat: configure Nginx for 2FA page (Tailscale-only)"
```

---

## Task 6: Update OpenClaw Config for Multi-Model Support

**Files:**
- Modify: `/root/.openclaw/openclaw.json` (on VPS)

**Step 1: Backup current config**

Run:
```bash
ssh vps "cp /root/.openclaw/openclaw.json /root/.openclaw/openclaw.json.bak"
```

Expected: Backup created

**Step 2: Add multi-model configuration**

Run:
```bash
ssh vps "cat /root/.openclaw/openclaw.json" > /tmp/openclaw-config.json
```

Then edit locally to add OpenAI and Google models to the config.

**Step 3: Update env vars in config**

The config needs to include references to the new API keys. This will be done through the OpenClaw configure command:

Run:
```bash
ssh vps "cd /opt/openclaw/runtime && pnpm openclaw configure"
```

Follow interactive prompts to add:
- OpenAI API key
- Google AI API key

**Step 4: Restart gateway**

Run:
```bash
ssh vps "systemctl restart openclaw && sleep 3 && systemctl status openclaw --no-pager | head -10"
```

Expected: Gateway active and running

**Step 5: Commit documentation**

```bash
git add -A
git commit -m "docs: update Phase 0 completion status"
```

---

## Task 7: Test Complete 2FA Flow

**Step 1: Send test approval request via Telegram**

From Telegram, send a message that would trigger Tier 2 approval.

**Step 2: Verify auth page accessible**

Open in browser: `https://100.113.138.27:8443/auth/?token=test&action=Test&details=Testing%202FA&tier=2`

**Step 3: Test fingerprint authentication**

Click "Authenticate with Fingerprint" and use Samsung fingerprint.

**Step 4: Test PIN fallback**

Click "Use PIN instead" and enter PIN: 410416

**Step 5: Verify approval logged**

Run:
```bash
ssh vps "docker exec -i timescaledb psql -U postgres -d openclaw -c 'SELECT * FROM cost_events ORDER BY timestamp DESC LIMIT 5;'"
```

**Step 6: Document test results**

Update TODO.md with test completion status.

---

## Verification Checklist

Run after all tasks complete:

```bash
# Check all secrets exist
ssh vps "ls -la /opt/openclaw/secrets/"

# Check cost registry
ssh vps "cat /opt/openclaw/config/cost-registry.yaml | head -20"

# Check TimescaleDB tables
ssh vps "docker exec -i timescaledb psql -U postgres -d openclaw -c '\\dt'"

# Check 2FA page
curl -k https://100.113.138.27:8443/auth/ | head -5

# Check gateway status
ssh vps "systemctl status openclaw --no-pager"

# Check Nginx status
ssh vps "systemctl status nginx --no-pager"
```

---

## Phase 0 Completion Criteria

- [ ] OpenAI API key stored and configured
- [ ] Google AI API key stored and configured (✅ DONE)
- [ ] Cost registry YAML created
- [ ] TimescaleDB cost_events table created
- [ ] WebAuthn 2FA page deployed
- [ ] Nginx serving 2FA page on Tailscale
- [ ] Gateway restarted with multi-model config
- [ ] 2FA flow tested end-to-end (3+ successful authentications)

---

*Plan created: 2026-02-01 | Estimated time: 2-3 hours*
