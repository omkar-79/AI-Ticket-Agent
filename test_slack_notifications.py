#!/usr/bin/env python3
"""Test Slack notification system for IT support tickets."""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_ticket_agent.tools.slack_handlers import (
    escalate_to_slack, 
    get_team_channel, 
    format_slack_message,
    send_slack_notification
)


def test_slack_notifications():
    """Test the Slack notification system."""
    
    print("🔔 Testing Slack Notification System")
    print("=" * 50)
    
    # Test cases for different teams
    test_cases = [
        {
            "team": "Software Team",
            "problem": "Our CRM system is completely broken. Users can't log in, data is corrupted, and we're getting database errors. This is affecting our sales team of 20 people.",
            "user_email": "sales.manager@company.com",
            "priority": "critical"
        },
        {
            "team": "Security Team",
            "problem": "URGENT: I received a suspicious email claiming to be from IT asking for my password. I clicked a link and entered my credentials. Now I'm seeing strange popups and my files are being encrypted.",
            "user_email": "security.incident@company.com",
            "priority": "critical"
        },
        {
            "team": "Hardware Team",
            "problem": "My laptop screen is completely black and won't turn on. I can hear the fan running and the power light is on, but no display. I dropped it yesterday and now it's making a clicking sound.",
            "user_email": "user.support@company.com",
            "priority": "high"
        },
        {
            "team": "Network Team",
            "problem": "CRITICAL: Our entire office network is down. No one can access the internet, internal servers, or VPN. This is affecting 50+ employees and we have client meetings starting in 30 minutes.",
            "user_email": "network.emergency@company.com",
            "priority": "critical"
        },
        {
            "team": "Infrastructure Team",
            "problem": "CRITICAL: Our main database server is down. All applications that depend on it are failing. Users are getting 'Connection refused' errors. The server room temperature is very high.",
            "user_email": "infrastructure.support@company.com",
            "priority": "critical"
        }
    ]
    
    print("🧪 Testing Team Channel Mapping:")
    for test_case in test_cases:
        channel = get_team_channel(test_case["team"])
        print(f"  {test_case['team']} → {channel}")
    
    print(f"\n🧪 Testing Message Formatting:")
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['team']}")
        print(f"Problem: {test_case['problem'][:80]}...")
        print(f"User: {test_case['user_email']}")
        print(f"Priority: {test_case['priority']}")
        
        # Format the message
        message = format_slack_message(
            test_case["team"],
            test_case["problem"],
            test_case["user_email"],
            test_case["priority"]
        )
        
        print(f"Channel: {get_team_channel(test_case['team'])}")
        print(f"Message blocks: {len(message['blocks'])} blocks")
        
        # Show the header text
        header_block = message["blocks"][0]
        if header_block["type"] == "header":
            header_text = header_block["text"]["text"]
            print(f"Header: {header_text}")
    
    print(f"\n🧪 Testing Slack Escalation:")
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['team']}")
        
        # Test escalation
        result = escalate_to_slack(
            team_assignment=test_case["team"],
            problem_description=test_case["problem"],
            user_email=test_case["user_email"],
            priority=test_case["priority"]
        )
        
        # Extract key information from result
        if "Slack Escalation Complete" in result:
            print(f"✅ Success: {test_case['team']}")
        elif "Slack Escalation Simulated" in result:
            print(f"🔄 Simulated: {test_case['team']} (no Slack credentials)")
        elif "Slack Escalation Failed" in result:
            print(f"❌ Failed: {test_case['team']}")
        else:
            print(f"❓ Unknown result for {test_case['team']}")
    
    print(f"\n🎯 Slack Notification Testing Complete!")
    print(f"Tested {len(test_cases)} different team scenarios")
    
    # Check Slack configuration
    print(f"\n📋 Slack Configuration Status:")
    bot_token = os.getenv("SLACK_BOT_TOKEN")
    if bot_token and bot_token != "xoxb-your-slack-bot-token":
        print(f"✅ SLACK_BOT_TOKEN: Configured")
    else:
        print(f"⚠️  SLACK_BOT_TOKEN: Not configured (will simulate)")
    
    try:
        from slack_sdk import WebClient
        print(f"✅ slack_sdk: Installed")
    except ImportError:
        print(f"❌ slack_sdk: Not installed (will simulate)")


if __name__ == "__main__":
    test_slack_notifications() 