#!/usr/bin/env python3
"""Test script for ticket lifecycle tracking functionality."""

import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_ticket_agent.database import db_manager
from ai_ticket_agent.tools.ticket_manager import create_ticket_tool, update_ticket_tool, get_ticket_info_tool
from ai_ticket_agent.tools.resolution_tracker import track_resolution_attempt, get_ticket_resolution_history


def test_ticket_lifecycle():
    """Test the complete ticket lifecycle."""
    print("🎫 Testing Ticket Lifecycle Tracking")
    print("=" * 50)
    
    # Test 1: Create a ticket
    print("\n1️⃣ Creating a new ticket...")
    result = create_ticket_tool(
        subject="Projector not connecting to laptop",
        description="I'm trying to connect my laptop to the conference room projector but it's not detecting the display. I've tried different cables and ports.",
        user_email="john.doe@company.com",
        priority="medium",
        category="hardware"
    )
    print(result)
    
    # Extract ticket ID from the result
    ticket_id = None
    for line in result.split('\n'):
        if 'Ticket ID:' in line:
            ticket_id = line.split('Ticket ID:')[1].strip()
            # Remove any markdown formatting
            ticket_id = ticket_id.replace('**', '').strip()
            break
    
    if not ticket_id:
        print("❌ Failed to extract ticket ID")
        return
    
    print(f"✅ Created ticket: {ticket_id}")
    
    # Test 2: Update ticket with team assignment
    print(f"\n2️⃣ Assigning ticket to Infrastructure Team...")
    result = update_ticket_tool(
        ticket_id=ticket_id,
        assigned_team="Infrastructure Team",
        slack_channel="#infrastructure-support",
        message="Ticket assigned to Infrastructure Team for hardware issue"
    )
    print(result)
    
    # Test 3: Track first resolution attempt (self-service)
    print(f"\n3️⃣ Tracking self-service resolution attempt...")
    result = track_resolution_attempt(
        ticket_id=ticket_id,
        problem_description="Projector not connecting to laptop",
        solution_provided="Try pressing Windows key + P and select 'Duplicate' or 'Extend' display mode. Also check if the projector is set to the correct input source.",
        user_feedback="I tried that but it still doesn't work. The projector shows 'No signal'.",
        agent_type="self_service"
    )
    print(result)
    
    # Test 4: Track second resolution attempt (escalation)
    print(f"\n4️⃣ Tracking escalation resolution attempt...")
    result = track_resolution_attempt(
        ticket_id=ticket_id,
        problem_description="Projector not connecting to laptop",
        solution_provided="This appears to be a hardware issue requiring physical inspection. I'm escalating this to the Infrastructure Team who will check the projector connections and cables.",
        user_feedback="Yes, please escalate this. I need this working for my presentation in 30 minutes.",
        agent_type="escalation"
    )
    print(result)
    
    # Test 5: Update ticket status to resolved
    print(f"\n5️⃣ Updating ticket to resolved...")
    result = update_ticket_tool(
        ticket_id=ticket_id,
        status="resolved",
        message="Issue resolved by Infrastructure Team - replaced faulty HDMI cable"
    )
    print(result)
    
    # Test 6: Get complete ticket information
    print(f"\n6️⃣ Getting complete ticket information...")
    result = get_ticket_info_tool(ticket_id)
    print(result)
    
    # Test 7: Get resolution history
    print(f"\n7️⃣ Getting resolution history...")
    result = get_ticket_resolution_history(ticket_id)
    print(result)
    
    print(f"\n🎉 Ticket lifecycle test completed for {ticket_id}!")


def test_multiple_tickets():
    """Test creating and managing multiple tickets."""
    print("\n\n🎫 Testing Multiple Ticket Management")
    print("=" * 50)
    
    # Create multiple tickets
    tickets = [
        {
            "subject": "Email not syncing on mobile",
            "description": "My work email stopped syncing on my iPhone. I can't receive new emails.",
            "user_email": "jane.smith@company.com",
            "priority": "high",
            "category": "software"
        },
        {
            "subject": "VPN connection issues",
            "description": "I can't connect to the company VPN from home. Getting authentication error.",
            "user_email": "mike.johnson@company.com",
            "priority": "medium",
            "category": "network"
        },
        {
            "subject": "Printer showing offline",
            "description": "The office printer shows as offline and won't print any documents.",
            "user_email": "sarah.wilson@company.com",
            "priority": "low",
            "category": "hardware"
        }
    ]
    
    created_tickets = []
    
    for i, ticket_data in enumerate(tickets, 1):
        print(f"\n{i}️⃣ Creating ticket: {ticket_data['subject']}")
        result = create_ticket_tool(**ticket_data)
        print(result)
        
        # Extract ticket ID
        ticket_id = None
        for line in result.split('\n'):
            if 'Ticket ID:' in line:
                ticket_id = line.split('Ticket ID:')[1].strip()
                # Remove any markdown formatting
                ticket_id = ticket_id.replace('**', '').strip()
                break
        
        if ticket_id:
            created_tickets.append(ticket_id)
    
    # Search for tickets
    print(f"\n🔍 Searching for all tickets...")
    from ai_ticket_agent.tools.ticket_manager import search_tickets_tool
    result = search_tickets_tool(limit=10)
    print(result)
    
    print(f"\n✅ Created {len(created_tickets)} tickets: {', '.join(created_tickets)}")


def main():
    """Main test function."""
    print("🧪 Ticket Lifecycle Tracking Test Suite")
    print("=" * 60)
    
    try:
        # Test single ticket lifecycle
        test_ticket_lifecycle()
        
        # Test multiple tickets
        test_multiple_tickets()
        
        print("\n🎉 All tests completed successfully!")
        print("\n📊 Database now contains:")
        print("  - Multiple tickets with different statuses")
        print("  - Resolution attempts and user feedback")
        print("  - Status updates and team assignments")
        print("  - Complete audit trail of ticket lifecycle")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 