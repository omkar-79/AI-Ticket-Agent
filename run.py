#!/usr/bin/env python3
"""Simple runner for AI Ticket Agent multi-agent system."""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from dotenv import load_dotenv


def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        ("google.adk", "google-adk"),
        ("google.genai", "google-genai"), 
        ("dotenv", "python-dotenv")
    ]
    
    missing_packages = []
    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install with: poetry install")
        return False
    
    print("✅ All dependencies found")
    return True


def setup_environment():
    """Set up environment variables."""
    print("⚙️ Setting up environment...")
    
    # Load .env file if it exists
    if Path(".env").exists():
        load_dotenv()
        print("✅ Loaded .env file")
    else:
        print("⚠️ No .env file found. Using default settings.")
    
    # Check for Google Cloud credentials
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        print("⚠️ GOOGLE_APPLICATION_CREDENTIALS not set")
        print("Please set up Google Cloud authentication")


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
    subprocess.run([sys.executable, "test_agents.py"])
    print("\n🚨 Running escalation tests...")
    subprocess.run([sys.executable, "test_escalation_scenarios.py"])
    print("\n🔔 Running Slack notification tests...")
    subprocess.run([sys.executable, "test_slack_notifications.py"])


def show_status():
    """Show system status and configuration."""
    print("📊 AI Ticket Agent System Status")
    print("=" * 40)
    
    # Check environment
    env_vars = [
        "GOOGLE_CLOUD_PROJECT",
        "GOOGLE_CLOUD_LOCATION", 
        "GOOGLE_APPLICATION_CREDENTIALS"
    ]
    
    print("\nEnvironment Variables:")
    for var in env_vars:
        value = os.getenv(var, "Not set")
        status = "✓" if value != "Not set" else "✗"
        print(f"  {status} {var}: {value}")
    
    # Check files
    files = [
        ".env",
        "ai_ticket_agent/agent.py",
        "ai_ticket_agent/prompt.py"
    ]
    
    print("\nConfiguration Files:")
    for file in files:
        exists = Path(file).exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {file}")
    
    print("\nAvailable Commands:")
    print("  python run.py web           - Start ADK web interface")
    print("  python run.py cli           - Start ADK CLI interface")
    print("  python run.py test          - Run tests")
    print("  python run.py status        - Show system status")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="AI Ticket Agent - Multi-Agent IT Support System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py web           # Start ADK web interface
  python run.py cli           # Start ADK CLI interface
  python run.py test          # Run tests
        """
    )
    
    parser.add_argument(
        "mode",
        choices=["web", "cli", "test", "status"],
        help="Mode to run the system in"
    )
    
    args = parser.parse_args()
    
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    # Set up environment
    setup_environment()
    
    # Run based on mode
    if args.mode == "web":
        run_adk_web()
    elif args.mode == "cli":
        run_adk_cli()
    elif args.mode == "test":
        run_tests()
    elif args.mode == "status":
        show_status()


if __name__ == "__main__":
    main() 