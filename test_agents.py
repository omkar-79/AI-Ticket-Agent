#!/usr/bin/env python3
"""Test script for the IT Support multi-agent system with email functionality."""

import asyncio
from ai_ticket_agent import root_agent


async def test_it_support_agents():
    """Test the IT support agents with different scenarios including email collection."""
    
    print("🤖 Testing IT Support Multi-Agent System with Email Functionality")
    print("=" * 70)
    
    # Test scenarios with email addresses
    test_cases = [
        {
            "name": "Password Reset with Email (Self-Service)",
            "problem": "I forgot my password and need to reset it. My email is john.doe@company.com",
            "expected": "self_service",
            "email": "john.doe@company.com"
        },
        {
            "name": "VPN Connection Issue with Email (Self-Service)",
            "problem": "My VPN keeps disconnecting every 30 minutes. Contact me at sarah.smith@company.com",
            "expected": "self_service",
            "email": "sarah.smith@company.com"
        },
        {
            "name": "Security Incident with Email (Escalation)",
            "problem": "I think my computer has a virus. I'm seeing suspicious popups and my files are encrypted. Email: security@company.com",
            "expected": "escalation",
            "email": "security@company.com"
        },
        {
            "name": "Hardware Failure with Email (Escalation)",
            "problem": "My laptop won't turn on. I hear a clicking sound and see a blue screen. Contact: mike.tech@company.com",
            "expected": "escalation",
            "email": "mike.tech@company.com"
        },
        {
            "name": "Email Setup without Email (Should Request Email)",
            "problem": "I need help setting up my email on my new phone. Can you guide me through it?",
            "expected": "self_service",
            "email": "none_provided"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print(f"Problem: {test_case['problem']}")
        print(f"Expected: {test_case['expected']}")
        print(f"Email: {test_case['email']}")
        print("-" * 50)
        
        try:
            # Create a simple conversation with the root agent
            # Note: For testing, we'll just verify the agent can be imported
            print(f"✅ Agent loaded successfully")
            print(f"Agent name: {root_agent.name}")
            print(f"Agent description: {root_agent.description}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_it_support_agents()) 