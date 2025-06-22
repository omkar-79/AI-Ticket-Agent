"""Notification tools for the AI Ticket Agent."""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


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
    
    if not config.email_enabled:
        print(f"Email notification disabled. Would send to {to_email}: {subject}")
        return True
    
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
        
        # Send email
        with smtplib.SMTP(config.smtp_host, config.smtp_port) as server:
            server.starttls()
            server.login(config.smtp_username, config.smtp_password)
            server.send_message(msg)
        
        print(f"Email notification sent to {to_email}: {subject}")
        return True
        
    except Exception as e:
        print(f"Failed to send email notification: {e}")
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
    
    try:
        # This would use the Slack API to send the message
        # For now, just print the message
        print(f"Slack notification to {channel}: {message}")
        if blocks:
            print(f"With blocks: {blocks}")
        return True
        
    except Exception as e:
        print(f"Failed to send Slack notification: {e}")
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