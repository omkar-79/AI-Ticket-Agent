#!/usr/bin/env python3
"""Create a test ticket to see in the dashboard."""

import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_ticket_agent.tools.ticket_manager import create_ticket_tool
from ai_ticket_agent.tools.resolution_tracker import track_resolution_attempt


def create_printer_ticket():
    """Create a test ticket for printer issues."""
    print("🎫 Creating Test Ticket for Printer Issues")
    print("=" * 50)
    
    # Create the ticket
    result = create_ticket_tool(
        subject="Printer showing offline - need help",
        description="My office printer is showing as offline and won't print any documents. I've tried restarting it but it's still not working. I need this fixed for an important meeting.",
        user_email="test.user@company.com",
        priority="high",
        category="hardware"
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
        
        # Add a resolution attempt
        print(f"\n🔧 Adding resolution attempt...")
        resolution_result = track_resolution_attempt(
            ticket_id=ticket_id,
            problem_description="Printer showing offline and won't print documents",
            solution_provided="I understand you're having trouble connecting to your printer. Let's try some common troubleshooting steps to get it working again. Here are the steps: 1. Check Physical Connections 2. Restart Devices 3. Check Printer Status 4. Update Printer Drivers 5. Run Printer Troubleshooter",
            user_feedback="I tried the steps but the printer is still offline. Can you help me further?",
            agent_type="self_service"
        )
        
        print(resolution_result)
        
        print(f"\n🎉 Test ticket created successfully!")
        print(f"📊 You can now view this ticket in the dashboard:")
        print(f"   1. Start the dashboard: python run.py dashboard")
        print(f"   2. Go to 'Ticket Management' section")
        print(f"   3. Search for ticket ID: {ticket_id}")
        print(f"   4. Or search for 'printer' to find the ticket")
        
    else:
        print("❌ Failed to create ticket")


if __name__ == "__main__":
    create_printer_ticket() 