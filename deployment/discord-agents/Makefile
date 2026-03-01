# DEPRECATED: This Makefile was for the old 5-container deployment model.
.PHONY: start stop restart status logs health clean setup

# Default action
all: start

# Setup environment
setup:
	@echo "Setting up Discord agent swarm..."
	@if [ ! -f .env ]; then \
		echo "Creating .env from template..."; \
		cp .env.template .env; \
		echo "⚠️  Please edit .env with your actual Discord bot tokens!"; \
	else \
		echo "✓ .env already exists"; \
	fi
	@chmod +x deploy-agents.sh

# Start all agents
start: setup
	@echo "🚀 Starting Discord agent swarm..."
	./deploy-agents.sh start

# Stop all agents
stop:
	@echo "🛑 Stopping Discord agent swarm..."
	./deploy-agents.sh stop

# Restart all agents
restart:
	@echo "🔄 Restarting Discord agent swarm..."
	./deploy-agents.sh restart

# Show status
status:
	@echo "📊 Agent swarm status:"
	./deploy-agents.sh status

# View logs
logs:
	@echo "📜 Following logs (Ctrl+C to exit)..."
	./deploy-agents.sh logs

# Health check
health:
	@echo "🏥 Running health checks..."
	./deploy-agents.sh health

# Clean up everything
clean:
	@echo "🧹 Cleaning up containers and volumes..."
	@read -p "Are you sure? This will delete all agent data! [y/N] " confirm && \
		if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
			docker-compose -f docker-compose.agents.yml down -v; \
			echo "✓ Cleanup complete"; \
		else \
			echo "Cancelled"; \
		fi

# Quick test - check if containers are running
test:
	@echo "🧪 Testing agent connectivity..."
	@for port in 8081 8082 8083 8084 8085; do \
		if curl -s -f http://localhost:$$port/health > /dev/null 2>&1; then \
			echo "✓ Port $$port: Healthy"; \
		else \
			echo "✗ Port $$port: Unreachable"; \
		fi \
	done

# Update images
update:
	@echo "⬆️  Pulling latest images..."
	docker-compose -f docker-compose.agents.yml pull
	@echo "🔄 Restarting agents..."
	./deploy-agents.sh restart

# Show resource usage
stats:
	@echo "📈 Resource usage:"
	docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.Status}}"

# Help
help:
	@echo "Available commands:"
	@echo "  make setup     - Create .env from template"
	@echo "  make start     - Start all agents"
	@echo "  make stop      - Stop all agents"
	@echo "  make restart   - Restart all agents"
	@echo "  make status    - Show container status"
	@echo "  make logs      - Follow logs"
	@echo "  make health    - Run health checks"
	@echo "  make test      - Test agent connectivity"
	@echo "  make stats     - Show resource usage"
	@echo "  make update    - Pull latest images and restart"
	@echo "  make clean     - Remove all containers and volumes"
	@echo "  make help      - Show this help"
