"""Slack button handlers for ticket management."""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError
from ai_ticket_agent.tools.database import get_ticket, update_ticket_fields
from ai_ticket_agent.tools.notifications import send_slack_notification
from ai_ticket_agent.sub_agents.follow_up.agent import send_resolution_and_request_feedback


class SlackButtonHandler:
    """Handler for Slack button interactions."""
    
    def __init__(self):
        self.client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
        self.channel_id = os.getenv("SLACK_CHANNEL_ID")
    
    def handle_button_click(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Slack button click events.
        
        Args:
            payload: Slack interaction payload
            
        Returns:
            Dict containing the response
        """
        try:
            # Parse the interaction
            actions = payload.get("actions", [])
            if not actions:
                return {"error": "No actions found in payload"}
            
            action = actions[0]
            action_id = action.get("action_id", "")
            ticket_id = action.get("value", "")
            
            print(f"DEBUG: Handling button click - action_id: {action_id}, ticket_id: {ticket_id}")
            
            # Route to appropriate handler
            if action_id.startswith("accept_assignment_"):
                return self.handle_accept_assignment(ticket_id, payload)
            elif action_id.startswith("mark_resolved_"):
                return self.open_resolve_modal(ticket_id, payload)
            elif action_id.startswith("need_support_"):
                return self.handle_need_support(ticket_id, payload)
            elif action_id.startswith("escalate_"):
                return self.handle_escalate(ticket_id, payload)
            elif action_id.startswith("close_ticket_"):
                return self.handle_close_ticket(ticket_id, payload)
            else:
                return {"error": f"Unknown action_id: {action_id}"}
                
        except Exception as e:
            print(f"❌ Error handling button click: {e}")
            return {"error": str(e)}
    
    def handle_accept_assignment(self, ticket_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle 'Accept Assignment' button click.
        
        Args:
            ticket_id: The ticket identifier
            payload: Slack interaction payload
            
        Returns:
            Dict containing the response
        """
        print(f"DEBUG: Processing accept assignment for ticket {ticket_id}")
        
        # Get ticket data
        ticket = get_ticket(ticket_id)
        if not ticket:
            return {"error": f"Ticket {ticket_id} not found"}
        
        # Check if ticket is already in progress
        if ticket.status == "in_progress":
            return {
                "success": False,
                "message": f"Ticket {ticket.id} is already in progress"
            }
        
        # Update ticket status to in_progress
        updated_ticket = update_ticket_fields(
            ticket_id=ticket_id,
            updates={
                "status": "in_progress",
                "assigned_agent": payload.get("user", {}).get("username", "unknown")
            },
            updated_by="slack_user"
        )
        
        if not updated_ticket:
            return {"error": f"Failed to update ticket {ticket_id}"}
        
        # Send confirmation message based on previous status
        if ticket.status == "escalated":
            confirmation_message = (
                f"✅ *Escalation Accepted*\n"
                f"Ticket: `{ticket_id}` assigned to <@{payload.get('user', {}).get('id', 'unknown')}>\n"
                f"Status: `in_progress`"
            )
        else:
            confirmation_message = (
                f"✅ *Assignment Accepted*\n"
                f"Ticket: `{ticket_id}`\n"
                f"Status: `in_progress`\n"
                f"Assigned to: <@{payload.get('user', {}).get('id', 'unknown')}>\n"
                f"Subject: {ticket.subject}"
            )
        
        # Update the original message with new buttons
        self.update_message_with_new_status(
            payload, 
            ticket_id, 
            "in_progress", 
            confirmation_message
        )
        
        print(f"✅ Assignment accepted for ticket {ticket_id}")
        return {
            "success": True,
            "message": f"Assignment accepted for ticket {ticket_id}",
            "new_status": "in_progress"
        }
    
    def handle_mark_resolved(self, ticket_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle 'Mark Resolved' button click.
        
        Args:
            ticket_id: The ticket identifier
            payload: Slack interaction payload
            
        Returns:
            Dict containing the response
        """
        print(f"DEBUG: Processing mark resolved for ticket {ticket_id}")
        
        # Get ticket data
        ticket = get_ticket(ticket_id)
        if not ticket:
            return {"error": f"Ticket {ticket_id} not found"}
        
        # Check if ticket is in progress
        if ticket.status != "in_progress":
            return {
                "success": False,
                "message": f"Ticket {ticket_id} must be in progress to mark as resolved"
            }
        
        # Update ticket status to resolved
        updated_ticket = update_ticket_fields(
            ticket_id=ticket_id,
            updates={
                "status": "resolved",
                "resolved_at": datetime.now().isoformat()
            },
            updated_by="slack_user"
        )
        
        if not updated_ticket:
            return {"error": f"Failed to update ticket {ticket_id}"}
        
        # Send confirmation message
        confirmation_message = (
            f"✅ *Ticket Resolved*\n"
            f"Ticket: `{ticket_id}`\n"
            f"Status: `resolved`\n"
            f"Resolved by: <@{payload.get('user', {}).get('id', 'unknown')}>\n"
            f"Subject: {ticket.subject}\n"
            f"Resolution time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        # Update the original message with new buttons
        self.update_message_with_new_status(
            payload, 
            ticket_id, 
            "resolved", 
            confirmation_message
        )
        
        print(f"✅ Ticket {ticket_id} marked as resolved")
        return {
            "success": True,
            "message": f"Ticket {ticket_id} marked as resolved",
            "new_status": "resolved"
        }
    
    def handle_need_support(self, ticket_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle 'Need Support' button click.
        
        Args:
            ticket_id: The ticket identifier
            payload: Slack interaction payload
            
        Returns:
            Dict containing the response
        """
        print(f"DEBUG: Processing need support for ticket {ticket_id}")
        
        # Get ticket data
        ticket = get_ticket(ticket_id)
        if not ticket:
            return {"error": f"Ticket {ticket_id} not found"}
        
        # Update ticket status to needs_support
        updated_ticket = update_ticket_fields(
            ticket_id=ticket_id,
            updates={
                "status": "needs_support"
            },
            updated_by="slack_user"
        )
        
        if not updated_ticket:
            return {"error": f"Failed to update ticket {ticket_id}"}
        
        # Send escalation notification
        escalation_message = (
            f"🆘 *Support Needed*\n"
            f"Ticket: `{ticket_id}`\n"
            f"Status: `needs_support`\n"
            f"Requested by: <@{payload.get('user', {}).get('id', 'unknown')}>\n"
            f"Subject: {ticket.subject}\n"
            f"Current Team: {ticket.assigned_team}\n"
            f"Priority: {ticket.priority}"
        )
        
        # Send to channel
        send_slack_notification(self.channel_id, escalation_message)
        
        # Update the original message
        self.update_message_with_new_status(
            payload, 
            ticket_id, 
            "needs_support", 
            escalation_message
        )
        
        print(f"✅ Support requested for ticket {ticket_id}")
        return {
            "success": True,
            "message": f"Support requested for ticket {ticket_id}",
            "new_status": "needs_support"
        }
    
    def handle_escalate(self, ticket_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle 'Escalate' button click.
        
        Args:
            ticket_id: The ticket identifier
            payload: Slack interaction payload
            
        Returns:
            Dict containing the response
        """
        print(f"DEBUG: Processing escalate for ticket {ticket_id}")
        
        # Get ticket data
        ticket = get_ticket(ticket_id)
        if not ticket:
            return {"error": f"Ticket {ticket_id} not found"}
        
        # Determine escalation team based on current team
        escalation_team = self.get_escalation_team(ticket.assigned_team)
        
        # Update ticket status and team
        updated_ticket = update_ticket_fields(
            ticket_id=ticket_id,
            updates={
                "status": "escalated",
                "assigned_team": escalation_team
            },
            updated_by="slack_user"
        )
        
        if not updated_ticket:
            return {"error": f"Failed to update ticket {ticket_id}"}
        
        # Send a new message to the channel for the escalation
        escalation_message = (
            f"🚨 *Ticket Escalated to {escalation_team}*\n"
            f"Ticket: `{ticket_id}` (from *{ticket.assigned_team}*)\n"
            f"Subject: {ticket.subject}\n"
            f"Priority: {ticket.priority}"
        )

        # Create new blocks with the "Accept Escalation" button
        escalation_blocks = self.create_status_blocks(updated_ticket, "escalated")
        
        send_slack_notification(
            channel=self.channel_id, 
            message=escalation_message,
            blocks=escalation_blocks
        )
        
        # Update the original message to show it has been escalated
        original_message_update_text = (
            f"✅ *Ticket Escalated*\n"
            f"Ticket: `{ticket_id}` has been escalated from *{ticket.assigned_team}* to *{escalation_team}*."
        )
        self.client.chat_update(
            channel=payload["channel"]["id"],
            ts=payload["message"]["ts"],
            text=original_message_update_text,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": original_message_update_text
                    }
                }
            ]
        )
        
        print(f"✅ Ticket {ticket_id} escalated to {escalation_team}")
        return {
            "success": True,
            "message": f"Ticket {ticket_id} escalated to {escalation_team}",
            "new_status": "escalated"
        }
    
    def handle_close_ticket(self, ticket_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle 'Close Ticket' button click.
        
        Args:
            ticket_id: The ticket identifier
            payload: Slack interaction payload
            
        Returns:
            Dict containing the response
        """
        print(f"DEBUG: Processing close ticket for ticket {ticket_id}")
        
        # Get ticket data
        ticket = get_ticket(ticket_id)
        if not ticket:
            return {"error": f"Ticket {ticket_id} not found"}
        
        # Check if ticket is resolved
        if ticket.status != "resolved":
            return {
                "success": False,
                "message": f"Ticket {ticket_id} must be resolved before closing"
            }
        
        # Update ticket status to closed
        updated_ticket = update_ticket_fields(
            ticket_id=ticket_id,
            updates={
                "status": "closed"
            },
            updated_by="slack_user"
        )
        
        if not updated_ticket:
            return {"error": f"Failed to update ticket {ticket_id}"}
        
        # Send confirmation message
        confirmation_message = (
            f"✅ *Ticket Closed*\n"
            f"Ticket: `{ticket_id}`\n"
            f"Status: `closed`\n"
            f"Closed by: <@{payload.get('user', {}).get('id', 'unknown')}>\n"
            f"Subject: {ticket.subject}\n"
            f"Total time: {self.calculate_total_time(ticket.created_at)}"
        )
        
        # Update the original message
        self.update_message_with_new_status(
            payload, 
            ticket_id, 
            "closed", 
            confirmation_message
        )
        
        print(f"✅ Ticket {ticket_id} closed")
        return {
            "success": True,
            "message": f"Ticket {ticket_id} closed",
            "new_status": "closed"
        }
    
    def get_escalation_team(self, current_team: str) -> str:
        """
        Determine the escalation team based on current team.
        
        Args:
            current_team: Current assigned team
            
        Returns:
            Escalation team name
        """
        escalation_map = {
            "Network Support": "Senior Network Support",
            "Software Support": "Senior Software Support", 
            "Hardware Support": "Senior Hardware Support",
            "Security Support": "Security Team Lead",
            "Email Support": "Senior Email Support",
            "Access Support": "Senior Access Support",
            "General Support": "Senior Support Team"
        }
        
        return escalation_map.get(current_team, "Senior Support Team")
    
    def calculate_total_time(self, created_at: str) -> str:
        """
        Calculate total time from creation to now.
        
        Args:
            created_at: Creation timestamp
            
        Returns:
            Formatted time string
        """
        created_dt = datetime.fromisoformat(created_at)
        total_time = datetime.now() - created_dt
        
        if total_time.days > 0:
            return f"{total_time.days} days, {total_time.seconds // 3600} hours"
        elif total_time.seconds > 3600:
            return f"{total_time.seconds // 3600} hours, {(total_time.seconds % 3600) // 60} minutes"
        else:
            return f"{total_time.seconds // 60} minutes"
    
    def update_message_with_new_status(
        self, 
        payload: Dict[str, Any], 
        ticket_id: str, 
        new_status: str, 
        confirmation_message: str
    ) -> None:
        """
        Update the original Slack message with new status and buttons.
        
        Args:
            payload: Slack interaction payload
            ticket_id: The ticket identifier
            new_status: New ticket status
            confirmation_message: Confirmation message to show
        """
        try:
            # Get ticket data
            ticket = get_ticket(ticket_id)
            if not ticket:
                return
            
            # Create new blocks based on status
            blocks = self.create_status_blocks(ticket, new_status)
            
            # Update the message
            self.client.chat_update(
                channel=payload["channel"]["id"],
                ts=payload["message"]["ts"],
                text=confirmation_message,
                blocks=blocks
            )
            
        except SlackApiError as e:
            print(f"❌ Error updating Slack message: {e.response['error']}")
        except Exception as e:
            print(f"❌ Error updating message: {e}")
    
    def create_status_blocks(self, ticket, status: str) -> list:
        """
        Create Slack blocks based on ticket status.
        
        Args:
            ticket: Ticket object
            status: Current ticket status
            
        Returns:
            List of Slack blocks
        """
        # Base blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📋 Ticket: {ticket.id} - {status.upper()}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Subject:*\n{ticket.subject}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Priority:*\n{ticket.priority}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Category:*\n{ticket.category}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Status:*\n{status}"
                    }
                ]
            }
        ]
        
        # Add description if available
        if ticket.description and ticket.description != "No description":
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Description:*\n{ticket.description}"
                }
            })
        
        # Add action buttons based on status
        action_blocks = self.get_action_buttons(ticket, status)
        if action_blocks:
            blocks.append(action_blocks)
        
        return blocks
    
    def get_action_buttons(self, ticket, status: str) -> Optional[Dict[str, Any]]:
        """
        Get action buttons based on ticket status.
        
        Args:
            ticket: Ticket object
            status: Current ticket status
            
        Returns:
            Action blocks or None
        """
        if status == "open":
            return {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Accept Assignment",
                            "emoji": True
                        },
                        "style": "primary",
                        "value": ticket.id,
                        "action_id": f"accept_assignment_{ticket.id}"
                    }
                ]
            }
        elif status == "in_progress":
            return {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Mark Resolved",
                            "emoji": True
                        },
                        "style": "primary",
                        "value": ticket.id,
                        "action_id": f"mark_resolved_{ticket.id}"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Escalate",
                            "emoji": True
                        },
                        "style": "danger",
                        "value": ticket.id,
                        "action_id": f"escalate_{ticket.id}"
                    }
                ]
            }
        elif status == "resolved":
            return {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Close Ticket",
                            "emoji": True
                        },
                        "style": "primary",
                        "value": ticket.id,
                        "action_id": f"close_ticket_{ticket.id}"
                    }
                ]
            }
        elif status == "escalated":
            return {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Accept Escalation",
                            "emoji": True
                        },
                        "style": "primary",
                        "value": ticket.id,
                        "action_id": f"accept_assignment_{ticket.id}"
                    }
                ]
            }
        
        return None

    def handle_view_submission(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a modal submission from Slack.
        """
        try:
            view = payload.get("view", {})
            callback_id = view.get("callback_id", "")
            
            if callback_id.startswith("resolve_ticket_modal_"):
                return self.handle_resolve_ticket_submission(payload)
            else:
                return {"error": f"Unknown view callback_id: {callback_id}"}

        except Exception as e:
            print(f"❌ Error handling view submission: {e}")
            return {"error": str(e)}

    def open_resolve_modal(self, ticket_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Open a modal for the user to enter resolution notes.
        """
        try:
            self.client.views_open(
                trigger_id=payload["trigger_id"],
                view={
                    "type": "modal",
                    "callback_id": f"resolve_ticket_modal_{ticket_id}",
                    "title": {"type": "plain_text", "text": "Resolve Ticket"},
                    "submit": {"type": "plain_text", "text": "Submit"},
                    "close": {"type": "plain_text", "text": "Cancel"},
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"Please enter the resolution notes for ticket `{ticket_id}`."
                            }
                        },
                        {
                            "type": "input",
                            "block_id": "resolution_notes_block",
                            "element": {
                                "type": "plain_text_input",
                                "action_id": "resolution_notes",
                                "multiline": True
                            },
                            "label": {"type": "plain_text", "text": "Resolution Notes"}
                        }
                    ]
                }
            )
            return {"success": True, "message": "Opening resolve modal."}
        except SlackApiError as e:
            print(f"❌ Slack API error opening modal: {e.response['error']}")
            return {"error": "Failed to open modal."}

    def handle_resolve_ticket_submission(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the submission of the resolve ticket modal.
        """
        view = payload["view"]
        ticket_id = view["callback_id"].replace("resolve_ticket_modal_", "")
        values = view["state"]["values"]
        resolution_notes = values["resolution_notes_block"]["resolution_notes"]["value"]

        if not resolution_notes or len(resolution_notes) < 10:
            return {"error": "Resolution notes must be at least 10 characters."}

        # Update the ticket in the database
        updated_ticket = update_ticket_fields(
            ticket_id=ticket_id,
            updates={
                "status": "resolved",
                "resolved_at": datetime.now().isoformat(),
                "resolution_notes": resolution_notes
            },
            updated_by=payload.get("user", {}).get("username", "unknown")
        )

        if not updated_ticket:
            return {"error": "Failed to update ticket in the database."}

        # Send resolution email to user via follow-up agent
        send_resolution_and_request_feedback(ticket_id)

        # Update the original Slack message
        # Note: We need the original message's channel and ts. This is a limitation.
        # For now, we'll post a new confirmation message to the channel.
        confirmation_message = (
            f"✅ *Ticket Resolved*\n"
            f"Ticket: `{ticket_id}` has been marked as resolved by <@{payload.get('user', {}).get('id', 'unknown')}>\n"
            f"*Resolution Notes:*\n{resolution_notes}"
        )
        send_slack_notification(self.channel_id, confirmation_message)
        
        print(f"INFO: Triggering follow-up agent for ticket {ticket_id}")

        return {"success": True}


# Global handler instance
slack_handler = SlackButtonHandler()


def handle_slack_interaction(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for handling Slack interactions.
    
    Args:
        payload: Slack interaction payload
        
    Returns:
        Dict containing the response
    """
    interaction_type = payload.get("type")
    
    if interaction_type == "block_actions":
        return slack_handler.handle_button_click(payload)
    elif interaction_type == "view_submission":
        return slack_handler.handle_view_submission(payload)
    else:
        return {"error": f"Unsupported interaction type: {interaction_type}"} 