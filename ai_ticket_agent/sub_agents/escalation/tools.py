"""Tools for the Escalation Agent."""

from typing import Dict, List, Any
from pydantic import BaseModel, Field
from ai_ticket_agent.tools.monitoring import (
    check_ticket_for_escalation,
    process_escalation_trigger,
    monitor_all_active_tickets,
    EscalationTrigger
)
from ai_ticket_agent.tools.database import get_ticket, search_tickets
from datetime import datetime


class EscalationTrigger(BaseModel):
    """Escalation trigger information."""
    
    ticket_id: str = Field(description="Ticket identifier")
    trigger_type: str = Field(description="Type of escalation trigger")
    severity: str = Field(description="Severity level: low, medium, high, critical")
    description: str = Field(description="Description of the trigger")
    recommended_action: str = Field(description="Recommended escalation action")
    urgency: str = Field(description="Urgency level", default="medium")
    created_at: str = Field(description="Timestamp when trigger was created")


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
    # Use the monitoring system to check for escalation triggers
    escalation_trigger = check_ticket_for_escalation(ticket_id)
    
    if escalation_trigger:
        # Determine escalation level based on trigger severity
        if escalation_trigger.severity == "critical":
            escalation_level = "tier3"
            target_team = "Senior Support / Management"
            priority_adjustment = "upgrade_to_critical"
            estimated_resolution_time = "1-2 hours"
        elif escalation_trigger.severity == "high":
            escalation_level = "tier2"
            target_team = "Advanced Support"
            priority_adjustment = "maintain_or_upgrade"
            estimated_resolution_time = "2-4 hours"
        else:
            escalation_level = "tier2"
            target_team = "Tier 2 Support"
            priority_adjustment = "maintain"
            estimated_resolution_time = "4-8 hours"
        
        return EscalationDecision(
            should_escalate=True,
            escalation_level=escalation_level,
            escalation_reason=escalation_trigger.description,
            target_team=target_team,
            priority_adjustment=priority_adjustment,
            estimated_resolution_time=estimated_resolution_time,
            escalation_notes=f"Auto-escalated due to {escalation_trigger.trigger_type}: {escalation_trigger.description}"
        )
    else:
        return EscalationDecision(
            should_escalate=False,
            escalation_level="none",
            escalation_reason="No escalation criteria met",
            target_team="none",
            priority_adjustment="maintain",
            estimated_resolution_time="standard",
            escalation_notes="Ticket does not require escalation at this time"
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


def run_escalation_monitoring() -> Dict[str, Any]:
    """
    Run escalation monitoring for all active tickets.
    
    Returns:
        Dict containing escalation monitoring results
    """
    # Use the monitoring system to check all tickets
    monitoring_results = monitor_all_active_tickets()
    
    escalation_results = []
    
    # Process any escalation triggers found
    for trigger_data in monitoring_results["escalation_triggers"]:
        trigger = EscalationTrigger(**trigger_data)
        result = process_escalation_trigger(trigger)
        escalation_results.append(result)
    
    return {
        "monitoring_time": monitoring_results["monitoring_time"],
        "tickets_checked": monitoring_results["tickets_checked"],
        "escalations_found": len(monitoring_results["escalation_triggers"]),
        "escalations_processed": len(escalation_results),
        "escalation_results": escalation_results
    }


def get_tickets_at_risk() -> List[Dict[str, Any]]:
    """
    Get all tickets that are at risk of escalation.
    
    Returns:
        List of tickets at risk with escalation details
    """
    # Get all open tickets
    open_tickets = search_tickets(status="open", limit=100)
    in_progress_tickets = search_tickets(status="in_progress", limit=100)
    all_active_tickets = open_tickets + in_progress_tickets
    
    at_risk_tickets = []
    
    for ticket in all_active_tickets:
        # Check if this ticket needs escalation
        escalation_trigger = check_ticket_for_escalation(ticket.id)
        if escalation_trigger:
            at_risk_tickets.append({
                "ticket_id": ticket.id,
                "subject": ticket.subject,
                "priority": ticket.priority,
                "category": ticket.category,
                "status": ticket.status,
                "created_at": ticket.created_at,
                "assigned_team": ticket.assigned_team,
                "escalation_trigger": escalation_trigger.dict(),
                "risk_level": escalation_trigger.severity
            })
    
    return at_risk_tickets


def manual_escalate_ticket(
    ticket_id: str,
    escalation_reason: str,
    target_team: str,
    escalation_level: str = "tier2"
) -> Dict[str, Any]:
    """
    Manually escalate a ticket.
    
    Args:
        ticket_id: The ticket identifier
        escalation_reason: Reason for escalation
        target_team: Target team for escalation
        escalation_level: Escalation level
        
    Returns:
        Dict containing escalation result
    """
    # Create a manual escalation trigger
    manual_trigger = EscalationTrigger(
        ticket_id=ticket_id,
        trigger_type="manual_escalation",
        severity="high" if escalation_level in ["tier3", "management"] else "medium",
        description=f"Manual escalation: {escalation_reason}",
        recommended_action=f"Escalate to {target_team}",
        urgency="high" if escalation_level in ["tier3", "management"] else "medium",
        created_at=datetime.now().isoformat()
    )
    
    # Process the escalation
    result = process_escalation_trigger(manual_trigger)
    
    return {
        "ticket_id": ticket_id,
        "escalation_processed": True,
        "escalation_level": escalation_level,
        "target_team": target_team,
        "reason": escalation_reason,
        "result": result
    } 