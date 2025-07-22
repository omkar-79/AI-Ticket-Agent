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
    """
    try:
        email_sender = EmailSender()
        subject = f"IT Support Solution: {problem_description[:50]}..."
        
        # Modern HTML email body
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6fa; color: #222; margin: 0; padding: 0; }}
        .container {{ max-width: 600px; margin: 30px auto; background: #fff; border-radius: 12px; box-shadow: 0 4px 24px rgba(0,0,0,0.07); overflow: hidden; }}
        .header {{ background: linear-gradient(90deg, #007bff 0%, #4CAF50 100%); color: #fff; padding: 32px 24px 20px 24px; text-align: center; }}
        .header h1 {{ margin: 0 0 8px 0; font-size: 2.2rem; letter-spacing: 1px; }}
        .header p {{ margin: 0; font-size: 1.1rem; }}
        .content {{ padding: 32px 24px 24px 24px; }}
        .section {{ background: #f9f9f9; border-radius: 8px; margin-bottom: 24px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.03); }}
        .section h3 {{ margin-top: 0; color: #007bff; }}
        .footer {{ background: #f1f3f6; color: #888; text-align: center; padding: 18px 10px; font-size: 0.95rem; border-top: 1px solid #e0e0e0; }}
        @media (max-width: 650px) {{
            .container, .content, .header {{ padding: 12px !important; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✅ Solution Found</h1>
            <p>Your IT support request has been resolved!</p>
        </div>
        <div class="content">
            <div class="section">
                <h3>Your Problem</h3>
                <p>{problem_description}</p>
            </div>
            <div class="section">
                <h3>Solution Steps</h3>
                <ol>
"""
        for step in solution_steps.split('\n'):
            step = step.strip()
            if step:
                html_body += f"<li>{step}</li>\n"
        html_body += """
                </ol>
            </div>
            <div class="section">
                <h3>Next Steps</h3>
                <ol>
                    <li>Follow the solution steps above</li>
                    <li>If the issue persists, reply to this email</li>
                    <li>We'll escalate your ticket if needed</li>
                </ol>
            </div>
            <div class="section">
                <p>Thank you for using our IT support service.</p>
                <p>Best regards,<br>AI IT Support Team</p>
            </div>
        </div>
        <div class="footer">
            This is an automated response. For urgent issues, please call our helpdesk at 1-800-IT-SUPPORT.
        </div>
    </div>
</body>
</html>
        """.strip()
        
        # Plain text body (same as before)
        body = f"""
Dear User,

We have a solution for your IT support request.

Your Problem:
{problem_description}

Solution Steps:
{solution_steps}

Next Steps:
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
            body=body,
            html_body=html_body
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
    """
    try:
        email_sender = EmailSender()
        subject = f"IT Support Escalated: {problem_description[:50]}..."
        
        # Modern HTML email body
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6fa; color: #222; margin: 0; padding: 0; }}
        .container {{ max-width: 600px; margin: 30px auto; background: #fff; border-radius: 12px; box-shadow: 0 4px 24px rgba(0,0,0,0.07); overflow: hidden; }}
        .header {{ background: linear-gradient(90deg, #007bff 0%, #FF9800 100%); color: #fff; padding: 32px 24px 20px 24px; text-align: center; }}
        .header h1 {{ margin: 0 0 8px 0; font-size: 2.2rem; letter-spacing: 1px; }}
        .header p {{ margin: 0; font-size: 1.1rem; }}
        .content {{ padding: 32px 24px 24px 24px; }}
        .section {{ background: #f9f9f9; border-radius: 8px; margin-bottom: 24px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.03); }}
        .section h3 {{ margin-top: 0; color: #FF9800; }}
        .footer {{ background: #f1f3f6; color: #888; text-align: center; padding: 18px 10px; font-size: 0.95rem; border-top: 1px solid #e0e0e0; }}
        @media (max-width: 650px) {{
            .container, .content, .header {{ padding: 12px !important; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚩 Ticket Escalated</h1>
            <p>Your IT support request has been escalated to our specialized team.</p>
        </div>
        <div class="content">
            <div class="section">
                <h3>Your Problem</h3>
                <p>{problem_description}</p>
            </div>
            <div class="section">
                <h3>Escalation Details</h3>
                <ul>
                    <li><b>Team Assigned:</b> {team_assigned}</li>
                    <li><b>Priority:</b> {priority.upper()}</li>
                    <li><b>Status:</b> Under investigation</li>
                </ul>
            </div>
            <div class="section">
                <h3>What This Means</h3>
                <ul>
                    <li>Your issue requires specialized expertise</li>
                    <li>Our {team_assigned} team will investigate</li>
                    <li>You'll receive updates as we progress</li>
                    <li>Expected resolution time based on priority</li>
                </ul>
            </div>
            <div class="section">
                <h3>Next Steps</h3>
                <ol>
                    <li>Our team will contact you if additional information is needed</li>
                    <li>You'll receive updates via email</li>
                    <li>For urgent issues, please call our helpdesk</li>
                </ol>
                <p>Thank you for your patience.</p>
                <p>Best regards,<br>AI IT Support Team</p>
            </div>
        </div>
        <div class="footer">
            This is an automated response. For urgent issues, please call our helpdesk at 1-800-IT-SUPPORT.
        </div>
    </div>
</body>
</html>
        """.strip()
        
        # Plain text body (same as before)
        body = f"""
Dear User,

Your IT support request has been escalated to our specialized team.

Your Problem:
{problem_description}

Escalation Details:
- Team Assigned: {team_assigned}
- Priority: {priority.upper()}
- Status: Under investigation

What This Means:
- Your issue requires specialized expertise
- Our {team_assigned} team will investigate
- You'll receive updates as we progress
- Expected resolution time based on priority

Next Steps:
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
            body=body,
            html_body=html_body
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
