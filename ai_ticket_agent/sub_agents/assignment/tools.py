"""Tools for the Ticket Assignment Agent."""

from typing import Dict, List, Any
from pydantic import BaseModel, Field
from ai_ticket_agent.tools.database import update_ticket_fields, get_step_data, update_workflow_state, get_ticket_info
from ai_ticket_agent.tools.notifications import draft_and_send_ticket_email, send_team_assignment_notification


class TicketAssignment(BaseModel):
    """Assignment result for routing a ticket."""
    
    team: str = Field(description="Assigned support team")
    queue: str = Field(description="Queue within the team: urgent, high, standard, low")
    estimated_response_time: str = Field(description="Estimated time to first response")
    routing_reason: str = Field(description="Reason for this assignment")


def assign_ticket(ticket_id: str) -> TicketAssignment:
    """
    Assign a ticket to the appropriate team based on its classification.
    """
    # Get classification data from the previous workflow step
    classification_data = get_step_data(ticket_id, "CLASSIFICATION")
    ticket_info = get_ticket_info(ticket_id)
    
    if not classification_data:
        print(f"Error: Could not find classification data for ticket {ticket_id}")
        # Return a default assignment
        return TicketAssignment(
            team="General IT",
            queue="standard",
            estimated_response_time="4 hours",
            routing_reason="Classification data was not found."
        )

    priority = classification_data.get("priority", "medium")
    category = classification_data.get("category", "general")
    suggested_team = classification_data.get("suggested_team")
    
    # Determine team based on category
    team_mapping = {
        "hardware": "Hardware Support",
        "software": "Software Support",
        "network": "Network Support",
        "access": "Access Management",
        "security": "Security Team",
        "email": "Email Support",
        "general": "General IT"
    }
    
    team = suggested_team or team_mapping.get(category, "General IT")
    
    # Determine queue based on priority
    queue_mapping = {
        "critical": "urgent",
        "high": "high",
        "medium": "standard",
        "low": "low"
    }
    queue = queue_mapping.get(priority, "standard")
    
    # Create assignment
    assignment = TicketAssignment(
        team=team,
        queue=queue,
        estimated_response_time="2 hours",
        routing_reason=f"{category} issue matches {team} expertise"
    )
    
    # Update ticket in database with assignment
    try:
        update_ticket_fields(
            ticket_id=ticket_id,
            updates={
                "assigned_team": assignment.team,
                "status": "assigned",
            }
        )
        
        # Update workflow state
        update_workflow_state(
            ticket_id=ticket_id,
            current_step="ASSIGNMENT",
            next_step="COMPLETE",
            step_data={"ASSIGNMENT": assignment.dict()},
            status="assigned"
        )
        
        print(f"Ticket {ticket_id} assigned to {assignment.team}")
        
        # Send assignment email to user
        if ticket_info:
            send_assignment_email_to_user(ticket_id, ticket_info, classification_data, assignment)
            # Send Slack notification to team
            send_team_assignment_notification(ticket_id, {**ticket_info, "assigned_team": assignment.team})
        
    except Exception as e:
        print(f"Error updating ticket assignment: {e}")
    
    return assignment


def send_assignment_email_to_user(
    ticket_id: str,
    ticket_info: Dict[str, Any],
    classification_data: Dict[str, Any],
    assignment: TicketAssignment
) -> bool:
    """
    Send an assignment email to the user when a ticket is assigned to a team.
    """
    try:
        user_email = ticket_info.get("user_email", "user@company.com")
        
        # Prepare ticket data
        ticket_data = {
            "subject": ticket_info.get("subject", "IT Support Request"),
            "priority": classification_data.get("priority", "MEDIUM"),
            "category": classification_data.get("category", "general"),
            "user_name": "Valued Customer"
        }
        
        # Prepare assignment data
        assignment_data = {
            "team": assignment.team,
            "estimated_response_time": assignment.estimated_response_time,
            "routing_reason": assignment.routing_reason
        }
        
        # Send the assignment email
        success = draft_and_send_ticket_email(
            ticket_id=ticket_id,
            user_email=user_email,
            email_type="team_assigned",
            ticket_data=ticket_data,
            assignment_data=assignment_data
        )
        
        if success:
            print(f"✅ Assignment email sent to {user_email} for ticket {ticket_id}")
        else:
            print(f"❌ Failed to send assignment email to {user_email} for ticket {ticket_id}")
        
        return success
        
    except Exception as e:
        print(f"❌ Error sending assignment email: {e}")
        return False


def continue_workflow(ticket_id: str) -> dict:
    """
    Continue the workflow after assignment.
    """
    return {
        "next_agent": None,
        "ticket_id": ticket_id,
        "status": "assigned"
    } 