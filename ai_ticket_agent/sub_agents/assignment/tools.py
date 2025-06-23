"""Tools for the Ticket Assignment Agent."""

from typing import Dict, List, Any
from pydantic import BaseModel, Field
from ai_ticket_agent.tools.database import update_ticket_fields, get_step_data, update_workflow_state, get_ticket_user_email
from ai_ticket_agent.tools.notifications import send_team_assignment_notification
from ai_ticket_agent.tools.notifications import draft_and_send_ticket_email


class TicketAssignment(BaseModel):
    """Assignment result for routing a ticket."""
    
    team: str = Field(description="Assigned support team")
    queue: str = Field(description="Queue within the team: urgent, high, standard, low")
    agent: str = Field(description="Assigned agent or technician")
    estimated_response_time: str = Field(description="Estimated time to first response")
    sla_target: str = Field(description="SLA target for this ticket")
    routing_reason: str = Field(description="Reason for this assignment")


class TeamWorkload(BaseModel):
    """Current workload information for a support team."""
    
    team: str = Field(description="Team name")
    active_tickets: int = Field(description="Number of active tickets")
    available_agents: int = Field(description="Number of available agents")
    average_response_time: str = Field(description="Average response time")
    sla_compliance_rate: float = Field(description="SLA compliance percentage")
    queue_distribution: Dict[str, int] = Field(description="Tickets by queue priority")


def assign_ticket(
    ticket_id: str
) -> TicketAssignment:
    """
    Assign a ticket to the appropriate team and queue based on its classification.

    Args:
        ticket_id: The unique ticket identifier.
        
    Returns:
        TicketAssignment: Assignment result with team and queue information.
    """
    # Get classification data from the previous workflow step
    classification_data = get_step_data(ticket_id, "CLASSIFICATION")
    if not classification_data:
        # Handle cases where classification data is missing
        print(f"Error: Could not find classification data for ticket {ticket_id}")
        # Return a default or error assignment
        return TicketAssignment(
            team="General IT",
            queue="standard",
            agent="unassigned",
            estimated_response_time="N/A",
            sla_target="N/A",
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
    
    # This would use business rules and team availability to make assignment
    assignment = TicketAssignment(
        team=team,
        queue=queue,
        agent="auto-assign",
        estimated_response_time="2 hours",
        sla_target="4 hours",
        routing_reason=f"{category} issue matches {team} expertise"
    )
    
    # Update ticket in database with assignment
    try:
        update_ticket_fields(
            ticket_id=ticket_id,
            updates={
                "assigned_team": assignment.team,
                "status": "assigned",
                "assigned_agent": assignment.agent
            }
        )
        
        # Update workflow state
        update_workflow_state(
            ticket_id=ticket_id,
            current_step="ASSIGNMENT",
            next_step="FOLLOW_UP",
            step_data={"ASSIGNMENT": assignment.dict()},
            status="assigned"
        )
        
        print(f"Ticket {ticket_id} assigned to {assignment.team}")
        
        # Send team assignment notification
        ticket_data = {
            "subject": classification_data.get("subject", "No subject"),
            "priority": priority.upper(),
            "category": category,
            "assigned_team": assignment.team,
            "description": classification_data.get("description", "No description")
        }
        
        notify_team_assignment(ticket_id, ticket_data)
        
        # Send assignment email to user
        send_assignment_email_to_user(ticket_id, classification_data, assignment)
        
    except Exception as e:
        print(f"Error updating ticket assignment: {e}")
    
    return assignment


def send_assignment_email_to_user(
    ticket_id: str,
    classification_data: Dict[str, Any],
    assignment: TicketAssignment
) -> bool:
    """
    Send an assignment email to the user when a ticket is assigned to a team.
    
    Args:
        ticket_id: The ticket identifier
        classification_data: Classification data from previous step
        assignment: Assignment data from the assignment process
        
    Returns:
        bool: True if email was sent successfully
    """
    try:
        # Get user email from database (primary source) or classification data (fallback)
        user_email = get_ticket_user_email(ticket_id)
        if not user_email:
            user_email = classification_data.get("user_email", "user@company.com")
            print(f"⚠️ WARNING: Using fallback email from classification data: {user_email}")
        else:
            print(f"✅ Using email from database: {user_email}")
        
        # Prepare ticket data
        ticket_data = {
            "subject": classification_data.get("subject", "IT Support Request"),
            "priority": classification_data.get("priority", "MEDIUM"),
            "category": classification_data.get("category", "general"),
            "user_name": classification_data.get("user_name", "Valued Customer")
        }
        
        # Prepare assignment data
        assignment_data = {
            "team": assignment.team,
            "estimated_response_time": assignment.estimated_response_time,
            "sla_target": assignment.sla_target,
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


def notify_team_assignment(
    ticket_id: str,
    ticket_data: Dict[str, Any],
    previous_team: str = None
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
    try:
        success = send_team_assignment_notification(
            ticket_id=ticket_id,
            ticket_data=ticket_data,
            previous_team=previous_team
        )
        
        if success:
            print(f"✅ Team assignment notification sent for ticket {ticket_id}")
        else:
            print(f"❌ Failed to send team assignment notification for ticket {ticket_id}")
        
        return success
        
    except Exception as e:
        print(f"❌ Error sending team assignment notification: {e}")
        return False


def get_team_workload(
    team: str
) -> TeamWorkload:
    """
    Get current workload information for a support team.
    
    Args:
        team: The team name to check
        
    Returns:
        TeamWorkload: Current workload information
    """
    # This would query the ticketing system for real-time workload data
    return TeamWorkload(
        team=team,
        active_tickets=15,
        available_agents=3,
        average_response_time="1.5 hours",
        sla_compliance_rate=0.92,
        queue_distribution={
            "urgent": 2,
            "high": 5,
            "standard": 6,
            "low": 2
        }
    ) 