#!/usr/bin/env python3
"""Initialize the ticket tracking database."""

import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_ticket_agent.database import init_database
from dotenv import load_dotenv


def main():
    """Initialize the database."""
    print("🗄️ Initializing Ticket Tracking Database")
    print("=" * 50)
    
    # Load environment variables
    env_file = Path(".env")
    if env_file.exists():
        load_dotenv()
        print("✅ Loaded .env file")
    else:
        print("⚠️ No .env file found. Using default SQLite database.")
    
    # Check database configuration
    database_url = os.getenv("DATABASE_URL", "sqlite:///./tickets.db")
    print(f"📊 Database URL: {database_url}")
    
    try:
        # Initialize database
        init_database()
        
        print("\n🎉 Database initialization completed successfully!")
        print("\n📋 Database includes the following tables:")
        print("  - tickets: Main ticket information")
        print("  - ticket_status_updates: Status change history")
        print("  - resolution_attempts: Resolution attempt tracking")
        print("  - team_assignments: Team routing history")
        
        print("\n🚀 Ready to track tickets!")
        
    except Exception as e:
        print(f"\n❌ Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 