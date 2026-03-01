#!/bin/bash
# DEPRECATED: This script was for the old 5-container deployment model.
# deploy-agents.sh - Deploy all 5 Discord agents with best practices
# Usage: ./deploy-agents.sh [start|stop|restart|status|logs]

set -e

ACTION=${1:-start}
COMPOSE_FILE="/opt/openclaw/discord-agents/docker-compose.agents.yml"
ENV_FILE="/opt/openclaw/discord-agents/.env"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker not found. Please install Docker."
        exit 1
    fi
    
    # Check docker-compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "docker-compose not found. Please install docker-compose."
        exit 1
    fi
    
    # Check env file
    if [ ! -f "$ENV_FILE" ]; then
        log_error "Environment file not found: $ENV_FILE"
        log_info "Copy from template: cp $ENV_FILE.template $ENV_FILE"
        exit 1
    fi
    
    # Check if tokens are set
    if grep -q "your_.*_token_here\|REPLACE_WITH" "$ENV_FILE"; then
        log_warn "Tokens appear to be placeholders in $ENV_FILE"
        log_info "Please update with actual Discord bot tokens"
    fi
    
    log_info "Prerequisites OK"
}

start_agents() {
    log_info "Starting Discord agent swarm..."
    
    cd "$(dirname "$COMPOSE_FILE")"
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    
    log_info "Waiting for services to initialize..."
    sleep 5
    
    # Check health
    docker-compose -f "$COMPOSE_FILE" ps
    
    log_info "Agent swarm deployed!"
    log_info "View logs: ./deploy-agents.sh logs"
}

stop_agents() {
    log_info "Stopping Discord agent swarm..."
    cd "$(dirname "$COMPOSE_FILE")"
    docker-compose -f "$COMPOSE_FILE" down
    log_info "Agent swarm stopped"
}

restart_agents() {
    log_info "Restarting Discord agent swarm..."
    cd "$(dirname "$COMPOSE_FILE")"
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" restart
    log_info "Agent swarm restarted"
}

status_agents() {
    log_info "Agent swarm status:"
    cd "$(dirname "$COMPOSE_FILE")"
    docker-compose -f "$COMPOSE_FILE" ps
}

logs_agents() {
    cd "$(dirname "$COMPOSE_FILE")"
    docker-compose -f "$COMPOSE_FILE" logs -f --tail=100
}

health_check() {
    log_info "Running health checks..."
    
    cd "$(dirname "$COMPOSE_FILE")"
    
    # Check each service
    services=("orchestrator" "researcher" "developer" "sysadmin" "reviewer")
    all_healthy=true
    
    for service in "${services[@]}"; do
        status=$(docker-compose -f "$COMPOSE_FILE" ps -q "openclaw-$service" | xargs docker inspect -f '{{.State.Health.Status}}' 2>/dev/null || echo "unknown")
        if [ "$status" = "healthy" ]; then
            log_info "$service: ✅ Healthy"
        elif [ "$status" = "starting" ]; then
            log_warn "$service: ⏳ Starting..."
            all_healthy=false
        else
            log_error "$service: ❌ Unhealthy ($status)"
            all_healthy=false
        fi
    done
    
    if [ "$all_healthy" = true ]; then
        log_info "All agents healthy!"
        return 0
    else
        log_warn "Some agents not healthy yet"
        return 1
    fi
}

case "$ACTION" in
    start)
        check_prerequisites
        start_agents
        sleep 3
        health_check
        ;;
    stop)
        stop_agents
        ;;
    restart)
        restart_agents
        sleep 3
        health_check
        ;;
    status)
        status_agents
        ;;
    logs)
        logs_agents
        ;;
    health)
        health_check
        ;;
    *)
        echo "Usage: $0 [start|stop|restart|status|logs|health]"
        exit 1
        ;;
esac
