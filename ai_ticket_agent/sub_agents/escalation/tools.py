"""Tools for the Escalation Agent."""

from typing import Dict, List, Any
from pydantic import BaseModel, Field


class EscalationTrigger(BaseModel):
    """Escalation trigger information."""
    
    trigger_type: str = Field(description="Type of escalation trigger")
    severity: str = Field(description="Severity level: low, medium, high, critical")
    description: str = Field(description="Description of the trigger")
    recommended_action: str = Field(description="Recommended escalation action")
    urgency: str = Field(description="Urgency level")


class EscalationResult(BaseModel):
    """Result of escalation action."""
    
    escalated: bool = Field(description="Whether ticket was escalated")
    escalation_level: str = Field(description="Escalation level: L1, L2, L3, Emergency")
    assigned_to: str = Field(description="Person or team assigned")
    reason: str = Field(description="Reason for escalation")
    estimated_response: str = Field(description="Estimated response time")


class SecurityIssue(BaseModel):
    """Security issue information."""
    
    issue_type: str = Field(description="Type of security issue")
    severity: str = Field(description="Security severity level")
    affected_systems: List[str] = Field(description="Affected systems or users")
    immediate_actions: List[str] = Field(description="Immediate actions required")
    notification_required: bool = Field(description="Whether management notification is required")


class EscalationDecision(BaseModel):
    """Escalation decision and routing information."""
    
    should_escalate: bool = Field(description="Whether the ticket should be escalated")
    escalation_level: str = Field(description="Escalation level: tier2, tier3, management, vendor")
    escalation_reason: str = Field(description="Reason for escalation")
    target_team: str = Field(description="Target team for escalation")
    priority_adjustment: str = Field(description="Priority adjustment if any")
    estimated_resolution_time: str = Field(description="Estimated time to resolution")
    escalation_notes: str = Field(description="Notes for the escalated team")


class EscalationCriteria(BaseModel):
    """Criteria for determining escalation."""
    
    sla_breach: bool = Field(description="Whether SLA is breached")
    complexity_score: float = Field(description="Complexity score 0.0-1.0")
    business_impact: str = Field(description="Business impact assessment")
    technical_difficulty: str = Field(description="Technical difficulty level")
    user_urgency: str = Field(description="User's urgency level")
    escalation_history: List[str] = Field(description="Previous escalation attempts")


def evaluate_escalation_need(
    ticket_id: str,
    current_status: str,
    time_open: str,
    priority: str,
    category: str,
    resolution_attempts: List[str]
) -> EscalationDecision:
    """
    Evaluate whether a ticket needs to be escalated based on various criteria.
    
    Args:
        ticket_id: The ticket identifier
        current_status: Current ticket status
        time_open: How long the ticket has been open
        priority: Current priority level
        category: Ticket category
        resolution_attempts: Previous resolution attempts
        
    Returns:
        EscalationDecision: Decision on whether and how to escalate
    """
    # This would use business rules and SLA policies to determine escalation
    should_escalate = False
    escalation_level = "tier2"
    escalation_reason = "Standard routing"
    
    # Check for escalation triggers
    if priority == "critical" and "4 hours" in time_open:
        should_escalate = True
        escalation_level = "tier3"
        escalation_reason = "Critical ticket approaching SLA breach"
    elif len(resolution_attempts) >= 3:
        should_escalate = True
        escalation_level = "tier2"
        escalation_reason = "Multiple resolution attempts without success"
    
    return EscalationDecision(
        should_escalate=should_escalate,
        escalation_level=escalation_level,
        escalation_reason=escalation_reason,
        target_team="Advanced Support" if escalation_level == "tier3" else "Tier 2 Support",
        priority_adjustment="maintain",
        estimated_resolution_time="2-4 hours",
        escalation_notes=f"Ticket {ticket_id} escalated due to {escalation_reason}"
    )


def get_escalation_criteria(
    ticket_data: Dict[str, Any]
) -> EscalationCriteria:
    """
    Analyze ticket data to determine escalation criteria.
    
    Args:
        ticket_data: Complete ticket data including history and context
        
    Returns:
        EscalationCriteria: Analysis of escalation criteria
    """
    # This would analyze the ticket data to extract escalation criteria
    return EscalationCriteria(
        sla_breach=False,
        complexity_score=0.6,
        business_impact="Individual productivity",
        technical_difficulty="Medium",
        user_urgency="Medium",
        escalation_history=[]
    ) 