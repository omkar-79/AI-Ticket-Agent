"""Tools for the SLA Tracking Agent."""

from typing import Dict, List, Any
from pydantic import BaseModel, Field


class SLAMetrics(BaseModel):
    """SLA metrics for a ticket or team."""
    
    ticket_id: str = Field(description="Ticket identifier")
    sla_target: str = Field(description="SLA target time")
    time_elapsed: str = Field(description="Time elapsed since ticket creation")
    time_remaining: str = Field(description="Time remaining to meet SLA")
    sla_status: str = Field(description="SLA status: on_track, at_risk, breached")
    breach_probability: float = Field(description="Probability of SLA breach 0.0-1.0")
    priority_adjustment_needed: bool = Field(description="Whether priority adjustment is needed")


class SLAAlert(BaseModel):
    """SLA alert notification."""
    
    alert_type: str = Field(description="Alert type: warning, breach, recovery")
    ticket_id: str = Field(description="Affected ticket ID")
    message: str = Field(description="Alert message")
    severity: str = Field(description="Alert severity: low, medium, high, critical")
    recommended_action: str = Field(description="Recommended action to take")
    escalation_needed: bool = Field(description="Whether escalation is needed")


class TeamSLAReport(BaseModel):
    """SLA performance report for a team."""
    
    team: str = Field(description="Team name")
    period: str = Field(description="Reporting period")
    total_tickets: int = Field(description="Total tickets in period")
    sla_compliance_rate: float = Field(description="SLA compliance percentage")
    average_resolution_time: str = Field(description="Average time to resolution")
    breached_tickets: int = Field(description="Number of breached tickets")
    at_risk_tickets: int = Field(description="Number of tickets at risk")


def check_sla_status(
    ticket_id: str,
    priority: str,
    category: str,
    created_time: str
) -> SLAMetrics:
    """
    Check the SLA status for a specific ticket.
    
    Args:
        ticket_id: The ticket identifier
        priority: The ticket priority level
        category: The ticket category
        created_time: When the ticket was created
        
    Returns:
        SLAMetrics: Current SLA metrics for the ticket
    """
    # This would calculate actual SLA metrics based on business rules
    # For now, returning sample data
    sla_targets = {
        "critical": "2 hours",
        "high": "4 hours", 
        "medium": "8 hours",
        "low": "24 hours"
    }
    
    sla_target = sla_targets.get(priority, "8 hours")
    time_elapsed = "3 hours"  # This would be calculated from created_time
    time_remaining = "1 hour"  # This would be calculated
    sla_status = "at_risk" if priority == "critical" else "on_track"
    breach_probability = 0.3 if sla_status == "at_risk" else 0.1
    
    return SLAMetrics(
        ticket_id=ticket_id,
        sla_target=sla_target,
        time_elapsed=time_elapsed,
        time_remaining=time_remaining,
        sla_status=sla_status,
        breach_probability=breach_probability,
        priority_adjustment_needed=sla_status == "at_risk"
    )


def generate_sla_alert(
    ticket_id: str,
    sla_metrics: Dict[str, Any]
) -> SLAAlert:
    """
    Generate an SLA alert based on current metrics.
    
    Args:
        ticket_id: The ticket identifier
        sla_metrics: Current SLA metrics
        
    Returns:
        SLAAlert: Generated alert notification
    """
    sla_status = sla_metrics.get("sla_status", "on_track")
    time_remaining = sla_metrics.get("time_remaining", "unknown")
    
    if sla_status == "breached":
        alert_type = "breach"
        severity = "critical"
        message = f"SLA breached for ticket {ticket_id}. Immediate attention required."
        recommended_action = "Escalate immediately and notify management"
        escalation_needed = True
    elif sla_status == "at_risk":
        alert_type = "warning"
        severity = "high"
        message = f"Ticket {ticket_id} at risk of SLA breach. {time_remaining} remaining."
        recommended_action = "Review priority and consider escalation"
        escalation_needed = False
    else:
        alert_type = "info"
        severity = "low"
        message = f"Ticket {ticket_id} on track for SLA compliance."
        recommended_action = "Continue monitoring"
        escalation_needed = False
    
    return SLAAlert(
        alert_type=alert_type,
        ticket_id=ticket_id,
        message=message,
        severity=severity,
        recommended_action=recommended_action,
        escalation_needed=escalation_needed
    )


def get_team_sla_report(
    team: str,
    period: str
) -> TeamSLAReport:
    """
    Generate SLA performance report for a team.
    
    Args:
        team: The team name
        period: The reporting period
        
    Returns:
        TeamSLAReport: SLA performance report
    """
    # This would query the ticketing system for actual SLA data
    return TeamSLAReport(
        team=team,
        period=period,
        total_tickets=45,
        sla_compliance_rate=0.89,
        average_resolution_time="3.2 hours",
        breached_tickets=3,
        at_risk_tickets=2
    ) 