#!/usr/bin/env python3
"""
Test script for team assignment notifications.
"""

from dotenv import load_dotenv
from ai_ticket_agent.tools.notifications import send_team_assignment_notification, get_notification_config

def test_new_assignment():
    """Test notification for a new ticket assignment."""
    print("🧪 Testing New Ticket Assignment Notification")
    print("=" * 50)
    
    ticket_data = {
        "subject": "WiFi Connection Issues in Building A",
        "priority": "HIGH",
        "category": "network",
        "assigned_team": "Network Support",
        "description": "Multiple users reporting WiFi connectivity problems in Building A. Users cannot connect to the corporate network. This affects approximately 50 employees and is impacting productivity."
    }
    
    success = send_team_assignment_notification(
        ticket_id="TICKET-2024-001",
        ticket_data=ticket_data
    )
    
    if success:
        print("✅ New assignment notification sent successfully!")
    else:
        print("❌ Failed to send new assignment notification")
    
    return success

def test_reassignment():
    """Test notification for a ticket reassignment."""
    print("\n🔄 Testing Ticket Reassignment Notification")
    print("=" * 50)
    
    ticket_data = {
        "subject": "Printer Configuration Error",
        "priority": "MEDIUM",
        "category": "hardware",
        "assigned_team": "Hardware Support",
        "description": "User cannot configure network printer settings. Initial diagnosis suggests hardware compatibility issue rather than software configuration."
    }
    
    success = send_team_assignment_notification(
        ticket_id="TICKET-2024-002",
        ticket_data=ticket_data,
        previous_team="Software Support"
    )
    
    if success:
        print("✅ Reassignment notification sent successfully!")
    else:
        print("❌ Failed to send reassignment notification")
    
    return success

def test_urgent_assignment():
    """Test notification for an urgent ticket assignment."""
    print("\n🚨 Testing Urgent Ticket Assignment Notification")
    print("=" * 50)
    
    ticket_data = {
        "subject": "Critical System Outage - Email Server Down",
        "priority": "URGENT",
        "category": "system",
        "assigned_team": "System Administration",
        "description": "Email server is completely down. No emails can be sent or received. This is affecting the entire organization of 500+ employees. Immediate action required to restore email services."
    }
    
    success = send_team_assignment_notification(
        ticket_id="TICKET-2024-003",
        ticket_data=ticket_data
    )
    
    if success:
        print("✅ Urgent assignment notification sent successfully!")
    else:
        print("❌ Failed to send urgent assignment notification")
    
    return success

def test_low_priority_assignment():
    """Test notification for a low priority ticket assignment."""
    print("\n📝 Testing Low Priority Ticket Assignment Notification")
    print("=" * 50)
    
    ticket_data = {
        "subject": "Request for Additional Software License",
        "priority": "LOW",
        "category": "software",
        "assigned_team": "Software Management",
        "description": "User requests additional license for Adobe Creative Suite. Current license expires next month. This is a routine request for license renewal."
    }
    
    success = send_team_assignment_notification(
        ticket_id="TICKET-2024-004",
        ticket_data=ticket_data
    )
    
    if success:
        print("✅ Low priority assignment notification sent successfully!")
    else:
        print("❌ Failed to send low priority assignment notification")
    
    return success

def main():
    """Run all team assignment notification tests."""
    load_dotenv()
    
    print("🧪 AI Ticket Agent - Team Assignment Notification Test Suite")
    print("=" * 70)
    
    # Check configuration
    config = get_notification_config()
    print(f"🔧 Slack Enabled: {config.slack_enabled}")
    print(f"🔧 Slack Bot Token: {'✅ Set' if config.slack_bot_token else '❌ Not Set'}")
    print(f"🔧 Slack Channel ID: {'✅ Set' if config.slack_channel_id else '❌ Not Set'}")
    print()
    
    if not config.slack_enabled:
        print("❌ Slack notifications are disabled. Please check your configuration.")
        return
    
    # Run tests
    tests = [
        test_new_assignment,
        test_reassignment,
        test_urgent_assignment,
        test_low_priority_assignment
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Results Summary")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All team assignment notification tests passed!")
        print("Check your Slack channel for the test notifications.")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Check the errors above.")
    
    print("\n📋 What to look for in Slack:")
    print("- 📋 New ticket assignment notifications")
    print("- 🔄 Ticket reassignment notifications") 
    print("- 🚨 Urgent ticket notifications")
    print("- 📝 Low priority ticket notifications")
    print("- Interactive buttons for 'View Ticket' and 'Accept Assignment'")

if __name__ == "__main__":
    main() 