#!/bin/bash
# health-check.sh - Quick health check for all 5 agents
# Run this to verify agents are online and responsive

echo "=========================================="
echo "🩺 OpenClaw Agent Health Check"
echo "=========================================="
echo ""

# Check Docker containers
echo "📦 Container Status:"
echo "--------------------"
docker ps --filter "name=openclaw-orchestrator\|openclaw-researcher\|openclaw-developer\|openclaw-sysadmin\|openclaw-reviewer" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# Check Discord login status
echo "💬 Discord Connection Status:"
echo "-----------------------------"
for agent in orchestrator researcher developer sysadmin reviewer; do
    LOGIN_STATUS=$(docker logs openclaw-$agent 2>&1 | grep "logged in to discord" | tail -1)
    if [ -n "$LOGIN_STATUS" ]; then
        # Extract bot ID
        BOT_ID=$(echo "$LOGIN_STATUS" | grep -oE '[0-9]{18,}')
        echo "✅ $agent: Connected (ID: $BOT_ID)"
    else
        echo "❌ $agent: Not connected"
    fi
done
echo ""

# Check ports
echo "🔌 Port Status:"
echo "---------------"
for port in 8081 8082 8083 8084 8085; do
    if curl -s http://127.0.0.1:$port > /dev/null 2>&1; then
        echo "✅ Port $port: Responding"
    else
        echo "⚠️  Port $port: No response (may be normal)"
    fi
done
echo ""

# Resource usage
echo "📊 Resource Usage:"
echo "------------------"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null | grep openclaw || echo "Stats not available"
echo ""

echo "=========================================="
echo "✅ Health check complete!"
echo "=========================================="
