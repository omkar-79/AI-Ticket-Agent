"""Tools for the SLA Tracking Agent."""

from typing import Dict, List, Any
from pydantic import BaseModel, Field
from ai_ticket_agent.tools.monitoring import (
    check_ticket_sla_status,
    process_sla_alert,
    monitor_all_active_tickets,
    SLAAlert
)
from ai_ticket_agent.tools.database import get_ticket, search_tickets


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
    # Use the monitoring system to check SLA status
    sla_alert = check_ticket_sla_status(ticket_id)
    
    # Get ticket data for additional context
    ticket = get_ticket(ticket_id)
    if not ticket:
        return SLAMetrics(
            ticket_id=ticket_id,
            sla_target="unknown",
            time_elapsed="unknown",
            time_remaining="unknown",
            sla_status="unknown",
            breach_probability=0.0,
            priority_adjustment_needed=False
        )
    
    # Determine SLA status based on alert
    if sla_alert:
        if sla_alert.alert_type == "breach":
            sla_status = "breached"
            breach_probability = 1.0
            priority_adjustment_needed = True
        elif sla_alert.severity == "high":
            sla_status = "at_risk"
            breach_probability = 0.8
            priority_adjustment_needed = True
        else:
            sla_status = "at_risk"
            breach_probability = 0.5
            priority_adjustment_needed = False
    else:
        sla_status = "on_track"
        breach_probability = 0.1
        priority_adjustment_needed = False
    
    return SLAMetrics(
        ticket_id=ticket_id,
        sla_target=ticket.sla_target,
        time_elapsed="calculated",  # Would be calculated from created_time
        time_remaining=sla_alert.time_remaining if sla_alert else "sufficient",
        sla_status=sla_status,
        breach_probability=breach_probability,
        priority_adjustment_needed=priority_adjustment_needed
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
    # Use the monitoring system to check for SLA alerts
    sla_alert = check_ticket_sla_status(ticket_id)
    
    if sla_alert:
        # Determine if escalation is needed
        escalation_needed = sla_alert.severity in ["critical", "high"]
        
        return SLAAlert(
            alert_type=sla_alert.alert_type,
            ticket_id=ticket_id,
            message=sla_alert.message,
            severity=sla_alert.severity,
            recommended_action="Escalate immediately" if escalation_needed else "Review priority",
            escalation_needed=escalation_needed
        )
    else:
        return SLAAlert(
            alert_type="info",
            ticket_id=ticket_id,
            message=f"Ticket {ticket_id} on track for SLA compliance",
            severity="low",
            recommended_action="Continue monitoring",
            escalation_needed=False
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
    # Get all tickets for the team
    team_tickets = search_tickets(assigned_team=team, limit=1000)
    
    total_tickets = len(team_tickets)
    breached_tickets = 0
    at_risk_tickets = 0
    resolved_tickets = 0
    
    # Analyze each ticket
    for ticket in team_tickets:
        sla_alert = check_ticket_sla_status(ticket.id)
        if sla_alert:
            if sla_alert.alert_type == "breach":
                breached_tickets += 1
            elif sla_alert.severity in ["high", "medium"]:
                at_risk_tickets += 1
        
        if ticket.status in ["resolved", "closed"]:
            resolved_tickets += 1
    
    # Calculate compliance rate
    if total_tickets > 0:
        sla_compliance_rate = (total_tickets - breached_tickets) / total_tickets
    else:
        sla_compliance_rate = 1.0
    
    return TeamSLAReport(
        team=team,
        period=period,
        total_tickets=total_tickets,
        sla_compliance_rate=sla_compliance_rate,
        average_resolution_time="calculated",  # Would be calculated from actual data
        breached_tickets=breached_tickets,
        at_risk_tickets=at_risk_tickets
    )


def run_sla_monitoring() -> Dict[str, Any]:
    """
    Run SLA monitoring for all active tickets.
    
    Returns:
        Dict containing SLA monitoring results
    """
    # Use the monitoring system to check all tickets
    monitoring_results = monitor_all_active_tickets()
    
    sla_results = []
    
    # Process any SLA alerts found
    for alert_data in monitoring_results["sla_alerts"]:
        alert = SLAAlert(**alert_data)
        result = process_sla_alert(alert)
        sla_results.append(result)
    
    return {
        "monitoring_time": monitoring_results["monitoring_time"],
        "tickets_checked": monitoring_results["tickets_checked"],
        "sla_alerts_found": len(monitoring_results["sla_alerts"]),
        "sla_alerts_processed": len(sla_results),
        "sla_results": sla_results
    }


def get_tickets_with_sla_issues() -> List[Dict[str, Any]]:
    """
    Get all tickets with SLA issues.
    
    Returns:
        List of tickets with SLA issues
    """
    # Get all active tickets
    open_tickets = search_tickets(status="open", limit=100)
    in_progress_tickets = search_tickets(status="in_progress", limit=100)
    all_active_tickets = open_tickets + in_progress_tickets
    
    tickets_with_issues = []
    
    for ticket in all_active_tickets:
        # Check if this ticket has SLA issues
        sla_alert = check_ticket_sla_status(ticket.id)
        if sla_alert:
            tickets_with_issues.append({
                "ticket_id": ticket.id,
                "subject": ticket.subject,
                "priority": ticket.priority,
                "category": ticket.category,
                "status": ticket.status,
                "created_at": ticket.created_at,
                "assigned_team": ticket.assigned_team,
                "sla_alert": sla_alert.dict(),
                "issue_severity": sla_alert.severity
            })
    
    return tickets_with_issues


def get_sla_summary() -> Dict[str, Any]:
    """
    Get a summary of SLA status across all tickets.
    
    Returns:
        Dict containing SLA summary
    """
    # Run monitoring to get current status
    monitoring_results = monitor_all_active_tickets()
    
    # Get all active tickets for total count
    open_tickets = search_tickets(status="open", limit=1000)
    in_progress_tickets = search_tickets(status="in_progress", limit=1000)
    total_active = len(open_tickets) + len(in_progress_tickets)
    
    # Count by severity
    critical_alerts = len([a for a in monitoring_results["sla_alerts"] if a["severity"] == "critical"])
    high_alerts = len([a for a in monitoring_results["sla_alerts"] if a["severity"] == "high"])
    medium_alerts = len([a for a in monitoring_results["sla_alerts"] if a["severity"] == "medium"])
    
    return {
        "monitoring_time": monitoring_results["monitoring_time"],
        "total_active_tickets": total_active,
        "tickets_with_sla_issues": len(monitoring_results["sla_alerts"]),
        "critical_alerts": critical_alerts,
        "high_alerts": high_alerts,
        "medium_alerts": medium_alerts,
        "sla_compliance_rate": (total_active - len(monitoring_results["sla_alerts"])) / total_active if total_active > 0 else 1.0
    } 