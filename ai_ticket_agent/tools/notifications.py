"""Notification tools for the AI Ticket Agent."""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
import re


class NotificationConfig(BaseModel):
    """Notification configuration."""
    
    email_enabled: bool = Field(description="Whether email notifications are enabled")
    slack_enabled: bool = Field(description="Whether Slack notifications are enabled")
    smtp_host: str = Field(description="SMTP server host")
    smtp_port: int = Field(description="SMTP server port")
    smtp_username: str = Field(description="SMTP username")
    smtp_password: str = Field(description="SMTP password")
    slack_bot_token: str = Field(description="Slack bot token")
    slack_channel_id: str = Field(description="Slack channel ID")


class EmailNotification(BaseModel):
    """Email notification details."""
    
    to_email: str = Field(description="Recipient email address")
    subject: str = Field(description="Email subject")
    body: str = Field(description="Email body content")
    html_body: Optional[str] = Field(description="HTML email body")
    attachments: List[str] = Field(description="List of attachment file paths")


class SlackNotification(BaseModel):
    """Slack notification details."""
    
    channel: str = Field(description="Slack channel")
    message: str = Field(description="Message text")
    blocks: Optional[List[Dict[str, Any]]] = Field(description="Slack blocks for rich formatting")
    attachments: Optional[List[Dict[str, Any]]] = Field(description="Slack attachments")


def get_notification_config() -> NotificationConfig:
    """Get notification configuration from environment variables."""
    load_dotenv()
    
    return NotificationConfig(
        email_enabled=os.getenv("SMTP_HOST") is not None,
        slack_enabled=os.getenv("SLACK_BOT_TOKEN") is not None,
        smtp_host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_username=os.getenv("SMTP_USERNAME", ""),
        smtp_password=os.getenv("SMTP_PASSWORD", ""),
        slack_bot_token=os.getenv("SLACK_BOT_TOKEN", ""),
        slack_channel_id=os.getenv("SLACK_CHANNEL_ID", "")
    )


def send_email_notification(
    to_email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None
) -> bool:
    """
    Send an email notification.
    
    Args:
        to_email: The recipient email address
        subject: The email subject
        body: The email body content
        html_body: Optional HTML email body
        
    Returns:
        bool: True if email was sent successfully
    """
    config = get_notification_config()
    
    print(f"🔍 DEBUG: Attempting to send email notification")
    print(f"📧 To: {to_email}")
    print(f"📝 Subject: {subject}")
    print(f"⚙️ Email enabled: {config.email_enabled}")
    
    if not config.email_enabled:
        print(f"❌ Email notification disabled. Would send to {to_email}: {subject}")
        return True
    
    if not config.smtp_username or not config.smtp_password:
        print(f"❌ SMTP credentials not configured")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = config.smtp_username
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add text and HTML parts
        text_part = MIMEText(body, 'plain')
        msg.attach(text_part)
        
        if html_body:
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
        
        print(f"🔌 Connecting to SMTP server: {config.smtp_host}:{config.smtp_port}")
        
        # Send email
        with smtplib.SMTP(config.smtp_host, config.smtp_port) as server:
            server.starttls()
            print(f"🔐 Logging in with username: {config.smtp_username}")
            server.login(config.smtp_username, config.smtp_password)
            print(f"📤 Sending email...")
            server.send_message(msg)
        
        print(f"✅ Email notification sent successfully to {to_email}: {subject}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email notification: {e}")
        print(f"🔍 DEBUG: SMTP Host: {config.smtp_host}")
        print(f"🔍 DEBUG: SMTP Port: {config.smtp_port}")
        print(f"🔍 DEBUG: SMTP Username: {config.smtp_username}")
        return False


def send_slack_notification(
    channel: str,
    message: str,
    blocks: Optional[List[Dict[str, Any]]] = None
) -> bool:
    """
    Send a Slack notification.
    
    Args:
        channel: The Slack channel
        message: The message text
        blocks: Optional Slack blocks for rich formatting
        
    Returns:
        bool: True if notification was sent successfully
    """
    config = get_notification_config()
    
    if not config.slack_enabled:
        print(f"Slack notification disabled. Would send to {channel}: {message}")
        return True
    
    if not config.slack_bot_token or not config.slack_channel_id:
        print("❌ Slack bot token or channel ID not set. Cannot send Slack notification.")
        return False

    client = WebClient(token=config.slack_bot_token)
    try:
        response = client.chat_postMessage(
            channel=channel,
            text=message,
            blocks=blocks if blocks else None
        )
        if response["ok"]:
            print(f"✅ Slack notification sent to {channel}: {message}")
            return True
        else:
            print(f"❌ Failed to send Slack notification: {response['error']}")
            return False
    except SlackApiError as e:
        print(f"❌ Slack API error: {e.response['error']}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error sending Slack notification: {e}")
        return False


def send_ticket_notification(
    ticket_id: str,
    notification_type: str,
    recipients: List[str],
    ticket_data: Dict[str, Any]
) -> bool:
    """
    Send a ticket-specific notification.
    
    Args:
        ticket_id: The ticket identifier
        notification_type: The type of notification
        recipients: List of recipient email addresses
        ticket_data: Ticket data for the notification
        
    Returns:
        bool: True if notifications were sent successfully
    """
    # Create notification content based on type
    notification_templates = {
        "created": {
            "subject": f"New IT Support Ticket Created - {ticket_id}",
            "body": f"""
A new IT support ticket has been created.

Ticket ID: {ticket_id}
Subject: {ticket_data.get('subject', 'N/A')}
Priority: {ticket_data.get('priority', 'N/A')}
Category: {ticket_data.get('category', 'N/A')}
Status: {ticket_data.get('status', 'N/A')}

Description:
{ticket_data.get('description', 'N/A')}

This ticket has been assigned to: {ticket_data.get('assigned_team', 'Unassigned')}
            """.strip()
        },
        "updated": {
            "subject": f"IT Support Ticket Updated - {ticket_id}",
            "body": f"""
An IT support ticket has been updated.

Ticket ID: {ticket_id}
Subject: {ticket_data.get('subject', 'N/A')}
Current Status: {ticket_data.get('status', 'N/A')}
Priority: {ticket_data.get('priority', 'N/A')}

Latest Update:
{ticket_data.get('latest_update', 'N/A')}
            """.strip()
        },
        "escalated": {
            "subject": f"IT Support Ticket Escalated - {ticket_id}",
            "body": f"""
An IT support ticket has been escalated.

Ticket ID: {ticket_id}
Subject: {ticket_data.get('subject', 'N/A')}
Escalation Reason: {ticket_data.get('escalation_reason', 'N/A')}
New Team: {ticket_data.get('assigned_team', 'N/A')}

This ticket requires immediate attention.
            """.strip()
        },
        "resolved": {
            "subject": f"IT Support Ticket Resolved - {ticket_id}",
            "body": f"""
An IT support ticket has been resolved.

Ticket ID: {ticket_id}
Subject: {ticket_data.get('subject', 'N/A')}
Resolution: {ticket_data.get('resolution', 'N/A')}
Resolution Time: {ticket_data.get('resolution_time', 'N/A')}

Thank you for using our IT support service.
            """.strip()
        }
    }
    
    template = notification_templates.get(notification_type, notification_templates["updated"])
    
    # Send to all recipients
    success_count = 0
    for recipient in recipients:
        if send_email_notification(
            to_email=recipient,
            subject=template["subject"],
            body=template["body"]
        ):
            success_count += 1
    
    return success_count == len(recipients)


def send_sla_alert(
    ticket_id: str,
    alert_type: str,
    sla_data: Dict[str, Any]
) -> bool:
    """
    Send an SLA alert notification.
    
    Args:
        ticket_id: The ticket identifier
        alert_type: The type of SLA alert
        sla_data: SLA data for the alert
        
    Returns:
        bool: True if alert was sent successfully
    """
    config = get_notification_config()
    
    # Create alert message
    if alert_type == "breach":
        subject = f"SLA BREACH ALERT - Ticket {ticket_id}"
        message = f"""
🚨 SLA BREACH ALERT 🚨

Ticket {ticket_id} has breached its SLA target.

SLA Target: {sla_data.get('sla_target', 'N/A')}
Time Elapsed: {sla_data.get('time_elapsed', 'N/A')}
Priority: {sla_data.get('priority', 'N/A')}

IMMEDIATE ACTION REQUIRED
        """.strip()
    else:
        subject = f"SLA Warning - Ticket {ticket_id}"
        message = f"""
⚠️ SLA WARNING ⚠️

Ticket {ticket_id} is approaching its SLA target.

SLA Target: {sla_data.get('sla_target', 'N/A')}
Time Elapsed: {sla_data.get('time_elapsed', 'N/A')}
Time Remaining: {sla_data.get('time_remaining', 'N/A')}
Priority: {sla_data.get('priority', 'N/A')}

Please review and take action if needed.
        """.strip()
    
    # Send to management and assigned team
    recipients = [
        "it-manager@company.com",
        "helpdesk-supervisor@company.com"
    ]
    
    if sla_data.get('assigned_team'):
        team_email = f"{sla_data['assigned_team'].lower().replace(' ', '-')}@company.com"
        recipients.append(team_email)
    
    # Send email notifications
    email_success = send_ticket_notification(
        ticket_id=ticket_id,
        notification_type="escalated" if alert_type == "breach" else "updated",
        recipients=recipients,
        ticket_data={
            "subject": f"SLA {alert_type.upper()} - {ticket_id}",
            "latest_update": message
        }
    )
    
    # Send Slack notification
    slack_success = send_slack_notification(
        channel=config.slack_channel_id,
        message=message
    )
    
    return email_success and slack_success


def send_team_assignment_notification(
    ticket_id: str,
    ticket_data: Dict[str, Any],
    previous_team: Optional[str] = None
) -> bool:
    """
    Send a Slack notification when a ticket is assigned to a team.
    
    Args:
        ticket_id: The ticket identifier
        ticket_data: Ticket data including assignment details
        previous_team: The previous team (if this is a reassignment)
        
    Returns:
        bool: True if notification was sent successfully
    """
    config = get_notification_config()
    
    if not config.slack_enabled:
        print(f"Slack notification disabled. Would send team assignment notification for {ticket_id}")
        return True
    
    assigned_team = ticket_data.get('assigned_team', 'Unassigned')
    priority = ticket_data.get('priority', 'MEDIUM')
    category = ticket_data.get('category', 'general')
    subject = ticket_data.get('subject', 'No subject')
    description = ticket_data.get('description', 'No description')
    
    # Determine notification type
    if previous_team and previous_team != assigned_team:
        notification_type = "reassigned"
        title = f"🔄 Ticket Reassigned: {ticket_id}"
        color = "#FF8C00"  # Orange for reassignment
    else:
        notification_type = "assigned"
        title = f"📋 New Ticket Assigned: {ticket_id}"
        color = "#36A64F"  # Green for new assignment
    
    # Create rich Slack blocks
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": title,
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Ticket ID:*\n`{ticket_id}`"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Priority:*\n{priority}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Category:*\n{category}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Assigned Team:*\n{assigned_team}"
                }
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Subject:*\n{subject}"
            }
        }
    ]
    
    # Add description if it's not too long
    if description and len(description) < 2000:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Description:*\n{description}"
            }
        })
    
    # Add reassignment info if applicable
    if notification_type == "reassigned":
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"🔄 Reassigned from *{previous_team}* to *{assigned_team}*"
                }
            ]
        })
    
    # Add action buttons
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "View Ticket",
                    "emoji": True
                },
                "style": "primary",
                "value": ticket_id,
                "action_id": f"view_ticket_{ticket_id}"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Accept Assignment",
                    "emoji": True
                },
                "style": "primary",
                "value": ticket_id,
                "action_id": f"accept_assignment_{ticket_id}"
            }
        ]
    })
    
    # Create the message text (fallback for notifications)
    message = f"""
+{title}
+
+**Subject:** {subject}
+**Priority:** {priority}
+**Category:** {category}
+**Assigned Team:** {assigned_team}
+
+**Description:**
+{description[:200]}{'...' if len(description) > 200 else ''}
+    """.strip()
    
    # Send the notification
    success = send_slack_notification(
        channel=config.slack_channel_id,
        message=message,
        blocks=blocks
    )
    
    if success:
        print(f"✅ Team assignment notification sent for ticket {ticket_id} to {assigned_team}")
    else:
        print(f"❌ Failed to send team assignment notification for ticket {ticket_id}")
    
    return success


def send_notification(
    recipient: str,
    subject: str,
    message: str,
    notification_type: str = "email",
    priority: str = "normal"
) -> bool:
    """
    Send a notification using the specified method.
    
    Args:
        recipient: The recipient (email address or Slack channel)
        subject: The notification subject/title
        message: The notification message
        notification_type: The type of notification ("email" or "slack")
        priority: The priority level ("low", "normal", "high", "urgent")
        
    Returns:
        bool: True if notification was sent successfully
    """
    if notification_type.lower() == "email":
        return send_email_notification(
            to_email=recipient,
            subject=subject,
            body=message
        )
    elif notification_type.lower() == "slack":
        return send_slack_notification(
            channel=recipient,
            message=f"*{subject}*\n{message}"
        )
    else:
        print(f"Unknown notification type: {notification_type}")
        return False


def draft_and_send_ticket_email(
    ticket_id: str,
    user_email: str,
    email_type: str,
    ticket_data: Dict[str, Any],
    solution_data: Optional[Dict[str, Any]] = None,
    assignment_data: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Draft and send a professional email to the user based on ticket status.
    
    Args:
        ticket_id: The ticket identifier
        user_email: The user's email address
        email_type: Type of email ("solution_found", "team_assigned", "escalated")
        ticket_data: Basic ticket information
        solution_data: Knowledge base solution data (for solution_found emails)
        assignment_data: Team assignment data (for team_assigned emails)
        
    Returns:
        bool: True if email was sent successfully
    """
    print(f"🔍 DEBUG: Starting email draft and send process")
    print(f"🎫 Ticket ID: {ticket_id}")
    print(f"📧 User Email: {user_email}")
    print(f"📝 Email Type: {email_type}")
    print(f"📋 Ticket Data: {ticket_data}")
    
    config = get_notification_config()
    
    if not config.email_enabled:
        print(f"❌ Email notifications disabled. Would send {email_type} email to {user_email}")
        return True
    
    # Create email content based on type
    print(f"📝 Creating email content for type: {email_type}")
    if email_type == "solution_found":
        subject, body, html_body = _create_solution_email(ticket_id, ticket_data, solution_data)
    elif email_type == "team_assigned":
        subject, body, html_body = _create_assignment_email(ticket_id, ticket_data, assignment_data)
    elif email_type == "escalated":
        subject, body, html_body = _create_escalation_email(ticket_id, ticket_data, assignment_data)
    else:
        print(f"❌ Unknown email type: {email_type}")
        return False
    
    print(f"📧 Email content created:")
    print(f"   Subject: {subject}")
    print(f"   Body length: {len(body)} characters")
    print(f"   HTML body length: {len(html_body) if html_body else 0} characters")
    
    # Send the email
    success = send_email_notification(
        to_email=user_email,
        subject=subject,
        body=body,
        html_body=html_body
    )
    
    if success:
        print(f"✅ {email_type} email sent successfully to {user_email} for ticket {ticket_id}")
    else:
        print(f"❌ Failed to send {email_type} email to {user_email} for ticket {ticket_id}")
    
    return success


def _markdown_to_html_sections(md_text: str) -> str:
    """Convert markdown-like solution text to HTML with headings and lists."""
    html = ""
    lines = md_text.split('\n')
    in_ul = False
    for line in lines:
        line = line.strip()
        if not line:
            if in_ul:
                html += '</ul>'
                in_ul = False
            continue
        if line.startswith('# '):
            if in_ul:
                html += '</ul>'
                in_ul = False
            html += f'<h2>{line[2:].strip()}</h2>'
        elif line.startswith('## '):
            if in_ul:
                html += '</ul>'
                in_ul = False
            html += f'<h3>{line[3:].strip()}</h3>'
        elif line.startswith('### '):
            if in_ul:
                html += '</ul>'
                in_ul = False
            html += f'<h4>{line[4:].strip()}</h4>'
        elif re.match(r'\*\*.*\*\*', line):
            if in_ul:
                html += '</ul>'
                in_ul = False
            html += f'<b>{line.replace("**", "")}</b><br>'
        elif re.match(r'\d+\. ', line):
            if not in_ul:
                html += '<ul>'
                in_ul = True
            html += f'<li>{line[3:].strip()}</li>'
        elif line.startswith('- '):
            if not in_ul:
                html += '<ul>'
                in_ul = True
            html += f'<li>{line[2:].strip()}</li>'
        else:
            if in_ul:
                html += '</ul>'
                in_ul = False
            html += f'<p>{line}</p>'
    if in_ul:
        html += '</ul>'
    return html


def _create_solution_email(
    ticket_id: str,
    ticket_data: Dict[str, Any],
    solution_data: Dict[str, Any]
) -> tuple[str, str, str]:
    """Create email content for when a solution is found in knowledge base."""
    subject = f"Solution Found - Ticket {ticket_id}: {ticket_data.get('subject', 'IT Support Request')}"
    # Plain text body (unchanged)
    body = f"""
Dear {ticket_data.get('user_name', 'Valued Customer')},

Good news! We found a solution for your IT support request.

Ticket ID: {ticket_id}
Subject: {ticket_data.get('subject', 'N/A')}
Priority: {ticket_data.get('priority', 'N/A')}

SOLUTION:
{solution_data.get('response_text', 'No solution text provided')}

STEP-BY-STEP INSTRUCTIONS:
"""
    for i, step in enumerate(solution_data.get('solution_steps', []), 1):
        body += f"{i}. {step}\n"
    body += f"""

If these steps don't resolve your issue, please reply to this email and we'll escalate your ticket to a specialist.

Additional Resources:
"""
    for article in solution_data.get('related_articles', []):
        body += f"- {article}\n"
    body += f"""

Thank you for using our IT support service.

Best regards,
IT Support Team

---
This is an automated response. For urgent issues, please call our helpdesk at 1-800-IT-SUPPORT.
    """.strip()

    # HTML body (improved)
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset=\"UTF-8\">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .ticket-info {{ background-color: #f9f9f9; padding: 15px; border-left: 4px solid #4CAF50; margin: 20px 0; }}
        .solution {{ background-color: #e8f5e8; padding: 15px; border-left: 4px solid #4CAF50; margin: 20px 0; }}
        .steps {{ background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; }}
        .footer {{ background-color: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
        .button {{ background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }}
        h2, h3, h4 {{ margin-bottom: 0.5em; }}
        ul, ol {{ margin-top: 0.5em; margin-bottom: 0.5em; }}
    </style>
</head>
<body>
    <div class=\"header\">
        <h1>✅ Solution Found</h1>
        <p>Your IT support request has been resolved!</p>
    </div>
    <div class=\"content\">
        <p>Dear {ticket_data.get('user_name', 'Valued Customer')},</p>
        <p>Good news! We found a solution for your IT support request.</p>
        <div class=\"ticket-info\">
            <strong>Ticket ID:</strong> {ticket_id}<br>
            <strong>Subject:</strong> {ticket_data.get('subject', 'N/A')}<br>
            <strong>Priority:</strong> {ticket_data.get('priority', 'N/A')}
        </div>
        <div class=\"solution\">
            <h2>Solution: {solution_data.get('related_articles', [''])[0]}</h2>
            {_markdown_to_html_sections(solution_data.get('response_text', 'No solution text provided'))}
        </div>
        <div class=\"steps\">
            <h3>Step-by-Step Instructions:</h3>
            <ol>
"""
    for step in solution_data.get('solution_steps', []):
        html_body += f"                <li>{step}</li>\n"
    html_body += f"""
            </ol>
        </div>
        <p><strong>Additional Resources:</strong></p>
        <ul>
"""
    for article in solution_data.get('related_articles', []):
        html_body += f"            <li>{article}</li>\n"
    html_body += f"""
        </ul>
        <p>If these steps don't resolve your issue, please reply to this email and we'll escalate your ticket to a specialist.</p>
        <p>Thank you for using our IT support service.</p>
        <p>Best regards,<br>IT Support Team</p>
    </div>
    <div class=\"footer\">
        <p>This is an automated response. For urgent issues, please call our helpdesk at 1-800-IT-SUPPORT.</p>
    </div>
</body>
</html>
    """.strip()
    return subject, body, html_body


def _create_assignment_email(
    ticket_id: str,
    ticket_data: Dict[str, Any],
    assignment_data: Dict[str, Any]
) -> tuple[str, str, str]:
    """Create email content for when a ticket is assigned to a team."""
    
    subject = f"Ticket Assigned - {ticket_id}: {ticket_data.get('subject', 'IT Support Request')}"
    
    # Plain text body
    body = f"""
Dear {ticket_data.get('user_name', 'Valued Customer')},

Your IT support request has been received and assigned to our specialized team.

Ticket ID: {ticket_id}
Subject: {ticket_data.get('subject', 'N/A')}
Priority: {ticket_data.get('priority', 'N/A')}
Category: {ticket_data.get('category', 'N/A')}

ASSIGNMENT DETAILS:
Assigned Team: {assignment_data.get('team', 'N/A')}
Expected Response Time: {assignment_data.get('estimated_response_time', 'N/A')}
SLA Target: {assignment_data.get('sla_target', 'N/A')}

Our {assignment_data.get('team', 'specialized team')} will review your request and provide a solution within the specified timeframe.

You will receive updates on your ticket status via email. If you have any urgent questions, please reply to this email.

Thank you for your patience.

Best regards,
IT Support Team

---
This is an automated response. For urgent issues, please call our helpdesk at 1-800-IT-SUPPORT.
    """.strip()
    
    # HTML body
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .ticket-info {{ background-color: #f9f9f9; padding: 15px; border-left: 4px solid #007bff; margin: 20px 0; }}
        .assignment {{ background-color: #e3f2fd; padding: 15px; border-left: 4px solid #007bff; margin: 20px 0; }}
        .footer {{ background-color: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📋 Ticket Assigned</h1>
        <p>Your IT support request has been assigned to our specialized team</p>
    </div>
    
    <div class="content">
        <p>Dear {ticket_data.get('user_name', 'Valued Customer')},</p>
        
        <p>Your IT support request has been received and assigned to our specialized team.</p>
        
        <div class="ticket-info">
            <strong>Ticket ID:</strong> {ticket_id}<br>
            <strong>Subject:</strong> {ticket_data.get('subject', 'N/A')}<br>
            <strong>Priority:</strong> {ticket_data.get('priority', 'N/A')}<br>
            <strong>Category:</strong> {ticket_data.get('category', 'N/A')}
        </div>
        
        <div class="assignment">
            <h3>Assignment Details:</h3>
            <p><strong>Assigned Team:</strong> {assignment_data.get('team', 'N/A')}</p>
            <p><strong>Expected Response Time:</strong> {assignment_data.get('estimated_response_time', 'N/A')}</p>
            <p><strong>SLA Target:</strong> {assignment_data.get('sla_target', 'N/A')}</p>
        </div>
        
        <p>Our {assignment_data.get('team', 'specialized team')} will review your request and provide a solution within the specified timeframe.</p>
        
        <p>You will receive updates on your ticket status via email. If you have any urgent questions, please reply to this email.</p>
        
        <p>Thank you for your patience.</p>
        
        <p>Best regards,<br>IT Support Team</p>
    </div>
    
    <div class="footer">
        <p>This is an automated response. For urgent issues, please call our helpdesk at 1-800-IT-SUPPORT.</p>
    </div>
</body>
</html>
    """.strip()
    
    return subject, body, html_body


def _create_escalation_email(
    ticket_id: str,
    ticket_data: Dict[str, Any],
    assignment_data: Dict[str, Any]
) -> tuple[str, str, str]:
    """Create email content for when a ticket is escalated."""
    
    subject = f"Ticket Escalated - {ticket_id}: {ticket_data.get('subject', 'IT Support Request')}"
    
    # Plain text body
    body = f"""
Dear {ticket_data.get('user_name', 'Valued Customer')},

Your IT support request has been escalated to our senior support team for specialized attention.

Ticket ID: {ticket_id}
Subject: {ticket_data.get('subject', 'N/A')}
Priority: {ticket_data.get('priority', 'N/A')}

ESCALATION DETAILS:
Escalated To: {assignment_data.get('team', 'Senior Support Team')}
Reason: {assignment_data.get('escalation_reason', 'Complex technical issue requiring specialized expertise')}
Expected Response Time: {assignment_data.get('estimated_response_time', 'N/A')}

Our senior team will provide a comprehensive solution to your issue. You will receive updates as we work on your request.

Thank you for your patience.

Best regards,
IT Support Team

---
This is an automated response. For urgent issues, please call our helpdesk at 1-800-IT-SUPPORT.
    """.strip()
    
    # HTML body (similar structure to assignment email but with escalation styling)
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background-color: #dc3545; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .ticket-info {{ background-color: #f9f9f9; padding: 15px; border-left: 4px solid #dc3545; margin: 20px 0; }}
        .escalation {{ background-color: #f8d7da; padding: 15px; border-left: 4px solid #dc3545; margin: 20px 0; }}
        .footer {{ background-color: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚨 Ticket Escalated</h1>
        <p>Your IT support request has been escalated for specialized attention</p>
    </div>
    
    <div class="content">
        <p>Dear {ticket_data.get('user_name', 'Valued Customer')},</p>
        
        <p>Your IT support request has been escalated to our senior support team for specialized attention.</p>
        
        <div class="ticket-info">
            <strong>Ticket ID:</strong> {ticket_id}<br>
            <strong>Subject:</strong> {ticket_data.get('subject', 'N/A')}<br>
            <strong>Priority:</strong> {ticket_data.get('priority', 'N/A')}
        </div>
        
        <div class="escalation">
            <h3>Escalation Details:</h3>
            <p><strong>Escalated To:</strong> {assignment_data.get('team', 'Senior Support Team')}</p>
            <p><strong>Reason:</strong> {assignment_data.get('escalation_reason', 'Complex technical issue requiring specialized expertise')}</p>
            <p><strong>Expected Response Time:</strong> {assignment_data.get('estimated_response_time', 'N/A')}</p>
        </div>
        
        <p>Our senior team will provide a comprehensive solution to your issue. You will receive updates as we work on your request.</p>
        
        <p>Thank you for your patience.</p>
        
        <p>Best regards,<br>IT Support Team</p>
    </div>
    
    <div class="footer">
        <p>This is an automated response. For urgent issues, please call our helpdesk at 1-800-IT-SUPPORT.</p>
    </div>
</body>
</html>
    """.strip()
    
    return subject, body, html_body 