#!/usr/bin/env python3
"""
Deployment script for AI Ticket Agent System.

This script manages all the different services:
- ADK API Server (Port 8000) - Main agent API
- ADK Web Interface (Port 8080) - Web UI for ticket creation
- Slack App (Port 5001) - Slack interactions
- Email Feedback Monitor - Background process
- Database - SQLite file
"""

import argparse
import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_file = Path(".env")
if env_file.exists():
    load_dotenv()

class ServiceManager:
    def __init__(self):
        self.processes = {}
        self.running = False
        
    def start_service(self, name, command, port=None, env=None):
        """Start a service in a separate process."""
        try:
            print(f"🚀 Starting {name}...")
            
            # Prepare environment
            service_env = os.environ.copy()
            if env:
                service_env.update(env)
            
            # Start the process
            process = subprocess.Popen(
                command,
                env=service_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes[name] = {
                'process': process,
                'command': command,
                'port': port
            }
            
            # Wait a moment to see if it starts successfully
            time.sleep(2)
            if process.poll() is None:
                print(f"✅ {name} started successfully")
                if port:
                    print(f"   📡 Available at: http://localhost:{port}")
            else:
                print(f"❌ {name} failed to start")
                stdout, stderr = process.communicate()
                print(f"   Error: {stderr}")
                
        except Exception as e:
            print(f"❌ Error starting {name}: {e}")
    
    def stop_service(self, name):
        """Stop a specific service."""
        if name in self.processes:
            process_info = self.processes[name]
            process = process_info['process']
            
            print(f"🛑 Stopping {name}...")
            try:
                process.terminate()
                process.wait(timeout=10)
                print(f"✅ {name} stopped")
            except subprocess.TimeoutExpired:
                print(f"⚠️ {name} didn't stop gracefully, forcing...")
                process.kill()
            except Exception as e:
                print(f"❌ Error stopping {name}: {e}")
            
            del self.processes[name]
    
    def stop_all(self):
        """Stop all running services."""
        print("🛑 Stopping all services...")
        for name in list(self.processes.keys()):
            self.stop_service(name)
        self.running = False
    
    def monitor_services(self):
        """Monitor running services and restart if needed."""
        while self.running:
            for name, info in list(self.processes.items()):
                process = info['process']
                if process.poll() is not None:
                    print(f"⚠️ {name} has stopped, restarting...")
                    self.stop_service(name)
                    self.start_service(name, info['command'], info['port'])
            time.sleep(30)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print("\n🛑 Received shutdown signal...")
        self.stop_all()
        sys.exit(0)

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        'google.adk',
        'fastapi',
        'uvicorn',
        'flask',
        'imaplib',
        'sqlite3'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing dependencies: {missing}")
        print("Please install with: poetry install")
        return False
    
    print("✅ All dependencies are available")
    return True

def check_environment():
    """Check if required environment variables are set."""
    required_vars = [
        'GOOGLE_CLOUD_PROJECT',
        'GOOGLE_CLOUD_LOCATION',
        'SLACK_BOT_TOKEN',
        'SLACK_CHANNEL_ID',
        'SUPPORT_EMAIL',
        'SUPPORT_EMAIL_PASSWORD'
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"⚠️ Missing environment variables: {missing}")
        print("Please check your .env file")
        return False
    
    print("✅ Environment variables are configured")
    return True

def start_all_services():
    """Start all services for the AI Ticket Agent system."""
    manager = ServiceManager()
    manager.running = True
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, manager.signal_handler)
    signal.signal(signal.SIGTERM, manager.signal_handler)
    
    print("🚀 Starting AI Ticket Agent System...")
    print("=" * 50)
    
    # 1. Start ADK API Server (Port 8000)
    manager.start_service(
        "ADK API Server",
        [sys.executable, "-m", "uvicorn", "ai_ticket_agent.main:app", "--host", "0.0.0.0", "--port", "8000"],
        port=8000
    )
    
    # Wait for API server to start
    time.sleep(3)
    
    # 2. Start Slack App (Port 5001)
    manager.start_service(
        "Slack App",
        [sys.executable, "slack_app.py"],
        port=5001
    )
    
    # 3. Start Email Feedback Monitor (Background process)
    manager.start_service(
        "Email Monitor",
        [sys.executable, "ai_ticket_agent/tools/email_feedback_reader.py"]
    )
    
    print("\n" + "=" * 50)
    print("🎉 AI Ticket Agent System is running!")
    print("\n📡 Service Endpoints:")
    print("   • ADK API Server: http://localhost:8000")
    print("   • ADK Web Interface: http://localhost:8080 (run 'adk web' separately)")
    print("   • Slack App: http://localhost:5001")
    print("   • Health Check: http://localhost:8000/health")
    print("\n🔧 Management:")
    print("   • Press Ctrl+C to stop all services")
    print("   • Check logs for each service")
    print("   • Database: helpdesk.db")
    
    # Start monitoring thread
    monitor_thread = threading.Thread(target=manager.monitor_services, daemon=True)
    monitor_thread.start()
    
    try:
        # Keep the main thread alive
        while manager.running:
            time.sleep(1)
    except KeyboardInterrupt:
        manager.signal_handler(signal.SIGINT, None)

def start_individual_service(service_name):
    """Start a specific service."""
    if service_name == "api":
        print("📡 Starting ADK API Server...")
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "ai_ticket_agent.main:app", 
            "--host", "0.0.0.0", "--port", "8000"
        ])
    elif service_name == "slack":
        print("🔗 Starting Slack App...")
        subprocess.run([sys.executable, "slack_app.py"])
    elif service_name == "email":
        print("📬 Starting Email Monitor...")
        subprocess.run([sys.executable, "ai_ticket_agent/tools/email_feedback_reader.py"])
    elif service_name == "web":
        print("🌐 Starting ADK Web Interface...")
        subprocess.run(["adk", "web"])
    else:
        print(f"❌ Unknown service: {service_name}")

def show_status():
    """Show system status."""
    print("📊 AI Ticket Agent System Status")
    print("=" * 40)
    
    # Check if services are running
    import psutil
    
    services = {
        "ADK API Server": 8000,
        "Slack App": 5001,
        "ADK Web": 8080
    }
    
    for service, port in services.items():
        try:
            # Check if port is in use
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    print(f"✅ {service}: Running on port {port}")
                    break
            else:
                print(f"❌ {service}: Not running")
        except Exception:
            print(f"❓ {service}: Status unknown")
    
    # Check database
    db_file = Path("helpdesk.db")
    if db_file.exists():
        print(f"✅ Database: {db_file} ({db_file.stat().st_size / 1024:.1f} KB)")
    else:
        print("❌ Database: Not found")
    
    # Check environment
    print(f"\nEnvironment:")
    print(f"  • Project: {os.getenv('GOOGLE_CLOUD_PROJECT', 'Not set')}")
    print(f"  • Location: {os.getenv('GOOGLE_CLOUD_LOCATION', 'Not set')}")
    print(f"  • Slack Channel: {os.getenv('SLACK_CHANNEL_ID', 'Not set')}")

def main():
    parser = argparse.ArgumentParser(description="AI Ticket Agent Deployment Manager")
    parser.add_argument("command", choices=[
        "start", "stop", "status", "api", "slack", "email", "web", "check"
    ], help="Command to execute")
    
    args = parser.parse_args()
    
    if args.command == "check":
        print("🔍 Checking system requirements...")
        check_dependencies()
        check_environment()
    elif args.command == "status":
        show_status()
    elif args.command == "start":
        if not check_dependencies() or not check_environment():
            print("❌ System check failed. Please fix issues before starting.")
            sys.exit(1)
        start_all_services()
    else:
        start_individual_service(args.command)

if __name__ == "__main__":
    main() 