"""Tools for the Ticket Assignment Agent."""

from typing import Dict, List, Any
from pydantic import BaseModel, Field


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
    ticket_id: str,
    classification: Dict[str, Any],
    priority: str,
    category: str
) -> TicketAssignment:
    """
    Assign a ticket to the appropriate team and queue based on classification.
    
    Args:
        ticket_id: The unique ticket identifier
        classification: The classification result from classifier agent
        priority: The ticket priority level
        category: The ticket category
        
    Returns:
        TicketAssignment: Assignment result with team and queue information
    """
    # This would use business rules and team availability to make assignment
    return TicketAssignment(
        team="Network Support",
        queue="standard",
        agent="auto-assign",
        estimated_response_time="2 hours",
        sla_target="4 hours",
        routing_reason="VPN connectivity issue matches network support expertise"
    )


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