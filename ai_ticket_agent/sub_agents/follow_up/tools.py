"""Tools for the Follow-up Agent."""

from typing import Dict, List, Any
from pydantic import BaseModel, Field


class SatisfactionCheck(BaseModel):
    """Satisfaction check result."""
    
    resolved: bool = Field(description="Whether the issue was resolved")
    satisfaction_level: str = Field(description="Satisfaction level: very_satisfied, satisfied, neutral, dissatisfied, very_dissatisfied")
    resolution_quality: int = Field(description="Resolution quality rating 1-5")
    response_time_rating: int = Field(description="Response time rating 1-5")
    communication_rating: int = Field(description="Communication quality rating 1-5")


class FeedbackResult(BaseModel):
    """Feedback collection result."""
    
    feedback_text: str = Field(description="User feedback text")
    improvement_suggestions: List[str] = Field(description="Suggestions for improvement")
    knowledge_base_updates: List[str] = Field(description="Suggested knowledge base updates")
    process_improvements: List[str] = Field(description="Process improvement suggestions")


class TicketClosure(BaseModel):
    """Ticket closure information."""
    
    closed: bool = Field(description="Whether ticket was successfully closed")
    closure_reason: str = Field(description="Reason for closure")
    resolution_summary: str = Field(description="Summary of resolution")
    documentation_updated: bool = Field(description="Whether documentation was updated")
    follow_up_required: bool = Field(description="Whether follow-up is required")


class FollowUpAction(BaseModel):
    """Follow-up action to be taken."""
    
    action_type: str = Field(description="Type of follow-up: reminder, escalation, closure, satisfaction_survey")
    ticket_id: str = Field(description="Ticket identifier")
    target_time: str = Field(description="When to perform the follow-up")
    message_template: str = Field(description="Message template for the follow-up")
    recipients: List[str] = Field(description="Who to send the follow-up to")
    priority: str = Field(description="Follow-up priority: low, medium, high")


class FollowUpSchedule(BaseModel):
    """Schedule for follow-up actions."""
    
    ticket_id: str = Field(description="Ticket identifier")
    follow_ups: List[FollowUpAction] = Field(description="Scheduled follow-up actions")
    next_follow_up: str = Field(description="Next scheduled follow-up time")
    escalation_threshold: str = Field(description="Time threshold for escalation")
    auto_closure_threshold: str = Field(description="Time threshold for auto-closure")


class CustomerSatisfaction(BaseModel):
    """Customer satisfaction survey result."""
    
    ticket_id: str = Field(description="Ticket identifier")
    satisfaction_score: int = Field(description="Satisfaction score 1-5")
    response_time_rating: int = Field(description="Response time rating 1-5")
    resolution_quality_rating: int = Field(description="Resolution quality rating 1-5")
    overall_experience: str = Field(description="Overall experience description")
    feedback_comments: str = Field(description="Additional feedback comments")
    would_recommend: bool = Field(description="Whether customer would recommend the service")


def schedule_follow_up(
    ticket_id: str,
    priority: str,
    category: str,
    current_status: str
) -> FollowUpSchedule:
    """
    Schedule appropriate follow-up actions for a ticket.
    
    Args:
        ticket_id: The ticket identifier
        priority: The ticket priority level
        category: The ticket category
        current_status: Current ticket status
        
    Returns:
        FollowUpSchedule: Scheduled follow-up actions
    """
    # Define follow-up schedules based on priority and category
    follow_up_templates = {
        "critical": {
            "reminder_interval": "1 hour",
            "escalation_threshold": "2 hours",
            "auto_closure_threshold": "24 hours"
        },
        "high": {
            "reminder_interval": "2 hours",
            "escalation_threshold": "4 hours",
            "auto_closure_threshold": "48 hours"
        },
        "medium": {
            "reminder_interval": "4 hours",
            "escalation_threshold": "8 hours",
            "auto_closure_threshold": "72 hours"
        },
        "low": {
            "reminder_interval": "8 hours",
            "escalation_threshold": "24 hours",
            "auto_closure_threshold": "168 hours"
        }
    }
    
    template = follow_up_templates.get(priority, follow_up_templates["medium"])
    
    # Create follow-up actions
    follow_ups = [
        FollowUpAction(
            action_type="reminder",
            ticket_id=ticket_id,
            target_time=template["reminder_interval"],
            message_template=f"Reminder: Ticket {ticket_id} is still open and requires attention.",
            recipients=["assigned_agent"],
            priority=priority
        ),
        FollowUpAction(
            action_type="escalation",
            ticket_id=ticket_id,
            target_time=template["escalation_threshold"],
            message_template=f"Escalation: Ticket {ticket_id} may need escalation if not resolved.",
            recipients=["supervisor"],
            priority="high"
        )
    ]
    
    return FollowUpSchedule(
        ticket_id=ticket_id,
        follow_ups=follow_ups,
        next_follow_up=template["reminder_interval"],
        escalation_threshold=template["escalation_threshold"],
        auto_closure_threshold=template["auto_closure_threshold"]
    )


def send_satisfaction_survey(
    ticket_id: str,
    resolution_time: str,
    agent_name: str
) -> CustomerSatisfaction:
    """
    Send a customer satisfaction survey after ticket resolution.
    
    Args:
        ticket_id: The ticket identifier
        resolution_time: Time taken to resolve the ticket
        agent_name: Name of the agent who resolved the ticket
        
    Returns:
        CustomerSatisfaction: Survey result (mock data for now)
    """
    # This would send an actual survey and collect responses
    # For now, returning mock survey data
    return CustomerSatisfaction(
        ticket_id=ticket_id,
        satisfaction_score=4,
        response_time_rating=4,
        resolution_quality_rating=5,
        overall_experience="Good experience with quick resolution",
        feedback_comments="The agent was helpful and resolved my issue quickly.",
        would_recommend=True
    )


def check_follow_up_due(
    current_time: str
) -> List[FollowUpAction]:
    """
    Check which follow-up actions are due at the current time.
    
    Args:
        current_time: Current timestamp
        
    Returns:
        List[FollowUpAction]: List of follow-up actions that are due
    """
    # This would query the database for due follow-ups
    # For now, returning empty list
    return [] 