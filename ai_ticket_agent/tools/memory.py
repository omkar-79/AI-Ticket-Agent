"""Memory and state management tools for the IT Helpdesk system."""

import json
import os
from typing import Dict, Any
from google.adk.agents.callback_context import CallbackContext


def _load_initial_state(callback_context: CallbackContext) -> None:
    """
    Load initial state into the session for IT Helpdesk operations.
    
    Args:
        callback_context: The ADK callback context which contains the session
    """
    session_state = callback_context.state
    
    # Initialize workflow state
    if "workflow_state" not in session_state:
        session_state["workflow_state"] = {
            "current_step": "CLASSIFICATION",
            "ticket_id": None,
            "ticket_status": None,
            "completed_steps": [],
            "next_step": "KNOWLEDGE_SEARCH"
        }
    
    # Load default configuration
    default_config = {
        "sla_rules": {
            "critical": {"response_time": "1 hour", "resolution_time": "4 hours"},
            "high": {"response_time": "2 hours", "resolution_time": "8 hours"},
            "medium": {"response_time": "4 hours", "resolution_time": "24 hours"},
            "low": {"response_time": "8 hours", "resolution_time": "72 hours"}
        },
        "teams": {
            "hardware": "Hardware Support",
            "software": "Software Support", 
            "network": "Network Support",
            "access": "Access Management",
            "security": "Security Team",
            "email": "Email Support",
            "general": "General IT"
        },
        "knowledge_base": {
            "enabled": True,
            "search_enabled": True,
            "auto_response_enabled": True
        },
        "escalation_rules": {
            "sla_breach_threshold": 0.9,
            "failed_attempts_threshold": 3,
            "security_auto_escalate": True
        }
    }
    
    # Load from environment if available
    scenario_path = os.getenv("IT_HELPDESK_SCENARIO")
    if scenario_path and os.path.exists(scenario_path):
        try:
            with open(scenario_path, 'r') as f:
                scenario_data = json.load(f)
                default_config.update(scenario_data)
        except Exception as e:
            print(f"Warning: Could not load scenario from {scenario_path}: {e}")
    
    # Set session state
    session_state["config"] = default_config
    session_state["active_tickets"] = {}
    session_state["sla_alerts"] = []
    session_state["escalations"] = []
    session_state["knowledge_base_cache"] = {}
    
    print("Initial state loaded for IT Helpdesk system")


def save_session_state(session, key: str, value: Any) -> None:
    """
    Save a value to the session state.
    
    Args:
        session: The ADK session
        key: The key to save under
        value: The value to save
    """
    session.state[key] = value


def get_session_state(session, key: str, default: Any = None) -> Any:
    """
    Get a value from the session state.
    
    Args:
        session: The ADK session
        key: The key to retrieve
        default: Default value if key doesn't exist
        
    Returns:
        The value from session state or default
    """
    return session.state.get(key, default)


def update_ticket_state(session, ticket_id: str, updates: Dict[str, Any]) -> None:
    """
    Update ticket state in the session.
    
    Args:
        session: The ADK session
        ticket_id: The ticket identifier
        updates: Updates to apply to the ticket
    """
    if "active_tickets" not in session.state:
        session.state["active_tickets"] = {}
    
    if ticket_id not in session.state["active_tickets"]:
        session.state["active_tickets"][ticket_id] = {}
    
    session.state["active_tickets"][ticket_id].update(updates)


def get_ticket_state(session, ticket_id: str) -> Dict[str, Any]:
    """
    Get ticket state from the session.
    
    Args:
        session: The ADK session
        ticket_id: The ticket identifier
        
    Returns:
        The ticket state dictionary
    """
    return session.state.get("active_tickets", {}).get(ticket_id, {})


def update_workflow_step(session, step: str, ticket_id: str = None, status: str = None) -> None:
    """
    Update the current workflow step in the session.
    
    Args:
        session: The ADK session
        step: The current workflow step
        ticket_id: The ticket identifier
        status: The ticket status
    """
    if "workflow_state" not in session.state:
        session.state["workflow_state"] = {}
    
    workflow_state = session.state["workflow_state"]
    workflow_state["current_step"] = step
    
    if ticket_id:
        workflow_state["ticket_id"] = ticket_id
    
    if status:
        workflow_state["ticket_status"] = status
    
    # Update completed steps
    if step not in workflow_state.get("completed_steps", []):
        if "completed_steps" not in workflow_state:
            workflow_state["completed_steps"] = []
        workflow_state["completed_steps"].append(step)
    
    # Set next step based on current step
    step_sequence = ["CLASSIFICATION", "KNOWLEDGE_SEARCH", "ASSIGNMENT", "FOLLOW_UP"]
    try:
        current_index = step_sequence.index(step)
        if current_index < len(step_sequence) - 1:
            workflow_state["next_step"] = step_sequence[current_index + 1]
        else:
            workflow_state["next_step"] = "COMPLETED"
    except ValueError:
        workflow_state["next_step"] = "UNKNOWN"


def get_workflow_state(session) -> Dict[str, Any]:
    """
    Get the current workflow state from the session.
    
    Args:
        session: The ADK session
        
    Returns:
        The workflow state dictionary
    """
    return session.state.get("workflow_state", {
        "current_step": "CLASSIFICATION",
        "ticket_id": None,
        "ticket_status": None,
        "completed_steps": [],
        "next_step": "KNOWLEDGE_SEARCH"
    })


def reset_workflow_state(session) -> None:
    """
    Reset the workflow state to initial values.
    
    Args:
        session: The ADK session
    """
    session.state["workflow_state"] = {
        "current_step": "CLASSIFICATION",
        "ticket_id": None,
        "ticket_status": None,
        "completed_steps": [],
        "next_step": "KNOWLEDGE_SEARCH"
    } 