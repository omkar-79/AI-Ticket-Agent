#!/usr/bin/env python3
"""
Quick start script for AI Ticket Agent.

This script provides easy commands to run the AI Ticket Agent system
in different modes: development, API server, or ADK web interface.
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import google.adk
        import fastapi
        import uvicorn
        print("✓ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please install dependencies with: poetry install")
        return False


def setup_environment():
    """Set up environment variables if .env file exists."""
    env_file = Path(".env")
    if env_file.exists():
        print("✓ Found .env file, loading environment variables")
        from dotenv import load_dotenv
        load_dotenv()
    else:
        print("⚠ No .env file found. Copy env.example to .env and configure it.")


def run_development():
    """Run the system in development mode."""
    print("🚀 Starting AI Ticket Agent in development mode...")
    
    # Start the API server
    print("📡 Starting API server on http://localhost:8000")
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "ai_ticket_agent.main:app", 
        "--reload", "--host", "0.0.0.0", "--port", "8000"
    ])


def run_api_server():
    """Run only the API server."""
    print("📡 Starting API server...")
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "ai_ticket_agent.main:app", 
        "--host", "0.0.0.0", "--port", "8000"
    ])


def run_adk_web():
    """Run the ADK web interface."""
    print("🌐 Starting ADK web interface...")
    subprocess.run(["adk", "web"])


def run_adk_cli():
    """Run the ADK CLI interface."""
    print("💬 Starting ADK CLI interface...")
    subprocess.run(["adk", "run", "ai_ticket_agent"])


def run_tests():
    """Run the test suite."""
    print("🧪 Running tests...")
    subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"])


def run_linting():
    """Run code linting."""
    print("🔍 Running code linting...")
    subprocess.run([sys.executable, "-m", "black", "ai_ticket_agent/", "tests/"])
    subprocess.run([sys.executable, "-m", "flake8", "ai_ticket_agent/", "tests/"])


def run_monitoring():
    """Run the monitoring system."""
    print("🔍 Starting monitoring system...")
    
    # Import monitoring functions
    sys.path.append('.')
    from ai_ticket_agent.tools.scheduler import start_monitoring_scheduler, get_scheduler_status
    from ai_ticket_agent.tools.monitoring import run_monitoring_cycle
    
    # Start the monitoring scheduler
    print("🚀 Starting monitoring scheduler (5-minute intervals)...")
    start_monitoring_scheduler(interval_minutes=5)
    
    try:
        # Keep the monitoring system running
        print("✅ Monitoring system is running. Press Ctrl+C to stop.")
        while True:
            import time
            time.sleep(60)  # Check status every minute
            
            # Show status
            status = get_scheduler_status()
            if status['running']:
                print(f"📊 Monitoring status: {status['run_count']} cycles completed, {status['error_count']} errors")
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping monitoring system...")
        from ai_ticket_agent.tools.scheduler import stop_monitoring_scheduler
        stop_monitoring_scheduler()
        print("✅ Monitoring system stopped")


def run_monitoring_test():
    """Run a single monitoring cycle for testing."""
    print("🧪 Running monitoring test...")
    
    # Import monitoring functions
    sys.path.append('.')
    from ai_ticket_agent.tools.monitoring import run_monitoring_cycle
    
    # Run a single monitoring cycle
    results = run_monitoring_cycle()
    
    print("📊 Monitoring Test Results:")
    print(f"  - Tickets checked: {results['monitoring_results']['tickets_checked']}")
    print(f"  - Escalations found: {results['monitoring_results']['summary']['escalations_needed']}")
    print(f"  - SLA alerts: {results['monitoring_results']['summary']['sla_alerts']}")
    print(f"  - Actions taken: {len(results['actions_taken'])}")
    
    if results['actions_taken']:
        print("\nActions taken:")
        for action in results['actions_taken']:
            print(f"  - {action.get('ticket_id', 'Unknown')}: {action.get('actions_taken', [])}")


def show_status():
    """Show system status and configuration."""
    print("📊 AI Ticket Agent System Status")
    print("=" * 40)
    
    # Check environment
    env_vars = [
        "GOOGLE_CLOUD_PROJECT",
        "GOOGLE_CLOUD_LOCATION", 
        "DATABASE_URL",
        "REDIS_URL"
    ]
    
    print("\nEnvironment Variables:")
    for var in env_vars:
        value = os.getenv(var, "Not set")
        status = "✓" if value != "Not set" else "✗"
        print(f"  {status} {var}: {value}")
    
    # Check files
    files = [
        ".env",
        "config/scenarios/default.json",
        "ai_ticket_agent/agent.py"
    ]
    
    print("\nConfiguration Files:")
    for file in files:
        exists = Path(file).exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {file}")
    
    # Check monitoring status
    try:
        sys.path.append('.')
        from ai_ticket_agent.tools.scheduler import get_scheduler_status
        status = get_scheduler_status()
        print(f"\nMonitoring System:")
        print(f"  {'✓' if status['running'] else '✗'} Status: {'Running' if status['running'] else 'Stopped'}")
        print(f"  📊 Cycles completed: {status['run_count']}")
        print(f"  ⚠️  Errors: {status['error_count']}")
        if status['last_run']:
            print(f"  🕐 Last run: {status['last_run']}")
    except Exception as e:
        print(f"\nMonitoring System: Error checking status - {e}")
    
    print("\nAvailable Commands:")
    print("  python run.py dev           - Start development server")
    print("  python run.py api           - Start API server only")
    print("  python run.py web           - Start ADK web interface")
    print("  python run.py cli           - Start ADK CLI interface")
    print("  python run.py monitor       - Start monitoring system")
    print("  python run.py monitor-test  - Run single monitoring cycle")
    print("  python run.py test          - Run tests")
    print("  python run.py lint          - Run code linting")
    print("  python run.py status        - Show system status")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="AI Ticket Agent - Autonomous IT Helpdesk Ticket Orchestration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py dev           # Start development server
  python run.py api           # Start API server only
  python run.py web           # Start ADK web interface
  python run.py monitor       # Start monitoring system
  python run.py monitor-test  # Test monitoring system
  python run.py test          # Run tests
        """
    )
    
    parser.add_argument(
        "mode",
        choices=["dev", "api", "web", "cli", "monitor", "monitor-test", "test", "lint", "status"],
        help="Mode to run the system in"
    )
    
    args = parser.parse_args()
    
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    # Set up environment
    setup_environment()
    
    # Run based on mode
    if args.mode == "dev":
        run_development()
    elif args.mode == "api":
        run_api_server()
    elif args.mode == "web":
        run_adk_web()
    elif args.mode == "cli":
        run_adk_cli()
    elif args.mode == "monitor":
        run_monitoring()
    elif args.mode == "monitor-test":
        run_monitoring_test()
    elif args.mode == "test":
        run_tests()
    elif args.mode == "lint":
        run_linting()
    elif args.mode == "status":
        show_status()


if __name__ == "__main__":
    main() 