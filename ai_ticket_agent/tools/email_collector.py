"""Email collector tool for gathering user contact information."""

from google.adk.tools import ToolContext
from typing import Dict, Any
import re


def collect_user_email(user_message: str, tool_context: ToolContext) -> str:
    """
    Extract or request user email address from their message.
    
    Args:
        user_message: The user's message containing their IT problem
        tool_context: The ADK tool context
        
    Returns:
        Email collection guidance or extracted email
    """
    
    # Check if email is already in the message
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, user_message)
    
    if emails:
        # Email found in message
        user_email = emails[0]
        return f"""
        **Email Address Collected:**
        - Email: {user_email}
        - Status: ✅ Found in user message
        
        **Next Steps:**
        - Store this email for ticket tracking
        - Use for sending solution updates and escalations
        """
    else:
        # No email found, need to request it
        return f"""
        **Email Collection Required:**
        
        User Message: {user_message}
        
        **Action Needed:** The user's message doesn't contain an email address.
        
        **Response Template:**
        "I'd be happy to help you with your IT issue. To provide you with updates and solutions, could you please provide your email address? This will help us track your ticket and send you important updates."
        
        **Email Validation:** Once provided, validate the email format and store it for:
        - Sending solution steps
        - Escalation notifications
        - Ticket status updates
        """


def validate_email_format(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if email format is valid
    """
    email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    return bool(re.match(email_pattern, email))


# The tool is just the function itself
email_collector_tool = collect_user_email 