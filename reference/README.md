# OpenClaw Discord Agent Team — Project Documentation

## Purpose

This documentation folder contains comprehensive research and architectural planning for building an autonomous multi-agent system using OpenClaw deployed on a Discord server. The goal is a structured agent team with individual workspaces, shared collaboration channels, recursive feedback loops, and human oversight — a proto-AGI bootstrap environment.

## Document Index

| Document | Description |
|---|---|
| [01-OPENCLAW-OVERVIEW.md](./01-OPENCLAW-OVERVIEW.md) | What OpenClaw is, current state of the ecosystem, key concepts |
| [02-DISCORD-INTEGRATION.md](./02-DISCORD-INTEGRATION.md) | Discord bot setup, permissions, channel config, the discord tool/skill |
| [03-MULTI-AGENT-ARCHITECTURE.md](./03-MULTI-AGENT-ARCHITECTURE.md) | Multi-agent routing, bindings, isolation, per-agent config |
| [04-AGENT-COMMUNICATION.md](./04-AGENT-COMMUNICATION.md) | Agent-to-agent messaging, session tools, subagents, feedback loops |
| [05-IDENTITY-AND-PERSONAS.md](./05-IDENTITY-AND-PERSONAS.md) | SOUL.md, AGENTS.md, IDENTITY.md, persona design patterns |
| [06-SKILLS-AND-CLAWHUB.md](./06-SKILLS-AND-CLAWHUB.md) | ClawHub ecosystem, relevant skills, security considerations |
| [07-SERVER-ARCHITECTURE.md](./07-SERVER-ARCHITECTURE.md) | Discord server structure, channel/category layout, routing plan |
| [08-CONFIGURATION-REFERENCE.md](./08-CONFIGURATION-REFERENCE.md) | Complete config.json5 reference with annotated examples |
| [09-AUTONOMOUS-LOOPS.md](./09-AUTONOMOUS-LOOPS.md) | Heartbeat, cron, recursive workflows, loop safety |
| [10-SECURITY-AND-SAFETY.md](./10-SECURITY-AND-SAFETY.md) | Bot loop prevention, sandboxing, token safety, skill auditing |
| [11-DEPLOYMENT-GUIDE.md](./11-DEPLOYMENT-GUIDE.md) | VPS deployment, Docker, systemd, production considerations |
| [12-RESOURCE-LINKS.md](./12-RESOURCE-LINKS.md) | Curated links to all key documentation, community, and tools |
| [13-BROWSER-AUTOMATION.md](./13-BROWSER-AUTOMATION.md) | Browser automation setup on ThinkPad — managed profile, Chrome relay, extension, Playwright |

## Architecture Summary

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           Discord Server                                 │
│                                                                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │ 🎯 ORCHESTR. │ │ 🔬 RESEARCH  │ │ 💻 CODER     │ │ 🔍 REVIEWER  │   │
│  │  #workspace   │ │  #workspace  │ │  #workspace  │ │  #workspace  │   │
│  │  #logs        │ │  #logs       │ │  #logs       │ │  #logs       │   │
│  │  #planning    │ │  #archive    │ │  #snippets   │ │              │   │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘   │
│         │                │                 │                │            │
│         └────────┬───────┴─────────┬───────┴────────┬──────┘            │
│                  │                 │                 │                    │
│  ┌───────────────┴─────────────────┴─────────────────┴──────────────┐   │
│  │                   🤝 SHARED WORKSPACE                             │   │
│  │  #task-dispatch   #collaboration   #review-queue   #completed     │   │
│  ├───────────────────────────────────────────────────────────────────┤   │
│  │                   👤 HUMAN CONTROL                                │   │
│  │  #human-oversight   #direct-command   #system-logs   #cost-track  │   │
│  └───────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                          ┌─────────┴─────────┐
                          │  OpenClaw Gateway  │
                          │  ws://127.0.0.1:   │
                          │      18789         │
                          └─────────┬─────────┘
                                    │
           ┌────────────────┬───────┴───────┬────────────────┐
           │                │               │                │
     ┌─────┴─────┐   ┌─────┴─────┐   ┌─────┴─────┐   ┌─────┴─────┐
     │ orchestr.  │   │ researcher │   │ coder      │   │ reviewer   │
     │ Opus 4.6   │   │ Sonnet 4.5 │   │ Sonnet 4.5 │   │ Sonnet 4.5 │
     │ workspace/ │   │ workspace/ │   │ workspace/ │   │ workspace/ │
     │ SOUL.md    │   │ SOUL.md    │   │ SOUL.md    │   │ SOUL.md    │
     └───────────┘   └───────────┘   └───────────┘   └───────────┘
```

## For Claude Code

When ingesting these docs, start with `01-OPENCLAW-OVERVIEW.md` for context, then `08-CONFIGURATION-REFERENCE.md` and `07-SERVER-ARCHITECTURE.md` for the build spec. The other docs provide deep-dive context on individual subsystems.

## Last Updated

2026-02-16 — Based on OpenClaw version 2026.2.16 (latest as of this date)
