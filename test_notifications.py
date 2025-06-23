#!/usr/bin/env python3
"""
Test script for Slack notifications in AI Ticket Agent.
Run this script to test if your Slack configuration is working.
"""

import os
from dotenv import load_dotenv
from ai_ticket_agent.tools.notifications import (
    send_slack_notification,
    send_notification,
    get_notification_config
)

def test_slack_config():
    """Test Slack configuration and send a test notification."""
    
    # Load environment variables
    load_dotenv()
    
    print("🔧 Testing Slack Notification Configuration")
    print("=" * 50)
    
    # Check configuration
    config = get_notification_config()
    print(f"Slack Enabled: {config.slack_enabled}")
    print(f"Slack Bot Token: {'✅ Set' if config.slack_bot_token else '❌ Not set'}")
    print(f"Slack Channel ID: {'✅ Set' if config.slack_channel_id else '❌ Not set'}")
    
    if not config.slack_enabled:
        print("\n❌ Slack notifications are disabled!")
        print("Please set SLACK_BOT_TOKEN in your .env file")
        return False
    
    # Test basic Slack notification
    print("\n📤 Sending test Slack notification...")
    
    test_message = "🧪 This is a test notification from AI Ticket Agent!"
    
    success = send_slack_notification(
        channel=config.slack_channel_id,
        message=test_message
    )
    
    if success:
        print("✅ Slack notification sent successfully!")
        print(f"Channel: {config.slack_channel_id}")
        print(f"Message: {test_message}")
    else:
        print("❌ Failed to send Slack notification")
    
    return success

def test_ticket_notification():
    """Test a ticket-specific notification."""
    
    print("\n🎫 Testing Ticket Notification")
    print("=" * 30)
    
    # Test ticket creation notification
    ticket_data = {
        "subject": "Test WiFi Issue",
        "priority": "medium",
        "category": "network",
        "status": "open",
        "description": "User cannot connect to WiFi network",
        "assigned_team": "Network Support"
    }
    
    test_message = f"""
🚨 New Ticket Created

**Subject:** {ticket_data['subject']}
**Priority:** {ticket_data['priority'].upper()}
**Category:** {ticket_data['category']}
**Status:** {ticket_data['status']}
**Assigned Team:** {ticket_data['assigned_team']}

**Description:**
{ticket_data['description']}

Please review and take appropriate action.
    """.strip()
    
    config = get_notification_config()
    
    success = send_slack_notification(
        channel=config.slack_channel_id,
        message=test_message
    )
    
    if success:
        print("✅ Ticket notification sent successfully!")
    else:
        print("❌ Failed to send ticket notification")
    
    return success

def test_sla_alert():
    """Test an SLA alert notification."""
    
    print("\n⏰ Testing SLA Alert")
    print("=" * 20)
    
    sla_data = {
        "sla_target": "4 hours",
        "time_elapsed": "3.5 hours",
        "time_remaining": "30 minutes",
        "priority": "high"
    }
    
    alert_message = f"""
⚠️ SLA WARNING ⚠️

**Ticket:** TICKET-20250622-TEST123
**SLA Target:** {sla_data['sla_target']}
**Time Elapsed:** {sla_data['time_elapsed']}
**Time Remaining:** {sla_data['time_remaining']}
**Priority:** {sla_data['priority'].upper()}

🚨 This ticket is approaching its SLA target!
Please review and take action if needed.
    """.strip()
    
    config = get_notification_config()
    
    success = send_slack_notification(
        channel=config.slack_channel_id,
        message=alert_message
    )
    
    if success:
        print("✅ SLA alert sent successfully!")
    else:
        print("❌ Failed to send SLA alert")
    
    return success

def main():
    """Main test function."""
    print("🧪 AI Ticket Agent - Notification Test Suite")
    print("=" * 50)
    
    # Test 1: Basic configuration
    config_ok = test_slack_config()
    
    if not config_ok:
        print("\n❌ Cannot proceed with tests due to configuration issues.")
        return
    
    # Test 2: Ticket notification
    test_ticket_notification()
    
    # Test 3: SLA alert
    test_sla_alert()
    
    print("\n✅ All notification tests completed!")
    print("Check your Slack channel for the test messages.")

if __name__ == "__main__":
    main() 