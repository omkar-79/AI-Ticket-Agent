"""Monitoring system for ticket escalation and SLA tracking."""

import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from ai_ticket_agent.tools.database import init_database, get_ticket, update_ticket_fields
from ai_ticket_agent.tools.notifications import send_slack_notification, send_email_notification


class MonitoringState(BaseModel):
    """State for monitoring agents."""
    
    last_check_time: str = Field(description="Last time monitoring was performed")
    active_monitors: List[str] = Field(description="List of active monitoring ticket IDs")
    escalation_queue: List[str] = Field(description="Tickets queued for escalation")
    sla_alerts: List[str] = Field(description="Tickets with SLA alerts")


class EscalationTrigger(BaseModel):
    """Escalation trigger information."""
    
    ticket_id: str = Field(description="Ticket identifier")
    trigger_type: str = Field(description="Type of escalation trigger")
    severity: str = Field(description="Severity level: low, medium, high, critical")
    description: str = Field(description="Description of the trigger")
    recommended_action: str = Field(description="Recommended escalation action")
    created_at: str = Field(description="When the trigger was created")
    urgency: str = Field(default="medium", description="Urgency level")


class SLAAlert(BaseModel):
    """SLA alert information."""
    
    ticket_id: str = Field(description="Ticket identifier")
    alert_type: str = Field(description="Alert type: warning, breach, recovery")
    message: str = Field(description="Alert message")
    severity: str = Field(description="Alert severity: low, medium, high, critical")
    time_remaining: str = Field(description="Time remaining to SLA breach")
    created_at: str = Field(description="When the alert was created")


def get_monitoring_state() -> MonitoringState:
    """Get the current monitoring state."""
    # This would typically be stored in a database or session state
    # For now, returning a default state
    return MonitoringState(
        last_check_time=datetime.now().isoformat(),
        active_monitors=[],
        escalation_queue=[],
        sla_alerts=[]
    )


def update_monitoring_state(state: MonitoringState):
    """Update the monitoring state."""
    # This would persist the state to database or session
    pass


def calculate_time_elapsed(created_time: str) -> timedelta:
    """Calculate time elapsed since ticket creation."""
    created_dt = datetime.fromisoformat(created_time)
    return datetime.now() - created_dt


def parse_sla_target(sla_target: str) -> timedelta:
    """Parse SLA target string into timedelta."""
    # Handle formats like "2 hours", "8 hours", "24 hours"
    if "hour" in sla_target.lower():
        hours = int(sla_target.split()[0])
        return timedelta(hours=hours)
    elif "day" in sla_target.lower():
        days = int(sla_target.split()[0])
        return timedelta(days=days)
    else:
        # Default to 8 hours
        return timedelta(hours=8)


def check_ticket_for_escalation(ticket_id: str) -> Optional[EscalationTrigger]:
    """
    Check if a ticket needs escalation based on various criteria.
    
    Args:
        ticket_id: The ticket identifier
        
    Returns:
        Optional[EscalationTrigger]: Escalation trigger if needed, None otherwise
    """
    init_database()
    
    # Get ticket data
    ticket = get_ticket(ticket_id)
    if not ticket:
        return None
    
    # Calculate time elapsed
    time_elapsed = calculate_time_elapsed(ticket.created_at)
    sla_target = parse_sla_target(ticket.sla_target)
    
    # Check escalation criteria
    escalation_triggers = []
    
    # 1. SLA breach or approaching breach
    if time_elapsed >= sla_target:
        escalation_triggers.append({
            "type": "sla_breach",
            "severity": "critical",
            "description": f"SLA breached - ticket open for {time_elapsed}",
            "action": "Immediate escalation to senior support"
        })
    elif time_elapsed >= sla_target * 0.8:  # 80% of SLA time
        escalation_triggers.append({
            "type": "sla_warning",
            "severity": "high",
            "description": f"Approaching SLA breach - {time_elapsed} elapsed",
            "action": "Review and consider escalation"
        })
    
    # 2. High priority tickets that are stuck
    if ticket.priority in ["critical", "high"] and ticket.status == "open":
        if time_elapsed >= timedelta(hours=2):
            escalation_triggers.append({
                "type": "priority_stuck",
                "severity": "high",
                "description": f"High priority ticket stuck for {time_elapsed}",
                "action": "Escalate to senior support"
            })
    
    # 3. Security-related issues
    if ticket.category == "security":
        escalation_triggers.append({
            "type": "security_issue",
            "severity": "critical",
            "description": "Security-related ticket requires immediate attention",
            "action": "Escalate to security team immediately"
        })
    
    # Return the highest priority trigger
    if escalation_triggers:
        # Sort by severity (critical > high > medium > low)
        severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        escalation_triggers.sort(key=lambda x: severity_order.get(x["severity"], 0), reverse=True)
        
        trigger = escalation_triggers[0]
        return EscalationTrigger(
            ticket_id=ticket_id,
            trigger_type=trigger["type"],
            severity=trigger["severity"],
            description=trigger["description"],
            recommended_action=trigger["action"],
            created_at=datetime.now().isoformat()
        )
    
    return None


def check_ticket_sla_status(ticket_id: str) -> Optional[SLAAlert]:
    """
    Check SLA status for a ticket and generate alerts if needed.
    
    Args:
        ticket_id: The ticket identifier
        
    Returns:
        Optional[SLAAlert]: SLA alert if needed, None otherwise
    """
    init_database()
    
    # Get ticket data
    ticket = get_ticket(ticket_id)
    if not ticket or ticket.status in ["resolved", "closed"]:
        return None
    
    # Calculate time metrics
    time_elapsed = calculate_time_elapsed(ticket.created_at)
    sla_target = parse_sla_target(ticket.sla_target)
    time_remaining = sla_target - time_elapsed
    
    # Determine alert type and severity
    if time_remaining <= timedelta(0):  # SLA breached
        alert_type = "breach"
        severity = "critical"
        message = f"SLA BREACHED for ticket {ticket_id}. Ticket open for {time_elapsed}"
        time_remaining_str = "BREACHED"
    elif time_remaining <= timedelta(hours=1):  # Less than 1 hour remaining
        alert_type = "warning"
        severity = "high"
        message = f"CRITICAL: Ticket {ticket_id} has {time_remaining} remaining"
        time_remaining_str = str(time_remaining)
    elif time_remaining <= sla_target * 0.2:  # Less than 20% remaining
        alert_type = "warning"
        severity = "medium"
        message = f"WARNING: Ticket {ticket_id} has {time_remaining} remaining"
        time_remaining_str = str(time_remaining)
    else:
        return None  # No alert needed
    
    return SLAAlert(
        ticket_id=ticket_id,
        alert_type=alert_type,
        message=message,
        severity=severity,
        time_remaining=time_remaining_str,
        created_at=datetime.now().isoformat()
    )


def monitor_all_active_tickets() -> Dict[str, Any]:
    """
    Monitor all active tickets for escalation and SLA issues.
    
    Returns:
        Dict containing monitoring results
    """
    init_database()
    
    db_path = os.getenv("DATABASE_URL", "sqlite:///./helpdesk.db").replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all open tickets
    cursor.execute('''
        SELECT id FROM tickets 
        WHERE status IN ('open', 'in_progress') 
        ORDER BY created_at ASC
    ''')
    
    open_tickets = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    escalation_triggers = []
    sla_alerts = []
    
    # Check each ticket
    for ticket_id in open_tickets:
        # Check for escalation
        escalation = check_ticket_for_escalation(ticket_id)
        if escalation:
            escalation_triggers.append(escalation)
        
        # Check SLA status
        sla_alert = check_ticket_sla_status(ticket_id)
        if sla_alert:
            sla_alerts.append(sla_alert)
    
    return {
        "monitoring_time": datetime.now().isoformat(),
        "tickets_checked": len(open_tickets),
        "escalation_triggers": [trigger.dict() for trigger in escalation_triggers],
        "sla_alerts": [alert.dict() for alert in sla_alerts],
        "summary": {
            "escalations_needed": len(escalation_triggers),
            "sla_alerts": len(sla_alerts)
        }
    }


def process_escalation_trigger(trigger: 'EscalationTrigger') -> Dict[str, Any]:
    """
    Process an escalation trigger and take appropriate action.
    
    Args:
        trigger: The escalation trigger to process
        
    Returns:
        Dict containing the action taken
    """
    # Debug: Check trigger object contents
    print(f"DEBUG: process_escalation_trigger called")
    print(f"DEBUG: trigger type: {type(trigger)}")
    print(f"DEBUG: trigger object: {trigger}")
    print(f"DEBUG: trigger fields: {trigger.__dict__ if hasattr(trigger, '__dict__') else 'No __dict__'}")
    print(f"DEBUG: trigger attributes: {[attr for attr in dir(trigger) if not attr.startswith('_')]}")
    
    # Check if ticket_id exists
    if not hasattr(trigger, 'ticket_id'):
        print(f"DEBUG: ERROR - trigger has no ticket_id attribute!")
        print(f"DEBUG: Available attributes: {[attr for attr in dir(trigger) if not attr.startswith('_')]}")
        return {"error": "EscalationTrigger missing ticket_id"}
    
    # Update ticket priority if needed
    ticket = get_ticket(trigger.ticket_id)
    if not ticket:
        return {"error": "Ticket not found"}
    
    actions_taken = []
    
    # 1. Update ticket priority for critical escalations
    if trigger.severity == "critical" and ticket.priority != "critical":
        update_ticket_fields(
            ticket_id=trigger.ticket_id,
            updates={"priority": "critical"},
            updated_by="escalation_agent"
        )
        actions_taken.append("Priority upgraded to critical")
    
    # 2. Assign team if recommended_action includes a team
    assigned_team = None
    if trigger.recommended_action and "Escalate to" in trigger.recommended_action:
        # Extract team name from action string
        parts = trigger.recommended_action.split("Escalate to", 1)
        if len(parts) > 1:
            assigned_team = parts[1].strip().replace("team", "").replace("immediately", "").strip()
            if assigned_team:
                update_ticket_fields(
                    ticket_id=trigger.ticket_id,
                    updates={"assigned_team": assigned_team},
                    updated_by="escalation_agent"
                )
                actions_taken.append(f"Assigned team updated to {assigned_team}")
    
    # 3. Send notifications
    if trigger.severity in ["critical", "high"]:
        # Debug print for Slack channel and message
        channel_id = get_slack_channel_id()
        # Compose informative Slack message
        slack_message = (
            f"🚨 ESCALATION ALERT for Ticket *{ticket.id}*\n"
            f"*Subject:* {ticket.subject}\n"
            f"*Priority:* {ticket.priority}\n"
            f"*Category:* {ticket.category}\n"
            f"*Status:* {ticket.status}\n"
            f"*Trigger:* {trigger.trigger_type}\n"
            f"*Severity:* {trigger.severity}\n"
            f"*Description:* {trigger.description}\n"
            f"*Recommended Action:* {trigger.recommended_action}"
        )
        print(f"DEBUG: About to call send_slack_notification")
        print(f"DEBUG: channel_id: {channel_id}")
        print(f"DEBUG: slack_message: {slack_message}")
        print(f"DEBUG: send_slack_notification parameters: channel='{channel_id}', message='{slack_message}'")
        
        # Call send_slack_notification with correct parameters
        send_slack_notification(channel_id, slack_message)
        actions_taken.append("Slack notification sent")
        
        # Send email to assigned team
        if ticket.assigned_team:
            email_subject = f"Ticket Escalation: {trigger.ticket_id}"
            email_body = f"""
            <h2>Ticket Escalation Alert</h2>
            <p><strong>Ticket ID:</strong> {trigger.ticket_id}</p>
            <p><strong>Subject:</strong> {ticket.subject}</p>
            <p><strong>Trigger:</strong> {trigger.trigger_type}</p>
            <p><strong>Severity:</strong> {trigger.severity}</p>
            <p><strong>Description:</strong> {trigger.description}</p>
            <p><strong>Recommended Action:</strong> {trigger.recommended_action}</p>
            """
            send_email_notification(
                to_email=ticket.user_email,
                subject=email_subject,
                body=email_body,
                html_body=email_body
            )
            actions_taken.append("Email notification sent")
    
    return {
        "ticket_id": trigger.ticket_id,
        "trigger_processed": True,
        "actions_taken": actions_taken,
        "timestamp": datetime.now().isoformat()
    }


def process_sla_alert(alert: 'SLAAlert') -> Dict[str, Any]:
    """
    Process an SLA alert and take appropriate action.
    
    Args:
        alert: The SLA alert to process
        
    Returns:
        Dict containing the action taken
    """
    # Debug: Check alert object contents
    print(f"DEBUG: process_sla_alert called")
    print(f"DEBUG: alert type: {type(alert)}")
    print(f"DEBUG: alert object: {alert}")
    print(f"DEBUG: alert fields: {alert.__dict__ if hasattr(alert, '__dict__') else 'No __dict__'}")
    
    ticket = get_ticket(alert.ticket_id)
    if not ticket:
        return {"error": "Ticket not found"}
    
    actions_taken = []
    
    # 1. Send notifications based on severity
    if alert.severity == "critical":
        channel_id = get_slack_channel_id()
        slack_message = f"🚨 CRITICAL SLA BREACH: {alert.message}\nTicket: {alert.ticket_id}"
        print(f"DEBUG: About to call send_slack_notification for SLA alert")
        print(f"DEBUG: channel_id: {channel_id}")
        print(f"DEBUG: slack_message: {slack_message}")
        print(f"DEBUG: send_slack_notification parameters: channel='{channel_id}', message='{slack_message}'")
        
        send_slack_notification(channel_id, slack_message)
        actions_taken.append("Critical Slack alert sent")
        
        # Escalate automatically
        escalation_trigger = EscalationTrigger(
            ticket_id=alert.ticket_id,
            trigger_type="sla_breach",
            severity="critical",
            description=f"SLA breached - {alert.message}",
            recommended_action="Immediate escalation to senior support",
            created_at=datetime.now().isoformat()
        )
        process_escalation_trigger(escalation_trigger)
        actions_taken.append("Automatic escalation triggered")
        
    elif alert.severity == "high":
        channel_id = get_slack_channel_id()
        slack_message = f"⚠️ HIGH PRIORITY SLA WARNING: {alert.message}\nTicket: {alert.ticket_id}"
        print(f"DEBUG: About to call send_slack_notification for SLA warning")
        print(f"DEBUG: channel_id: {channel_id}")
        print(f"DEBUG: slack_message: {slack_message}")
        
        send_slack_notification(channel_id, slack_message)
        actions_taken.append("High priority Slack warning sent")
        
    elif alert.severity == "medium":
        channel_id = get_slack_channel_id()
        slack_message = f"⚠️ SLA WARNING: {alert.message}\nTicket: {alert.ticket_id}"
        print(f"DEBUG: About to call send_slack_notification for SLA warning")
        print(f"DEBUG: channel_id: {channel_id}")
        print(f"DEBUG: slack_message: {slack_message}")
        
        send_slack_notification(channel_id, slack_message)
        actions_taken.append("Medium priority Slack warning sent")
    
    return {
        "ticket_id": alert.ticket_id,
        "alert_processed": True,
        "actions_taken": actions_taken,
        "timestamp": datetime.now().isoformat()
    }


def run_monitoring_cycle() -> Dict[str, Any]:
    """
    Run a complete monitoring cycle for all active tickets.
    
    Returns:
        Dict containing monitoring results and actions taken
    """
    print("🔄 Starting monitoring cycle...")
    
    # Monitor all tickets
    monitoring_results = monitor_all_active_tickets()
    
    actions_taken = []
    
    # Process escalation triggers
    for trigger_data in monitoring_results["escalation_triggers"]:
        trigger = EscalationTrigger(**trigger_data)
        result = process_escalation_trigger(trigger)
        actions_taken.append(result)
    
    # Process SLA alerts
    for alert_data in monitoring_results["sla_alerts"]:
        alert = SLAAlert(**alert_data)
        result = process_sla_alert(alert)
        actions_taken.append(result)
    
    print(f"✅ Monitoring cycle complete. {len(actions_taken)} actions taken.")
    
    return {
        "monitoring_results": monitoring_results,
        "actions_taken": actions_taken,
        "cycle_completed_at": datetime.now().isoformat()
    }


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
        # Debug print for trigger type
        print(f"DEBUG: run_escalation_monitoring - trigger_data type: {type(trigger_data)}")
        print(f"DEBUG: run_escalation_monitoring - trigger_data: {trigger_data}")
        print(f"DEBUG: run_escalation_monitoring - trigger_data keys: {trigger_data.keys() if isinstance(trigger_data, dict) else 'Not a dict'}")
        
        if isinstance(trigger_data, dict):
            # Check if all required fields are present
            required_fields = ['ticket_id', 'trigger_type', 'severity', 'description', 'recommended_action', 'created_at']
            missing_fields = [field for field in required_fields if field not in trigger_data]
            if missing_fields:
                print(f"DEBUG: ERROR - Missing fields in trigger_data: {missing_fields}")
                print(f"DEBUG: Available fields: {list(trigger_data.keys())}")
                continue
            
            trigger = EscalationTrigger(**trigger_data)
        else:
            trigger = trigger_data
        
        print(f"DEBUG: run_escalation_monitoring - trigger type: {type(trigger)}")
        print(f"DEBUG: run_escalation_monitoring - trigger: {trigger}")
        print(f"DEBUG: run_escalation_monitoring - trigger attributes: {[attr for attr in dir(trigger) if not attr.startswith('_')]}")
        
        result = process_escalation_trigger(trigger)
        escalation_results.append(result)
    
    return {
        "monitoring_time": monitoring_results["monitoring_time"],
        "tickets_checked": monitoring_results["tickets_checked"],
        "escalations_found": len(monitoring_results["escalation_triggers"]),
        "escalations_processed": len(escalation_results),
        "escalation_results": escalation_results
    }


# Use environment variable for Slack channel ID
def get_slack_channel_id():
    return os.getenv("SLACK_CHANNEL_ID", "C092BQHHGKV") 