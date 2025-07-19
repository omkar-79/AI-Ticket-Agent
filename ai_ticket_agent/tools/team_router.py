"""Team router tool that provides context for LLM-based team assignment."""

from google.adk.tools import ToolContext
from typing import Dict, Any


def route_to_team(problem_description: str, priority: str = "medium", tool_context: ToolContext = None) -> str:
    """
    Provide context and guidance for LLM-based team routing.
    
    Args:
        problem_description: The IT problem description
        priority: Priority level (critical, high, medium, low)
        tool_context: The ADK tool context
        
    Returns:
        Context and guidance for the LLM to assign teams
    """
    
    # Priority-based SLA mapping
    sla_map = {
        "critical": "1 hour",
        "high": "4 hours", 
        "medium": "8 hours",
        "low": "24 hours"
    }
    
    sla = sla_map.get(priority.lower(), "8 hours")
    
    return f"""
    **Team Routing Context:**
    
    Problem Description: {problem_description}
    Priority: {priority.upper()}
    SLA: {sla}
    
    **Available Teams and Their Expertise:**
    
    1. **Network Team** (#it-network-support)
       - VPN issues, connectivity problems, firewall issues
       - Network configuration, bandwidth issues, wireless connectivity
       - Internet connectivity, routing problems
    
    2. **Security Team** (#it-security-support)
       - Security incidents, access violations, suspicious activity
       - Malware, phishing, data breaches, compliance issues
       - Security policy violations, threat assessment
    
    3. **Hardware Team** (#it-hardware-support)
       - Hardware failures, device issues, equipment problems
       - Laptop/desktop repairs, printer/scanner issues, physical damage
       - Device replacement, hardware upgrades
    
    4. **Software Team** (#it-software-support)
       - Application bugs, system errors, software conflicts
       - Installation issues, updates, compatibility problems
       - Software licensing, application support
       - Application database errors (CRM, ERP, business apps)
       - User authentication issues within applications
       - Application-specific functionality problems
    
    5. **Access Management** (#it-access-support)
       - Account creation, permissions, access requests
       - Password resets, user provisioning, role management
       - Identity management, authentication issues
    
    6. **Infrastructure Team** (#it-infrastructure-support)
       - System outages, server hardware issues, infrastructure database problems
       - Cloud services, backup/restore, performance issues
       - System administration, infrastructure maintenance
       - Core infrastructure services (DNS, DHCP, file servers)
       - Physical server and network infrastructure
    
    7. **General IT Support** (#it-general-support)
       - General IT inquiries, basic troubleshooting
       - First-level support, general questions
       - Issues that don't fit specific team categories
    
    **Routing Guidelines:**
    
    - **Software Team**: Application-specific issues (CRM, ERP, business apps), application database errors, user login issues within applications
    - **Infrastructure Team**: Core infrastructure (servers, networks, DNS, DHCP), physical hardware issues, infrastructure-level outages
    - **Network Team**: Network connectivity, VPN, firewall, internet access issues
    - **Security Team**: Security incidents, malware, data breaches, access violations
    - **Hardware Team**: Physical device issues, laptop/desktop hardware, printers, scanners
    - **Access Management**: Account creation, permissions, user provisioning, identity management
    - **General IT Support**: Multiple unrelated issues, general troubleshooting, non-technical users
    
    **Your Task:** Analyze the problem and assign it to the most appropriate team based on the problem description and team expertise. Provide your reasoning for the assignment.
    """


# The tool is just the function itself
team_router_tool = route_to_team 