#!/usr/bin/env python3
"""
Test script for email notifications in AI Ticket Agent.
Run this script to test if your email configuration is working.
"""

import os
from dotenv import load_dotenv
from ai_ticket_agent.tools.notifications import (
    send_email_notification,
    send_notification,
    get_notification_config
)

def test_email_config():
    """Test email configuration and send a test notification."""
    
    # Load environment variables
    load_dotenv()
    
    print("🔧 Testing Email Notification Configuration")
    print("=" * 50)
    
    # Check configuration
    config = get_notification_config()
    print(f"Email Enabled: {config.email_enabled}")
    print(f"SMTP Host: {config.smtp_host}")
    print(f"SMTP Port: {config.smtp_port}")
    print(f"SMTP Username: {'✅ Set' if config.smtp_username else '❌ Not set'}")
    print(f"SMTP Password: {'✅ Set' if config.smtp_password else '❌ Not set'}")
    
    if not config.email_enabled:
        print("\n❌ Email notifications are disabled!")
        print("Please set SMTP_HOST in your .env file")
        return False
    
    return True

def test_basic_email():
    """Test basic email notification."""
    
    print("\n📧 Testing Basic Email Notification")
    print("=" * 35)
    
    # Get test email from user or use default
    test_email = input("Enter test email address (or press Enter for default): ").strip()
    if not test_email:
        test_email = "test@example.com"
        print(f"Using default email: {test_email}")
    
    test_subject = "🧪 Test Email from AI Ticket Agent"
    test_body = """
This is a test email notification from the AI Ticket Agent system.

If you received this email, your email notification configuration is working correctly!

Best regards,
AI Ticket Agent Team
    """.strip()
    
    success = send_email_notification(
        to_email=test_email,
        subject=test_subject,
        body=test_body
    )
    
    if success:
        print("✅ Email notification sent successfully!")
        print(f"To: {test_email}")
        print(f"Subject: {test_subject}")
    else:
        print("❌ Failed to send email notification")
    
    return success

def test_ticket_email():
    """Test ticket-specific email notification."""
    
    print("\n🎫 Testing Ticket Email Notification")
    print("=" * 35)
    
    # Get test email from user or use default
    test_email = input("Enter test email address for ticket notification (or press Enter for default): ").strip()
    if not test_email:
        test_email = "test@example.com"
        print(f"Using default email: {test_email}")
    
    ticket_data = {
        "ticket_id": "TICKET-20250622-TEST123",
        "subject": "Test WiFi Connection Issue",
        "priority": "medium",
        "category": "network",
        "status": "open",
        "description": "User reported issues connecting to the WiFi network. Cannot access internet from their workstation.",
        "assigned_team": "Network Support",
        "created_by": "user@company.com"
    }
    
    html_body = f"""
    <html>
    <body>
        <h2>🚨 New IT Support Ticket Created</h2>
        <p>A new IT support ticket has been created and requires your attention.</p>
        
        <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
            <tr style="background-color: #f2f2f2;">
                <td style="padding: 10px; border: 1px solid #ddd;"><strong>Ticket ID:</strong></td>
                <td style="padding: 10px; border: 1px solid #ddd;">{ticket_data['ticket_id']}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;"><strong>Subject:</strong></td>
                <td style="padding: 10px; border: 1px solid #ddd;">{ticket_data['subject']}</td>
            </tr>
            <tr style="background-color: #f2f2f2;">
                <td style="padding: 10px; border: 1px solid #ddd;"><strong>Priority:</strong></td>
                <td style="padding: 10px; border: 1px solid #ddd;">{ticket_data['priority'].upper()}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;"><strong>Category:</strong></td>
                <td style="padding: 10px; border: 1px solid #ddd;">{ticket_data['category']}</td>
            </tr>
            <tr style="background-color: #f2f2f2;">
                <td style="padding: 10px; border: 1px solid #ddd;"><strong>Status:</strong></td>
                <td style="padding: 10px; border: 1px solid #ddd;">{ticket_data['status']}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;"><strong>Assigned Team:</strong></td>
                <td style="padding: 10px; border: 1px solid #ddd;">{ticket_data['assigned_team']}</td>
            </tr>
            <tr style="background-color: #f2f2f2;">
                <td style="padding: 10px; border: 1px solid #ddd;"><strong>Created By:</strong></td>
                <td style="padding: 10px; border: 1px solid #ddd;">{ticket_data['created_by']}</td>
            </tr>
        </table>
        
        <h3>Description:</h3>
        <p style="background-color: #f9f9f9; padding: 15px; border-left: 4px solid #007cba;">
            {ticket_data['description']}
        </p>
        
        <p><strong>Please review this ticket and take appropriate action.</strong></p>
        
        <hr>
        <p style="color: #666; font-size: 12px;">
            This is an automated notification from the AI Ticket Agent system.
        </p>
    </body>
    </html>
    """
    
    success = send_email_notification(
        to_email=test_email,
        subject=f"New Ticket: {ticket_data['subject']}",
        body=f"""
New IT Support Ticket Created

Ticket ID: {ticket_data['ticket_id']}
Subject: {ticket_data['subject']}
Priority: {ticket_data['priority'].upper()}
Category: {ticket_data['category']}
Status: {ticket_data['status']}
Assigned Team: {ticket_data['assigned_team']}
Created By: {ticket_data['created_by']}

Description:
{ticket_data['description']}

Please review and take appropriate action.
        """.strip(),
        html_body=html_body
    )
    
    if success:
        print("✅ Ticket email notification sent successfully!")
        print(f"To: {test_email}")
    else:
        print("❌ Failed to send ticket email notification")
    
    return success

def main():
    """Main test function."""
    print("🧪 AI Ticket Agent - Email Notification Test Suite")
    print("=" * 55)
    
    # Test 1: Basic configuration
    config_ok = test_email_config()
    
    if not config_ok:
        print("\n❌ Cannot proceed with tests due to configuration issues.")
        return
    
    # Test 2: Basic email
    test_basic_email()
    
    # Test 3: Ticket email
    test_ticket_email()
    
    print("\n✅ All email notification tests completed!")
    print("Check your email inbox for the test messages.")

if __name__ == "__main__":
    main() 