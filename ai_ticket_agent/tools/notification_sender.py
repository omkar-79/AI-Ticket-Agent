"""Notification sender tool for sending email updates to users."""

from google.adk.tools import ToolContext
from typing import Dict, Any
from .email_sender import EmailSender


def send_solution_notification(
    user_email: str, 
    problem_description: str, 
    solution_steps: str,
    tool_context: ToolContext
) -> str:
    """
    Send solution notification email to user.
    
    Args:
        user_email: User's email address
        problem_description: The IT problem description
        solution_steps: Solution steps to send
        tool_context: The ADK tool context
        
    Returns:
        Status of email sending
    """
    try:
        email_sender = EmailSender()
        
        subject = f"IT Support Solution: {problem_description[:50]}..."
        
        body = f"""
Dear User,

We have a solution for your IT support request.

**Your Problem:**
{problem_description}

**Solution Steps:**
{solution_steps}

**Next Steps:**
1. Follow the solution steps above
2. If the issue persists, reply to this email
3. We'll escalate your ticket if needed

Thank you for using our IT support service.

Best regards,
AI IT Support Team
        """.strip()
        
        success = email_sender.send_simple_email(
            to_email=user_email,
            subject=subject,
            body=body
        )
        
        if success:
            return f"✅ Solution notification sent successfully to {user_email}"
        else:
            return f"❌ Failed to send solution notification to {user_email}"
            
    except Exception as e:
        return f"❌ Error sending solution notification: {str(e)}"


def send_escalation_notification(
    user_email: str,
    problem_description: str,
    team_assigned: str,
    priority: str,
    tool_context: ToolContext
) -> str:
    """
    Send escalation notification email to user.
    
    Args:
        user_email: User's email address
        problem_description: The IT problem description
        team_assigned: Team assigned to handle the issue
        priority: Priority level
        tool_context: The ADK tool context
        
    Returns:
        Status of email sending
    """
    try:
        email_sender = EmailSender()
        
        subject = f"IT Support Escalated: {problem_description[:50]}..."
        
        body = f"""
Dear User,

Your IT support request has been escalated to our specialized team.

**Your Problem:**
{problem_description}

**Escalation Details:**
- Team Assigned: {team_assigned}
- Priority: {priority.upper()}
- Status: Under investigation

**What This Means:**
- Your issue requires specialized expertise
- Our {team_assigned} team will investigate
- You'll receive updates as we progress
- Expected resolution time based on priority

**Next Steps:**
- Our team will contact you if additional information is needed
- You'll receive updates via email
- For urgent issues, please call our helpdesk

Thank you for your patience.

Best regards,
AI IT Support Team
        """.strip()
        
        success = email_sender.send_simple_email(
            to_email=user_email,
            subject=subject,
            body=body
        )
        
        if success:
            return f"✅ Escalation notification sent successfully to {user_email}"
        else:
            return f"❌ Failed to send escalation notification to {user_email}"
            
    except Exception as e:
        return f"❌ Error sending escalation notification: {str(e)}"


# The tools are just the functions themselves
solution_notification_tool = send_solution_notification
escalation_notification_tool = send_escalation_notification 