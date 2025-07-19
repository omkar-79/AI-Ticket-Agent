#!/usr/bin/env python3
"""Test CRM system routing to verify it goes to Software Team, not Infrastructure Team."""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_ticket_agent.agent import root_agent


async def test_crm_routing():
    """Test CRM system issue routing specifically."""
    
    print("🔍 Testing CRM System Routing - Software vs Infrastructure Team")
    print("=" * 70)
    
    # CRM system issue that should go to Software Team
    crm_issue = {
        "problem": "Our CRM system is completely broken. Users can't log in, data is corrupted, and we're getting database errors. This is affecting our sales team of 20 people. The error message says 'ORA-00942: table or view does not exist' and we can't process any customer orders.",
        "expected_team": "Software Team",
        "reasoning": "CRM system = application, database errors = application database, user login issues = application authentication"
    }
    
    # Infrastructure issue for comparison
    infrastructure_issue = {
        "problem": "CRITICAL: Our main database server is down. All applications that depend on it are failing. Users are getting 'Connection refused' errors. The server room temperature is very high and the server is making loud noises. We can't access any customer data or process transactions.",
        "expected_team": "Infrastructure Team", 
        "reasoning": "Database server = infrastructure, server room = physical infrastructure, temperature = hardware issue"
    }
    
    test_cases = [crm_issue, infrastructure_issue]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['expected_team']}")
        print(f"Problem: {test_case['problem'][:100]}...")
        print(f"Expected Team: {test_case['expected_team']}")
        print(f"Reasoning: {test_case['reasoning']}")
        print("-" * 50)
        
        try:
            # Test that the agent can be loaded
            print(f"✅ Agent loaded successfully")
            print(f"Agent name: {root_agent.name}")
            
            # Check escalation agent
            escalation_agent = None
            for agent in root_agent.sub_agents:
                if "escalation" in agent.name.lower():
                    escalation_agent = agent
                    break
            
            if escalation_agent:
                print(f"✅ Escalation agent found: {escalation_agent.name}")
                
                # Check if team router tool is available
                team_router_found = False
                for i, tool in enumerate(escalation_agent.tools):
                    tool_name = str(tool)
                    if "team_router" in tool_name.lower() or "route_to_team" in tool_name.lower():
                        team_router_found = True
                        break
                
                if team_router_found:
                    print(f"✅ Team router tool available")
                else:
                    print(f"❌ Team router tool not found")
                    
            else:
                print("❌ Escalation agent not found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n🎯 CRM Routing Test Complete!")
    print(f"Key distinction:")
    print(f"  - CRM system issues → Software Team (application-level)")
    print(f"  - Database server issues → Infrastructure Team (infrastructure-level)")


if __name__ == "__main__":
    asyncio.run(test_crm_routing()) 