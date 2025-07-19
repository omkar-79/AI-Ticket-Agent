"""Knowledge base tool for IT support solutions."""

from google.adk.tools import ToolContext
from typing import Dict, Any


def search_knowledge_base(query: str, tool_context: ToolContext) -> str:
    """
    Search the IT knowledge base for solutions to common problems.
    
    Args:
        query: The user's IT problem or question
        
    Returns:
        Relevant solution or documentation
    """
    # Mock knowledge base - in production, this would connect to a real knowledge base
    knowledge_base = {
        "password reset": """
        **Password Reset Process:**
        1. Go to https://password.company.com
        2. Enter your username
        3. Click "Reset Password"
        4. Check your email for reset link
        5. Create a new password following security requirements
        6. Log in with new password
        
        **Security Requirements:**
        - Minimum 8 characters
        - Include uppercase, lowercase, number, and special character
        - Cannot reuse last 5 passwords
        """,
        
        "vpn connection": """
        **VPN Connection Troubleshooting:**
        1. Check internet connection
        2. Open VPN client application
        3. Enter your username and password
        4. If connection fails:
           - Try different VPN server
           - Check firewall settings
           - Restart VPN client
           - Contact IT if issue persists
        """,
        
        "email setup": """
        **Email Configuration:**
        1. Open email client (Outlook, Thunderbird, etc.)
        2. Add new account
        3. Enter your email address: username@company.com
        4. Server settings:
           - IMAP: mail.company.com (port 993)
           - SMTP: mail.company.com (port 587)
        5. Use your network password
        """,
        
        "printer setup": """
        **Printer Installation:**
        1. Connect printer to network or USB
        2. Download printer driver from manufacturer website
        3. Run installer as administrator
        4. Add printer through Windows Settings
        5. Test print a page
        6. If issues, check printer IP address and network connectivity
        """,
        
        "software installation": """
        **Software Installation Guide:**
        1. Download software from approved sources
        2. Run installer as administrator
        3. Follow installation wizard
        4. Restart computer if prompted
        5. Test the application
        6. Contact IT if installation fails
        """,
        
        "network connectivity": """
        **Network Troubleshooting:**
        1. Check physical connections
        2. Restart network adapter
        3. Run network troubleshooter
        4. Check IP configuration
        5. Test with different network cable
        6. Contact IT if issue persists
        """
    }
    
    # Simple keyword matching - in production, use semantic search
    query_lower = query.lower()
    for key, solution in knowledge_base.items():
        if key in query_lower:
            return solution
    
    return "I don't have a specific solution for this issue in my knowledge base. Let me escalate this to a human team for assistance."


# The tool is just the function itself
knowledge_search_tool = search_knowledge_base 