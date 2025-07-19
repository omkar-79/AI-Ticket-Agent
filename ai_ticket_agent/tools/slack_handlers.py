"""Slack escalation tool for sending tickets to human teams."""

import os
import json
from typing import Dict, Any, Optional
from google.adk.tools import ToolContext

# Try to import slack_sdk, but don't fail if not available
try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False
    print("⚠️  slack_sdk not installed. Slack notifications will be simulated.")


def get_slack_client() -> Optional[WebClient]:
    """Get Slack client if credentials are available."""
    if not SLACK_AVAILABLE:
        return None
    
    bot_token = os.getenv("SLACK_BOT_TOKEN")
    if not bot_token or bot_token == "xoxb-your-slack-bot-token":
        return None
    
    return WebClient(token=bot_token)


def get_team_channel(team_name: str) -> str:
    """Map team names to Slack channels."""
    team_channel_map = {
        "Network Team": "#it-network-support",
        "Security Team": "#it-security-support", 
        "Hardware Team": "#it-hardware-support",
        "Software Team": "#it-software-support",
        "Access Management": "#it-access-support",
        "Infrastructure Team": "#it-infrastructure-support",
        "General IT Support": "#it-general-support"
    }
    
    return team_channel_map.get(team_name, "#it-general-support")


def get_fallback_channel() -> str:
    """Get fallback channel when team-specific channels don't exist."""
    # Try to use SLACK_CHANNEL_ID from environment, or default to general
    channel_id = os.getenv("SLACK_CHANNEL_ID")
    if channel_id and channel_id != "C1234567890":
        return channel_id
    
    return "#it-general-support"


def format_slack_message(team_name: str, problem_description: str, user_email: str, priority: str = "medium") -> Dict[str, Any]:
    """Format a Slack message for team escalation."""
    
    # Priority emoji mapping
    priority_emoji = {
        "critical": "🚨",
        "high": "⚠️", 
        "medium": "📋",
        "low": "ℹ️"
    }
    
    emoji = priority_emoji.get(priority.lower(), "📋")
    
    # Format the message
    message = {
        "text": f"{emoji} IT Support Ticket - {team_name}",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} IT Support Ticket - {team_name}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*User:*\n{user_email}"
                    },
                    {
                        "type": "mrkdwn", 
                        "text": f"*Priority:*\n{priority.upper()}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Problem Description:*\n{problem_description}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Next Steps:*\n• Please acknowledge this ticket\n• Update status in the thread\n• Contact user when resolved"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "🤖 *Automatically escalated by AI Support Agent*"
                    }
                ]
            }
        ]
    }
    
    return message


def send_slack_notification(channel: str, message: Dict[str, Any]) -> Dict[str, Any]:
    """Send a message to a Slack channel."""
    client = get_slack_client()
    
    if not client:
        # Simulate Slack notification
        return {
            "success": True,
            "simulated": True,
            "channel": channel,
            "message": "Slack notification simulated (no credentials or slack_sdk)"
        }
    
    try:
        response = client.chat_postMessage(
            channel=channel,
            text=message["text"],
            blocks=message["blocks"]
        )
        
        return {
            "success": True,
            "channel": channel,
            "ts": response["ts"],
            "message": "Slack notification sent successfully"
        }
        
    except SlackApiError as e:
        error_msg = f"Slack API error: {e.response['error']}"
        print(f"Slack API Error: {error_msg}")
        
        # If channel not found, try fallback channel
        if e.response['error'] == 'channel_not_found':
            fallback_channel = get_fallback_channel()
            print(f"Trying fallback channel: {fallback_channel}")
            
            try:
                response = client.chat_postMessage(
                    channel=fallback_channel,
                    text=message["text"],
                    blocks=message["blocks"]
                )
                
                return {
                    "success": True,
                    "channel": fallback_channel,
                    "ts": response["ts"],
                    "message": f"Slack notification sent to fallback channel {fallback_channel}",
                    "fallback_used": True
                }
                
            except SlackApiError as fallback_error:
                return {
                    "success": False,
                    "error": f"Both primary and fallback channels failed: {fallback_error.response['error']}",
                    "channel": channel,
                    "fallback_channel": fallback_channel
                }
        
        return {
            "success": False,
            "error": error_msg,
            "channel": channel
        }
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"Unexpected Error: {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "channel": channel
        }


def escalate_to_slack(team_assignment: str, problem_description: str, user_email: str = "Unknown User", priority: str = "medium", tool_context: ToolContext = None) -> str:
    """
    Format and send ticket to appropriate Slack channel.
    
    Args:
        team_assignment: Team routing information (e.g., "Software Team")
        problem_description: The IT problem description
        user_email: User's email address
        priority: Priority level (critical, high, medium, low)
        tool_context: The ADK tool context
        
    Returns:
        Confirmation of escalation
    """
    
    # Extract team name from assignment
    team_name = team_assignment
    if "#it-" in team_assignment:
        # Extract team name from channel format
        channel_part = team_assignment.split("#it-")[1].split("-")[0]
        team_name_map = {
            "network": "Network Team",
            "security": "Security Team", 
            "hardware": "Hardware Team",
            "software": "Software Team",
            "access": "Access Management",
            "infrastructure": "Infrastructure Team",
            "general": "General IT Support"
        }
        team_name = team_name_map.get(channel_part, "General IT Support")
    
    # Get the appropriate channel
    channel = get_team_channel(team_name)
    
    # Format the Slack message
    slack_message = format_slack_message(team_name, problem_description, user_email, priority)
    
    # Send the notification
    result = send_slack_notification(channel, slack_message)
    
    if result["success"]:
        if result.get("simulated"):
            return f"""
**Slack Escalation Simulated**

Team: {team_name}
Channel: {channel}
User: {user_email}
Priority: {priority.upper()}

Message would be sent to Slack with the following content:
{json.dumps(slack_message, indent=2)}

**Note:** To enable real Slack notifications:
1. Install slack_sdk: `pip install slack_sdk`
2. Set SLACK_BOT_TOKEN in your .env file
3. Ensure your bot has permissions to post to the channel
            """
        else:
            fallback_note = ""
            if result.get("fallback_used"):
                fallback_note = f"\n**Note:** Sent to fallback channel {result.get('channel')} (team-specific channel not found)"
            
            return f"""
**Slack Escalation Complete** ✅

Team: {team_name}
Channel: {result.get('channel', channel)}
User: {user_email}
Priority: {priority.upper()}
Message ID: {result.get('ts', 'N/A')}

The ticket has been successfully sent to Slack.{fallback_note}
            """
    else:
        return f"""
**Slack Escalation Failed** ❌

Team: {team_name}
Channel: {channel}
Error: {result.get('error', 'Unknown error')}

Please check your Slack configuration and try again.
        """


def handle_slack_interaction(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Slack interactive events (button clicks, etc.)."""
    try:
        # Extract interaction details
        interaction_type = payload.get("type")
        
        if interaction_type == "block_actions":
            # Handle button clicks
            actions = payload.get("actions", [])
            for action in actions:
                action_id = action.get("action_id")
                
                if action_id == "acknowledge_ticket":
                    return {"message": "✅ Ticket acknowledged by the team"}
                elif action_id == "escalate_further":
                    return {"message": "🔄 Ticket escalated to senior team member"}
                elif action_id == "mark_resolved":
                    return {"message": "🎉 Ticket marked as resolved"}
        
        elif interaction_type == "view_submission":
            # Handle modal submissions
            view = payload.get("view", {})
            state = view.get("state", {})
            values = state.get("values", {})
            
            # Extract form data
            resolution_notes = ""
            for block_id, block_values in values.items():
                for action_id, action_value in block_values.items():
                    if action_id == "resolution_notes":
                        resolution_notes = action_value.get("value", "")
            
            if resolution_notes:
                return {"message": f"📝 Resolution notes added: {resolution_notes}"}
            else:
                return {"error": "Resolution notes are required"}
        
        return {"message": "Interaction processed successfully"}
        
    except Exception as e:
        return {"error": f"Error processing interaction: {str(e)}"}


# The tool is just the function itself
slack_escalation_tool = escalate_to_slack 