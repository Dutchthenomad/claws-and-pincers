# 12 — Resource Links

## Official Documentation

| Resource | URL | Notes |
|---|---|---|
| OpenClaw Docs | https://docs.openclaw.ai | Primary reference |
| Discord Channel Docs | https://docs.openclaw.ai/channels/discord | Discord integration |
| Multi-Agent Routing | https://docs.openclaw.ai/concepts/multi-agent | Agent config + bindings |
| Session Tools | https://docs.openclaw.ai/concepts/session-tool | sessions_send, sessions_spawn |
| Configuration Reference | https://docs.openclaw.ai/gateway/configuration | All config keys |
| Security Guide | https://docs.openclaw.ai/gateway/security | Sandboxing, tool policies |
| ClawHub Docs | https://docs.openclaw.ai/tools/clawhub | Skill registry |
| Skills Reference | https://docs.openclaw.ai/concepts/skills | How skills work |
| Gateway Runbook | https://docs.openclaw.ai/gateway/runbook | Operations guide |
| Docker + Sandboxing | https://docs.openclaw.ai/gateway/docker | Container setup |

## Source Code

| Resource | URL | Notes |
|---|---|---|
| OpenClaw Core | https://github.com/openclaw/openclaw | Main repo (157K+ stars) |
| ClawHub | https://github.com/openclaw/clawhub | Skill registry source |
| AGENTS.md (repo) | https://github.com/openclaw/openclaw/blob/main/AGENTS.md | Maintainer instructions |
| Multi-Agent Config (source) | https://github.com/openclaw/openclaw/blob/main/docs/concepts/multi-agent.md | Canonical multi-agent docs |
| CHANGELOG | https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md | Latest changes |

## DeepWiki (Auto-Generated Deep Docs)

| Resource | URL | Notes |
|---|---|---|
| Discord Integration | https://deepwiki.com/openclaw/openclaw/8.6-discord-integration | Deep technical reference |
| Multi-Agent Configuration | https://deepwiki.com/openclaw/openclaw/4.3-multi-agent-configuration | Agent config internals |
| Subagent Management | https://deepwiki.com/openclaw/openclaw/9.6-subagent-management | /subagents command |
| Agent Commands | https://deepwiki.com/openclaw/openclaw/12.2-agent-commands | CLI agent operations |

## Community

| Resource | URL | Notes |
|---|---|---|
| Discord Community | Search "Friends of the Crustacean" on Discord | Official community server |
| AnswerOverflow (Discord archives) | https://www.answeroverflow.com/m/1471735773106540544 | Discord bot setup thread |
| AnswerOverflow (Multi-agent) | https://www.answeroverflow.com/m/1471884586425520300 | Multi-agent setup thread |
| Awesome OpenClaw Skills | https://github.com/VoltAgent/awesome-openclaw-skills | Curated skill list (3,002 reviewed) |

## Registries

| Resource | URL | Notes |
|---|---|---|
| ClawHub (Skills) | https://clawhub.ai | Browse and install skills |
| OnlyCrabs (SOUL.md) | https://onlycrabs.ai | Browse and install personas |
| npm Package | https://www.npmjs.com/package/openclaw | npm registry |

## Tutorials and Guides

| Resource | URL | Notes |
|---|---|---|
| Discord Setup (Markaicode) | https://markaicode.com/openclaw-discord-setup-guide/ | Step-by-step Discord setup |
| Discord Setup (Stack Junkie) | https://www.stack-junkie.com/blog/openclaw-discord-setup-guide | Practical 6-step guide |
| Self-Host Guide (Pinggy) | https://pinggy.io/blog/self_hosting_openclaw_ai_agent/ | VPS deployment |
| Identity Architecture (MMNTM) | https://www.mmntm.net/articles/openclaw-identity-architecture | Deep dive on SOUL.md/IDENTITY.md |
| Tools + Skills Explained (WenHao Yu) | https://yu-wenhao.com/en/blog/openclaw-tools-skills-tutorial/ | 25 tools + 53 skills breakdown |
| Multi-Agent Orchestration (Zen van Riel) | https://zenvanriel.nl/ai-engineer-blog/openclaw-multi-agent-orchestration-guide/ | Orchestration patterns |
| "You Could've Invented OpenClaw" (Gist) | https://gist.github.com/dabit3/bc60d3bea0b02927995cd9bf53c3db32 | Build-from-scratch walkthrough |
| Complete Guide (Milvus) | https://milvus.io/blog/openclaw-formerly-clawdbot-moltbot-explained-a-complete-guide-to-the-autonomous-ai-agent.md | Comprehensive overview |
| Codecademy Tutorial | https://www.codecademy.com/article/open-claw-tutorial-installation-to-first-chat-setup | Beginner-friendly setup |

## Moltbook (Study Reference for Agent Interaction Patterns)

| Resource | URL | Notes |
|---|---|---|
| Moltbook Wikipedia | https://en.wikipedia.org/wiki/Moltbook | Neutral overview |
| Moltbook Explained (Built In) | https://builtin.com/articles/what-is-moltbook-openclaw | Technical breakdown |
| Moltbook (DigitalOcean) | https://www.digitalocean.com/resources/articles/what-is-moltbook | Detailed analysis |
| Moltbook (IEEE Spectrum) | https://spectrum.ieee.org/moltbook-agentic-ai-agents-openclaw | Security perspective |
| OpenClaw + Moltbook (IBM Think) | https://www.ibm.com/think/news/clawdbot-ai-agent-testing-limits-vertical-integration | Enterprise angle |

**Moltbook is a study reference only.** Do not connect your agents to Moltbook — it's an unmoderated external platform with significant security risks. Study its interaction patterns (heartbeat-driven autonomous posting, mention-based communication, community formation) to inform your private Discord server design.

## Security Research

| Resource | URL | Notes |
|---|---|---|
| ClawHavoc Campaign (SC Media) | https://www.scworld.com/news/openclaw-agents-targeted-with-341-malicious-clawhub-skills | 341 malicious skills |
| ClawHavoc (The Hacker News) | https://thehackernews.com/2026/02/researchers-find-341-malicious-clawhub.html | Detailed breakdown |
| Privacy Concerns (Northeastern) | https://news.northeastern.edu/2026/02/10/open-claw-ai-assistant/ | Academic perspective |

## Helm / Kubernetes

| Resource | URL | Notes |
|---|---|---|
| OpenClaw Helm Chart (5dlabs) | https://github.com/5dlabs/openclaw-helm | K8s deployment with NATS messaging |

NATS messaging in the Helm chart is designed for coordinated multi-agent workflows. Worth evaluating if scaling beyond a single VPS.

## Discord Skill (Built-in)

| Resource | URL | Notes |
|---|---|---|
| Discord Skill on ClawHub | https://skillsmp.com/skills/openclaw-openclaw-skills-discord-skill-md | Full skill reference |
| Discord Actions Reference | https://agent-skills.md/skills/openclaw/openclaw/discord | Action catalog |

## Multi-Agent Proposal (Community)

| Resource | URL | Notes |
|---|---|---|
| Multimodal Multi-Agent Proposal | https://medium.com/@gwrx2005/proposal-for-a-multimodal-multi-agent-system-using-openclaw-81f5e4488233 | Architecture proposal |
