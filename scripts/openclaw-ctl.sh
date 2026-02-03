#!/bin/bash
# OpenClaw Control Script
# Usage: openclaw-ctl.sh [command]

set -e

COMPOSE_FILE="/opt/openclaw/docker/docker-compose.yml"
PROJECT_NAME="openclaw"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_compose() {
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "Docker compose file not found at $COMPOSE_FILE"
        exit 1
    fi
}

cmd_start() {
    check_compose
    log_info "Starting OpenClaw gateway..."
    docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d openclaw-gateway
    log_info "Gateway started. Checking health..."
    sleep 5
    cmd_status
}

cmd_start_voice() {
    check_compose
    log_info "Starting OpenClaw with voice processing..."
    docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" --profile voice up -d
    log_info "Services started."
    cmd_status
}

cmd_stop() {
    check_compose
    log_info "Stopping OpenClaw services..."
    docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down
    log_info "Services stopped."
}

cmd_restart() {
    cmd_stop
    sleep 2
    cmd_start
}

cmd_status() {
    echo ""
    log_info "OpenClaw Service Status:"
    echo "----------------------------------------"
    docker ps --filter "name=openclaw" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""

    # Check gateway health if running
    if docker ps --filter "name=openclaw-gateway" --filter "status=running" -q | grep -q .; then
        HEALTH=$(docker inspect --format='{{.State.Health.Status}}' openclaw-gateway 2>/dev/null || echo "unknown")
        echo "Gateway Health: $HEALTH"
    fi
}

cmd_logs() {
    check_compose
    SERVICE=${1:-openclaw-gateway}
    log_info "Showing logs for $SERVICE (Ctrl+C to exit)..."
    docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs -f "$SERVICE"
}

cmd_shell() {
    log_info "Opening shell in gateway container..."
    docker exec -it openclaw-gateway /bin/sh
}

cmd_health() {
    log_info "Checking OpenClaw health..."

    # Gateway
    if curl -sf http://localhost:18789/health > /dev/null 2>&1; then
        echo -e "Gateway:    ${GREEN}HEALTHY${NC}"
    else
        echo -e "Gateway:    ${RED}UNHEALTHY${NC}"
    fi

    # Connected services
    echo ""
    log_info "Connected Services:"

    # RAG API
    if curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "RAG API:    ${GREEN}HEALTHY${NC}"
    else
        echo -e "RAG API:    ${RED}UNHEALTHY${NC}"
    fi

    # Qdrant
    if curl -sf http://localhost:6333/collections > /dev/null 2>&1; then
        echo -e "Qdrant:     ${GREEN}HEALTHY${NC}"
    else
        echo -e "Qdrant:     ${RED}UNHEALTHY${NC}"
    fi
}

cmd_pull() {
    check_compose
    log_info "Pulling latest OpenClaw images..."
    docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" pull
    log_info "Images updated. Run 'openclaw-ctl restart' to apply."
}

cmd_help() {
    echo "OpenClaw Control Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start       Start the OpenClaw gateway"
    echo "  start-voice Start gateway with voice processing"
    echo "  stop        Stop all OpenClaw services"
    echo "  restart     Restart OpenClaw services"
    echo "  status      Show service status"
    echo "  logs [svc]  Show logs (default: openclaw-gateway)"
    echo "  shell       Open shell in gateway container"
    echo "  health      Check health of all services"
    echo "  pull        Pull latest images"
    echo "  help        Show this help message"
    echo ""
}

# Main
case "${1:-help}" in
    start)       cmd_start ;;
    start-voice) cmd_start_voice ;;
    stop)        cmd_stop ;;
    restart)     cmd_restart ;;
    status)      cmd_status ;;
    logs)        cmd_logs "$2" ;;
    shell)       cmd_shell ;;
    health)      cmd_health ;;
    pull)        cmd_pull ;;
    help|--help|-h) cmd_help ;;
    *)
        log_error "Unknown command: $1"
        cmd_help
        exit 1
        ;;
esac
