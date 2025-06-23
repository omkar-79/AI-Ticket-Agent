#!/bin/bash

# AI Ticket Agent Startup Script
# This script provides easy commands to start the AI Ticket Agent system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Function to check dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check Poetry
    if ! command -v poetry &> /dev/null; then
        print_warning "Poetry is not installed. Installing dependencies with pip..."
        pip install -r requirements.txt
    else
        print_status "Installing dependencies with Poetry..."
        poetry install
    fi
    
    # Check .env file
    if [ ! -f .env ]; then
        print_warning ".env file not found. Copying from env.example..."
        cp env.example .env
        print_warning "Please edit .env file with your configuration before starting services."
    fi
    
    print_success "Dependencies check completed"
}

# Function to start all services
start_all() {
    print_status "Starting AI Ticket Agent System..."
    
    # Check if services are already running
    if check_port 8000; then
        print_warning "Port 8000 is already in use (ADK API Server)"
    fi
    
    if check_port 5001; then
        print_warning "Port 5001 is already in use (Slack App)"
    fi
    
    # Start services in background
    print_status "Starting ADK API Server on port 8000..."
    python3 -m uvicorn ai_ticket_agent.main:app --host 0.0.0.0 --port 8000 > logs/api_server.log 2>&1 &
    API_PID=$!
    echo $API_PID > pids/api_server.pid
    
    # Wait for API server to start
    sleep 3
    
    print_status "Starting Slack App on port 5001..."
    python3 slack_app.py > logs/slack_app.log 2>&1 &
    SLACK_PID=$!
    echo $SLACK_PID > pids/slack_app.pid
    
    print_status "Starting Email Monitor..."
    python3 ai_ticket_agent/tools/email_feedback_reader.py > logs/email_monitor.log 2>&1 &
    EMAIL_PID=$!
    echo $EMAIL_PID > pids/email_monitor.pid
    
    # Create logs directory if it doesn't exist
    mkdir -p logs
    mkdir -p pids
    
    print_success "All services started!"
    print_status "Service endpoints:"
    echo "  • ADK API Server: http://localhost:8000"
    echo "  • Slack App: http://localhost:5001"
    echo "  • Health Check: http://localhost:8000/health"
    echo ""
    print_status "To view logs:"
    echo "  • API Server: tail -f logs/api_server.log"
    echo "  • Slack App: tail -f logs/slack_app.log"
    echo "  • Email Monitor: tail -f logs/email_monitor.log"
    echo ""
    print_status "To stop all services: ./start.sh stop"
}

# Function to stop all services
stop_all() {
    print_status "Stopping AI Ticket Agent System..."
    
    # Stop services using PID files
    if [ -f pids/api_server.pid ]; then
        API_PID=$(cat pids/api_server.pid)
        if kill -0 $API_PID 2>/dev/null; then
            print_status "Stopping ADK API Server..."
            kill $API_PID
            rm pids/api_server.pid
        fi
    fi
    
    if [ -f pids/slack_app.pid ]; then
        SLACK_PID=$(cat pids/slack_app.pid)
        if kill -0 $SLACK_PID 2>/dev/null; then
            print_status "Stopping Slack App..."
            kill $SLACK_PID
            rm pids/slack_app.pid
        fi
    fi
    
    if [ -f pids/email_monitor.pid ]; then
        EMAIL_PID=$(cat pids/email_monitor.pid)
        if kill -0 $EMAIL_PID 2>/dev/null; then
            print_status "Stopping Email Monitor..."
            kill $EMAIL_PID
            rm pids/email_monitor.pid
        fi
    fi
    
    print_success "All services stopped"
}

# Function to show status
show_status() {
    print_status "AI Ticket Agent System Status"
    echo "=================================="
    
    # Check API Server
    if check_port 8000; then
        print_success "ADK API Server: Running on port 8000"
    else
        print_error "ADK API Server: Not running"
    fi
    
    # Check Slack App
    if check_port 5001; then
        print_success "Slack App: Running on port 5001"
    else
        print_error "Slack App: Not running"
    fi
    
    # Check database
    if [ -f helpdesk.db ]; then
        DB_SIZE=$(du -h helpdesk.db | cut -f1)
        print_success "Database: helpdesk.db ($DB_SIZE)"
    else
        print_error "Database: Not found"
    fi
    
    # Check PID files
    echo ""
    print_status "Process IDs:"
    if [ -f pids/api_server.pid ]; then
        echo "  • API Server: $(cat pids/api_server.pid)"
    fi
    if [ -f pids/slack_app.pid ]; then
        echo "  • Slack App: $(cat pids/slack_app.pid)"
    fi
    if [ -f pids/email_monitor.pid ]; then
        echo "  • Email Monitor: $(cat pids/email_monitor.pid)"
    fi
}

# Function to show logs
show_logs() {
    local service=$1
    
    case $service in
        "api")
            if [ -f logs/api_server.log ]; then
                tail -f logs/api_server.log
            else
                print_error "API Server log not found"
            fi
            ;;
        "slack")
            if [ -f logs/slack_app.log ]; then
                tail -f logs/slack_app.log
            else
                print_error "Slack App log not found"
            fi
            ;;
        "email")
            if [ -f logs/email_monitor.log ]; then
                tail -f logs/email_monitor.log
            else
                print_error "Email Monitor log not found"
            fi
            ;;
        *)
            print_error "Unknown service: $service"
            echo "Available services: api, slack, email"
            ;;
    esac
}

# Main script logic
case "${1:-start}" in
    "start")
        check_dependencies
        start_all
        ;;
    "stop")
        stop_all
        ;;
    "restart")
        stop_all
        sleep 2
        start_all
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs $2
        ;;
    "check")
        check_dependencies
        ;;
    "web")
        print_status "Starting ADK Web Interface..."
        adk web
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|check|web}"
        echo ""
        echo "Commands:"
        echo "  start   - Start all services"
        echo "  stop    - Stop all services"
        echo "  restart - Restart all services"
        echo "  status  - Show system status"
        echo "  logs    - Show logs (usage: $0 logs {api|slack|email})"
        echo "  check   - Check dependencies"
        echo "  web     - Start ADK Web Interface"
        exit 1
        ;;
esac 