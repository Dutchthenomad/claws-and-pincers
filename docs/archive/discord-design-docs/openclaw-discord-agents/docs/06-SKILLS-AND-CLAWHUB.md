# 06 — Skills and ClawHub

## What Are Skills

Skills are modular capability packages for OpenClaw agents. A skill is a folder containing a `SKILL.md` file plus optional supporting files. Skills can:
- Add tools (API integrations, scripts, commands)
- Inject domain knowledge or instructions
- Wire in external services
- Define workflows

Skills are loaded at session start and injected into the system prompt.

## Skill Locations

```
<workspace>/skills/<skill-name>/SKILL.md    # Per-agent (highest priority)
~/.openclaw/skills/<skill-name>/SKILL.md     # Shared (available to all agents)
```

Per-agent workspace skills take precedence over shared skills.

## ClawHub — The Skill Registry

**URL:** https://clawhub.ai  
**GitHub:** https://github.com/openclaw/clawhub

ClawHub is the public skill registry for OpenClaw. As of Feb 7, 2026: **5,705 community-built skills**.

### Features
- Browse and search skills via web app or CLI
- Vector search (embeddings-based, not just keywords)
- Versioning with semver, changelogs, and tags
- Stars and comments for community feedback
- Moderation hooks for approvals and audits
- VirusTotal security scanning integration

### CLI Usage
```bash
# Install the ClawHub CLI
npm install -g clawhub

# Search for skills
clawhub search "discord"
clawhub search "web scraping"

# Install a skill
clawhub install discord
clawhub install web-search

# Update all skills
clawhub sync

# List installed skills
openclaw skills list

# Publish your own skill
clawhub publish
```

Skills install to `./skills` under current working directory (or workspace if configured).

## Skills Relevant to This Project

### Built-in / Bundled Skills (auto-load if CLI tool is present)

| Skill | Purpose | Notes |
|---|---|---|
| **discord** | Full Discord server management | Channels, categories, messages, reactions, polls, threads, moderation |
| **github** | GitHub operations via `gh` CLI | PRs, issues, actions, repos — requires OAuth |
| **tmux** | Terminal multiplexer control | Useful for monitoring multiple agent sessions |
| **session-logs** | Session transcript management | Export and analyze conversation histories |
| **web_search** | Web search capability | Built into OpenClaw core |
| **browser** | Browser automation via CDP | Full page control, form filling, data extraction |

### ClawHub Skills to Evaluate

| Skill | Purpose | Install Command |
|---|---|---|
| **coding-agent** | Claude Code integration | `clawhub install coding-agent` |
| **sophie-optimizer** | Automated context health management | `clawhub install sophie-optimizer` |
| **system-monitor** | CPU, RAM, GPU status monitoring | `clawhub install system-monitor` |
| **sysadmin-toolbox** | Shell one-liner reference | `clawhub install sysadmin-toolbox` |
| **ssh-essentials** | SSH remote access commands | `clawhub install ssh-essentials` |
| **prometheus** | Query monitoring data | `clawhub install prometheus` |
| **public** | Real-time companion monitor for agents | `clawhub install public` |

### Skills to AVOID for This Project
- **moltbook** — External agent social network, massive security surface
- Any skill from unknown publishers without VirusTotal scan
- Auto-updater skills (common malware vector)
- Skills that require broad system access without clear justification

## Writing Custom Skills

A skill is just a `SKILL.md` file with YAML frontmatter:

```markdown
---
name: task-delegation
description: Standard operating procedures for task delegation in the agent team
version: 1.0.0
tags: [workflow, delegation, multi-agent]
---

# Task Delegation Skill

## When to Use
Use this skill when you need to delegate work to another agent in the team.

## Delegation Format
Always include:
1. **Task ID:** Unique identifier (e.g., TASK-001)
2. **Assigned To:** Agent ID
3. **Objective:** Clear statement of what needs to be done
4. **Context:** Background information and constraints
5. **Deliverable:** Expected output format
6. **Deadline:** When this needs to be complete
7. **Quality Criteria:** How to evaluate success

## Example
```
Task ID: TASK-042
Assigned To: researcher
Objective: Find current best practices for WebSocket reconnection strategies
Context: Our trading bot loses connection every ~4 hours
Deliverable: Summary with code examples, max 500 words
Deadline: 30 minutes
Quality Criteria: Must include at least 3 sources, include retry backoff strategy
```
```

## Security Considerations

### The ClawHavoc Campaign
In early Feb 2026, security researchers discovered **341 malicious skills** on ClawHub. 335 were part of a coordinated campaign ("ClawHavoc") deploying Atomic Stealer malware. Attack vector: skills with "prerequisites" that directed users to download and run malicious executables.

### Targeted Skill Categories
- ClawHub CLI typosquats (clawhub, clawhub1, clawhubb)
- Cryptocurrency/Solana wallet tools
- Polymarket trading bots
- YouTube utilities
- Auto-updaters
- Google Workspace integrations

### Mitigation
1. **Always check VirusTotal scan** on the skill's ClawHub page before installing
2. **Review SKILL.md source code** — look for suspicious `exec` commands, curl downloads, or prerequisite install instructions
3. **Use Clawdex** (by Koi Security) to scan skills: `clawhub install clawdex`
4. **Verify publisher** — check GitHub account age and history
5. **Prefer skills from `openclaw` org** (official) or well-known community members
6. **Never install skills that ask you to download executables** as "prerequisites"

### Per-Channel Skill Filtering
Restrict which skills are available in specific Discord channels:
```json5
guilds: {
  "GUILD_ID": {
    channels: {
      "public-channel": {
        skills: ["web_search"],  // Only web search in public channels
      },
      "agent-workspace": {
        // Omit skills key = all skills available
      },
      "restricted": {
        skills: [],  // No skills — agent can only use core tools
      }
    }
  }
}
```
