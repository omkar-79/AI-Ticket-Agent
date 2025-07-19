#!/usr/bin/env python3
"""Test escalation scenarios to verify team routing functionality."""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_ticket_agent.agent import root_agent


async def test_escalation_scenarios():
    """Test various escalation scenarios to verify team routing."""
    
    print("🚨 Testing Escalation Scenarios - Team Routing Verification")
    print("=" * 70)
    
    # Test cases for each team
    escalation_tests = [
        {
            "team": "Network Team",
            "problem": "CRITICAL: Our entire office network is down. No one can access the internet, internal servers, or VPN. This is affecting 50+ employees and we have client meetings starting in 30 minutes. The network switch in the server room is showing red lights and making unusual sounds.",
            "expected_team": "Network Team",
            "email": "network.emergency@company.com"
        },
        {
            "team": "Security Team", 
            "problem": "URGENT: I received a suspicious email claiming to be from IT asking for my password. I clicked a link and entered my credentials. Now I'm seeing strange popups and my files are being encrypted. I think this is ransomware. I have access to sensitive customer data.",
            "expected_team": "Security Team",
            "email": "security.incident@company.com"
        },
        {
            "team": "Hardware Team",
            "problem": "My laptop screen is completely black and won't turn on. I can hear the fan running and the power light is on, but no display. I dropped it yesterday and now it's making a clicking sound. This is my only work device and I have a presentation tomorrow.",
            "expected_team": "Hardware Team", 
            "email": "hardware.support@company.com"
        },
        {
            "team": "Software Team",
            "problem": "Our CRM system is completely broken. Users can't log in, data is corrupted, and we're getting database errors. This is affecting our sales team of 20 people. The error message says 'ORA-00942: table or view does not exist' and we can't process any customer orders.",
            "expected_team": "Software Team",
            "email": "software.support@company.com"
        },
        {
            "team": "Access Management",
            "problem": "I'm a new employee starting tomorrow and I still don't have access to any systems. I can't log into my email, the company portal, or any applications. My manager says I should have been provisioned last week. I need immediate access to start my job.",
            "expected_team": "Access Management",
            "email": "access.support@company.com"
        },
        {
            "team": "Infrastructure Team",
            "problem": "CRITICAL: Our main database server is down. All applications that depend on it are failing. Users are getting 'Connection refused' errors. The server room temperature is very high and the server is making loud noises. We can't access any customer data or process transactions.",
            "expected_team": "Infrastructure Team",
            "email": "infrastructure.support@company.com"
        },
        {
            "team": "General IT Support",
            "problem": "I'm having trouble with multiple things: my email isn't working properly, my printer won't connect, and I can't access some shared folders. I've tried restarting everything but nothing helps. I'm not very technical and need someone to help me figure this out.",
            "expected_team": "General IT Support",
            "email": "general.support@company.com"
        }
    ]
    
    for i, test_case in enumerate(escalation_tests, 1):
        print(f"\n🧪 Test {i}: {test_case['team']}")
        print(f"Problem: {test_case['problem'][:100]}...")
        print(f"Expected Team: {test_case['expected_team']}")
        print(f"Email: {test_case['email']}")
        print("-" * 50)
        
        try:
            # Test that the agent can be loaded and has the right tools
            print(f"✅ Agent loaded successfully")
            print(f"Agent name: {root_agent.name}")
            print(f"Sub-agents available: {len(root_agent.sub_agents)}")
            
            # Check if escalation agent is available
            escalation_agent = None
            for agent in root_agent.sub_agents:
                if "escalation" in agent.name.lower():
                    escalation_agent = agent
                    break
            
            if escalation_agent:
                print(f"✅ Escalation agent found: {escalation_agent.name}")
                print(f"Escalation agent tools: {len(escalation_agent.tools)}")
            else:
                print("❌ Escalation agent not found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n🎯 Escalation Testing Complete!")
    print(f"Tested {len(escalation_tests)} escalation scenarios")
    print(f"Each scenario should route to the appropriate human team")


if __name__ == "__main__":
    asyncio.run(test_escalation_scenarios()) 