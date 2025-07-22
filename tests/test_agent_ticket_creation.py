#!/usr/bin/env python3
"""Test script to verify agent ticket creation in database."""

import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_ticket_agent.database import db_manager


def check_database_tickets():
    """Check what tickets are currently in the database."""
    print("🔍 Checking Database for Tickets")
    print("=" * 50)
    
    session = db_manager.get_session()
    try:
        # Get all tickets
        tickets = db_manager.search_tickets(session, limit=100)
        
        print(f"📊 Total tickets in database: {len(tickets)}")
        
        if tickets:
            print("\n📋 Recent Tickets:")
            for i, ticket in enumerate(tickets[:10], 1):
                print(f"{i}. {ticket.ticket_id} - {ticket.subject}")
                print(f"   Status: {ticket.status.value}, Priority: {ticket.priority.value}")
                print(f"   User: {ticket.user_email}, Created: {ticket.created_at}")
                print(f"   Resolution Attempts: {len(ticket.resolution_attempts)}")
                print()
        else:
            print("❌ No tickets found in database")
            
        return len(tickets)
        
    finally:
        session.close()


def test_agent_integration():
    """Test that agents are properly integrated with ticket creation."""
    print("\n🧪 Testing Agent Integration")
    print("=" * 50)
    
    # Check if agents have ticket creation tools
    try:
        from ai_ticket_agent.sub_agents.self_service.agent import self_service_agent
        from ai_ticket_agent.sub_agents.escalation.agent import escalation_agent
        
        # Check self-service agent tools
        self_service_tools = [tool.__name__ if hasattr(tool, '__name__') else str(tool) for tool in self_service_agent.tools]
        print(f"✅ Self-service agent tools: {self_service_tools}")
        
        # Check escalation agent tools
        escalation_tools = [tool.__name__ if hasattr(tool, '__name__') else str(tool) for tool in escalation_agent.tools]
        print(f"✅ Escalation agent tools: {escalation_tools}")
        
        # Check if create_ticket is available
        if any('create_ticket' in str(tool) for tool in self_service_tools):
            print("✅ Self-service agent has create_ticket tool")
        else:
            print("❌ Self-service agent missing create_ticket tool")
            
        if any('create_ticket' in str(tool) for tool in escalation_tools):
            print("✅ Escalation agent has create_ticket tool")
        else:
            print("❌ Escalation agent missing create_ticket tool")
            
    except Exception as e:
        print(f"❌ Error checking agent integration: {e}")


def create_test_ticket_via_agent():
    """Create a test ticket using the ticket manager directly."""
    print("\n🎫 Creating Test Ticket via Ticket Manager")
    print("=" * 50)
    
    try:
        from ai_ticket_agent.tools.ticket_manager import create_ticket_tool
        from ai_ticket_agent.tools.resolution_tracker import track_resolution_attempt
        
        # Create ticket
        result = create_ticket_tool(
            subject="Test ticket from agent integration",
            description="This is a test ticket to verify agent integration with database",
            user_email="test.agent@company.com",
            priority="medium",
            category="software"
        )
        
        print(result)
        
        # Extract ticket ID
        ticket_id = None
        for line in result.split('\n'):
            if 'Ticket ID:' in line:
                ticket_id = line.split('Ticket ID:')[1].strip()
                ticket_id = ticket_id.replace('**', '').strip()
                break
        
        if ticket_id:
            print(f"\n✅ Created ticket: {ticket_id}")
            
            # Add resolution attempt
            resolution_result = track_resolution_attempt(
                ticket_id=ticket_id,
                problem_description="Test ticket from agent integration",
                solution_provided="This is a test resolution attempt",
                user_feedback="Test feedback",
                agent_type="self_service"
            )
            
            print(f"🔧 Resolution tracking: {resolution_result}")
            
            return ticket_id
        else:
            print("❌ Failed to extract ticket ID")
            return None
            
    except Exception as e:
        print(f"❌ Error creating test ticket: {e}")
        return None


def main():
    """Main test function."""
    print("🧪 Agent Ticket Creation Test Suite")
    print("=" * 60)
    
    # Check current database state
    initial_count = check_database_tickets()
    
    # Test agent integration
    test_agent_integration()
    
    # Create test ticket
    new_ticket_id = create_test_ticket_via_agent()
    
    # Check database again
    print("\n🔍 Checking Database After Test")
    print("=" * 50)
    final_count = check_database_tickets()
    
    # Summary
    print("\n📋 Test Summary")
    print("=" * 30)
    print(f"Initial tickets: {initial_count}")
    print(f"Final tickets: {final_count}")
    print(f"New tickets created: {final_count - initial_count}")
    
    if new_ticket_id:
        print(f"✅ Test ticket created: {new_ticket_id}")
        print(f"📊 You can view this ticket in the dashboard:")
        print(f"   1. Start dashboard: python run.py dashboard")
        print(f"   2. Search for: {new_ticket_id}")
    else:
        print("❌ Failed to create test ticket")
    
    print("\n🎯 Next Steps:")
    print("1. Start the ADK web interface: python run.py web")
    print("2. Report a printer issue with your email")
    print("3. Check the dashboard to see if a ticket was created")
    print("4. The agent should now create tickets automatically!")


if __name__ == "__main__":
    main() 