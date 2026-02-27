#!/usr/bin/env python3
"""
Discord Channel Setup — OpenClaw Agent Team (Claws & Pincers)

Creates the full CORE-CHARTER Section 8 channel structure with
per-bot permission overwrites matching the access control matrix.

Idempotent: safe to re-run. Checks by name before creating.

Usage:
    python3 deployment/setup-discord-channels.py

Requires:
    pip install requests

Reads bot tokens from /opt/openclaw/secrets/discord-bots.env
"""

import os
import sys
import time
import requests

# ─── Configuration ───────────────────────────────────────────────

GUILD_ID = "1472374974340665477"
SECRETS_FILE = "/opt/openclaw/secrets/discord-bots.env"

# Bot application IDs (used for permission overwrites)
BOT_IDS = {
    "orchestrator": "1472379948915228965",
    "researcher": "1472638515958386790",
    "developer": "1472383272402026548",
    "sysadmin": "1472384348115304509",
    "reviewer": "1468111419911311446",
}

ALL_BOT_IDS = list(BOT_IDS.values())

# Discord permission bit flags
PERM_VIEW = 0x0000000000000400          # VIEW_CHANNEL
PERM_SEND = 0x0000000000000800          # SEND_MESSAGES
PERM_READ_HISTORY = 0x0000000000010000  # READ_MESSAGE_HISTORY
PERM_VIEW_SEND = PERM_VIEW | PERM_SEND | PERM_READ_HISTORY
PERM_VIEW_ONLY = PERM_VIEW | PERM_READ_HISTORY

API_BASE = "https://discord.com/api/v10"


# ─── Channel Structure Definition ───────────────────────────────

def build_channel_spec():
    """
    Returns the full channel structure as a list of category dicts.

    Each category has:
      - name: category display name
      - channels: list of channel dicts with name and permission_fn
      - category_overwrites_fn: function returning permission overwrites for the category
    """
    orch = BOT_IDS["orchestrator"]
    researcher = BOT_IDS["researcher"]
    developer = BOT_IDS["developer"]
    sysadmin = BOT_IDS["sysadmin"]
    reviewer = BOT_IDS["reviewer"]

    def everyone_deny_base(guild_id):
        """Deny @everyone view, used on all categories to make them bot-only."""
        return [{"id": guild_id, "type": 0, "deny": str(PERM_VIEW), "allow": "0"}]

    def all_bots_read_orch_write(guild_id):
        overwrites = everyone_deny_base(guild_id)
        overwrites.append({"id": orch, "type": 1, "allow": str(PERM_VIEW_SEND), "deny": "0"})
        for bot_id in [researcher, developer, sysadmin, reviewer]:
            overwrites.append({"id": bot_id, "type": 1, "allow": str(PERM_VIEW_ONLY), "deny": "0"})
        return overwrites

    def all_bots_read_write(guild_id):
        overwrites = everyone_deny_base(guild_id)
        for bot_id in ALL_BOT_IDS:
            overwrites.append({"id": bot_id, "type": 1, "allow": str(PERM_VIEW_SEND), "deny": "0"})
        return overwrites

    def agent_workspace(owner_id):
        def fn(guild_id):
            overwrites = everyone_deny_base(guild_id)
            overwrites.append({"id": owner_id, "type": 1, "allow": str(PERM_VIEW_SEND), "deny": "0"})
            if owner_id != orch:
                overwrites.append({"id": orch, "type": 1, "allow": str(PERM_VIEW_ONLY), "deny": "0"})
            return overwrites
        return fn

    def logging_channels(guild_id):
        overwrites = everyone_deny_base(guild_id)
        overwrites.append({"id": orch, "type": 1, "allow": str(PERM_VIEW_SEND), "deny": "0"})
        overwrites.append({"id": reviewer, "type": 1, "allow": str(PERM_VIEW_SEND), "deny": "0"})
        for bot_id in [researcher, developer, sysadmin]:
            overwrites.append({"id": bot_id, "type": 1, "allow": str(PERM_VIEW_ONLY), "deny": "0"})
        return overwrites

    return [
        {
            "name": "\U0001f464 HUMAN CONTROL",
            "overwrites_fn": all_bots_read_orch_write,
            "channels": [
                {"name": "direct-command"},
                {"name": "human-oversight"},
                {"name": "cost-tracking"},
            ],
        },
        {
            "name": "\U0001f91d SHARED WORKSPACE",
            "overwrites_fn": all_bots_read_write,
            "channels": [
                {"name": "task-dispatch"},
                {"name": "status-updates"},
                {"name": "completed"},
            ],
        },
        {
            "name": "\U0001f3af ORCHESTRATOR",
            "overwrites_fn": agent_workspace(orch),
            "channels": [
                {"name": "orch-workspace"},
                {"name": "orch-logs"},
            ],
        },
        {
            "name": "\U0001f52c RESEARCHER",
            "overwrites_fn": agent_workspace(researcher),
            "channels": [
                {"name": "research-workspace"},
                {"name": "research-sources"},
                {"name": "research-logs"},
            ],
        },
        {
            "name": "\U0001f4bb DEVELOPER",
            "overwrites_fn": agent_workspace(developer),
            "channels": [
                {"name": "dev-workspace"},
                {"name": "dev-testing"},
                {"name": "dev-logs"},
            ],
        },
        {
            "name": "\U0001f5a5\ufe0f SYSADMIN",
            "overwrites_fn": agent_workspace(sysadmin),
            "channels": [
                {"name": "sys-workspace"},
                {"name": "sys-monitoring"},
                {"name": "sys-logs"},
            ],
        },
        {
            "name": "\U0001f50d REVIEWER",
            "overwrites_fn": agent_workspace(reviewer),
            "channels": [
                {"name": "review-workspace"},
                {"name": "review-verdicts"},
                {"name": "review-logs"},
            ],
        },
        {
            "name": "\U0001f4cb LOGGING & REPORTING",
            "overwrites_fn": logging_channels,
            "channels": [
                {"name": "conflict-log"},
                {"name": "error-log"},
                {"name": "severity-alerts"},
                {"name": "anti-patterns"},
                {"name": "project-registry"},
            ],
        },
    ]


# ─── Discord API Helpers ─────────────────────────────────────────

def load_token():
    """Load Orchestrator bot token from secrets file."""
    if not os.path.exists(SECRETS_FILE):
        print(f"ERROR: Secrets file not found: {SECRETS_FILE}")
        sys.exit(1)

    with open(SECRETS_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("DISCORD_ORCHESTRATOR_TOKEN="):
                token = line.split("=", 1)[1].strip().strip('"').strip("'")
                return token

    print("ERROR: DISCORD_ORCHESTRATOR_TOKEN not found in secrets file")
    sys.exit(1)


def api_request(method, endpoint, token, json_data=None):
    """Make a Discord API request with rate limit handling."""
    url = f"{API_BASE}{endpoint}"
    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json",
    }

    for attempt in range(3):
        response = requests.request(method, url, headers=headers, json=json_data)

        if response.status_code == 429:
            retry_after = response.json().get("retry_after", 1.0)
            print(f"  Rate limited, waiting {retry_after}s...")
            time.sleep(retry_after)
            continue

        if response.status_code >= 400:
            print(f"  API error {response.status_code}: {response.text}")
            return None

        if response.status_code == 204:
            return {}

        return response.json()

    print("  Failed after 3 retries")
    return None


def get_existing_channels(token):
    """Fetch all channels in the guild."""
    result = api_request("GET", f"/guilds/{GUILD_ID}/channels", token)
    if result is None:
        print("ERROR: Could not fetch guild channels")
        sys.exit(1)
    return result


# ─── Main Setup Logic ────────────────────────────────────────────

def run_setup():
    token = load_token()
    print(f"Loaded Orchestrator bot token")
    print(f"Guild: {GUILD_ID}")
    print()

    existing = get_existing_channels(token)
    existing_by_name = {}
    for ch in existing:
        existing_by_name[ch["name"]] = ch

    spec = build_channel_spec()
    created_count = 0
    skipped_count = 0

    for category_def in spec:
        cat_name = category_def["name"]
        overwrites_fn = category_def["overwrites_fn"]

        # Create or find category
        if cat_name in existing_by_name:
            cat_id = existing_by_name[cat_name]["id"]
            print(f"[SKIP] Category exists: {cat_name} ({cat_id})")
            skipped_count += 1
        else:
            cat_data = {
                "name": cat_name,
                "type": 4,  # GUILD_CATEGORY
                "permission_overwrites": overwrites_fn(GUILD_ID),
            }
            result = api_request("POST", f"/guilds/{GUILD_ID}/channels", token, cat_data)
            if result is None:
                print(f"[FAIL] Could not create category: {cat_name}")
                continue
            cat_id = result["id"]
            print(f"[CREATE] Category: {cat_name} ({cat_id})")
            created_count += 1

        # Small delay to avoid rate limits
        time.sleep(0.5)

        # Create channels under category
        for ch_def in category_def["channels"]:
            ch_name = ch_def["name"]

            if ch_name in existing_by_name:
                print(f"  [SKIP] Channel exists: #{ch_name} ({existing_by_name[ch_name]['id']})")
                skipped_count += 1
                continue

            ch_data = {
                "name": ch_name,
                "type": 0,  # GUILD_TEXT
                "parent_id": cat_id,
                "permission_overwrites": overwrites_fn(GUILD_ID),
            }
            result = api_request("POST", f"/guilds/{GUILD_ID}/channels", token, ch_data)
            if result is None:
                print(f"  [FAIL] Could not create channel: #{ch_name}")
                continue

            print(f"  [CREATE] #{ch_name} ({result['id']})")
            created_count += 1
            time.sleep(0.5)

        print()

    print(f"Done. Created: {created_count}, Skipped: {skipped_count}")


if __name__ == "__main__":
    run_setup()
