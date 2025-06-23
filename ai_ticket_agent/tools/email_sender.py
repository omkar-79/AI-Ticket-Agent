"""Clean email sender for AI Ticket Agent."""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class EmailSender:
    """Simple email sender for ticket notifications."""
    
    def __init__(self):
        """Initialize email sender with configuration."""
        load_dotenv()
        
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        
        # Validate configuration
        if not self.smtp_username or not self.smtp_password:
            raise ValueError("SMTP_USERNAME and SMTP_PASSWORD must be set in .env file")
    
    def send_simple_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """
        Send a simple email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
            
        Returns:
            bool: True if email was sent successfully
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add text part
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            print(f"✅ Email sent successfully to {to_email}: {subject}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {e}")
            return False
    
    def send_solution_email(
        self,
        ticket_id: str,
        user_email: str,
        ticket_data: Dict[str, Any],
        solution_data: Dict[str, Any]
    ) -> bool:
        """
        Send a solution email when knowledge base has a solution.
        
        Args:
            ticket_id: The ticket identifier
            user_email: User's email address
            ticket_data: Basic ticket information
            solution_data: Solution information
            
        Returns:
            bool: True if email was sent successfully
        """
        subject = f"Solution Found - Ticket {ticket_id}: {ticket_data.get('subject', 'IT Support Request')}"
        
        # Plain text body
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
        
        # HTML body
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .ticket-info {{ background-color: #f9f9f9; padding: 15px; border-left: 4px solid #4CAF50; margin: 20px 0; }}
        .solution {{ background-color: #e8f5e8; padding: 15px; border-left: 4px solid #4CAF50; margin: 20px 0; }}
        .steps {{ background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; }}
        .footer {{ background-color: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>✅ Solution Found</h1>
        <p>Your IT support request has been resolved!</p>
    </div>
    
    <div class="content">
        <p>Dear {ticket_data.get('user_name', 'Valued Customer')},</p>
        
        <p>Good news! We found a solution for your IT support request.</p>
        
        <div class="ticket-info">
            <strong>Ticket ID:</strong> {ticket_id}<br>
            <strong>Subject:</strong> {ticket_data.get('subject', 'N/A')}<br>
            <strong>Priority:</strong> {ticket_data.get('priority', 'N/A')}
        </div>
        
        <div class="solution">
            <h3>Solution:</h3>
            <p>{solution_data.get('response_text', 'No solution text provided')}</p>
        </div>
        
        <div class="steps">
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
    
    <div class="footer">
        <p>This is an automated response. For urgent issues, please call our helpdesk at 1-800-IT-SUPPORT.</p>
    </div>
</body>
</html>
        """.strip()
        
        return self.send_simple_email(user_email, subject, body, html_body)
    
    def send_assignment_email(
        self,
        ticket_id: str,
        user_email: str,
        ticket_data: Dict[str, Any],
        assignment_data: Dict[str, Any]
    ) -> bool:
        """
        Send an assignment email when a ticket is assigned to a team.
        
        Args:
            ticket_id: The ticket identifier
            user_email: User's email address
            ticket_data: Basic ticket information
            assignment_data: Assignment information
            
        Returns:
            bool: True if email was sent successfully
        """
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
        
        return self.send_simple_email(user_email, subject, body, html_body)


# Global email sender instance
email_sender = EmailSender() 