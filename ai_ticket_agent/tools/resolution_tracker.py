"""Enhanced resolution tracker tool for monitoring self-service success with database persistence."""

from google.adk.tools import ToolContext
from typing import Dict, Any, Optional
from ai_ticket_agent.database import db_manager
from ai_ticket_agent.models import ResolutionStatus


def track_resolution_attempt(
    ticket_id: str,
    problem_description: str, 
    solution_provided: str, 
    user_feedback: Optional[str] = None,
    agent_type: str = "self_service",
    tool_context: Optional[ToolContext] = None
) -> str:
    """
    Track resolution attempts and determine if escalation is needed.
    
    Args:
        ticket_id: The ticket ID to track
        problem_description: The original problem reported by user
        solution_provided: The solution that was provided
        user_feedback: User's response about whether the solution worked
        agent_type: Type of agent that provided the solution
        tool_context: The ADK tool context
        
    Returns:
        Status of resolution attempt with database tracking
    """
    
    # Get database session
    session = db_manager.get_session()
    
    try:
        # Check if ticket exists
        ticket = db_manager.get_ticket(session, ticket_id)
        if not ticket:
            return f"ERROR: Ticket {ticket_id} not found in database"
        
        # Analyze user feedback if provided
        feedback_analysis = None
        resolution_status = ResolutionStatus.PENDING
        
        if user_feedback:
            feedback_analysis = analyze_user_feedback(user_feedback)
            resolution_status = determine_resolution_status(feedback_analysis)
        
        # Create resolution attempt record
        resolution_attempt = db_manager.add_resolution_attempt(
            session=session,
            ticket_id=ticket_id,
            agent_type=agent_type,
            solution_provided=solution_provided,
            user_feedback=user_feedback,
            status=resolution_status,
            feedback_analysis=feedback_analysis
        )
        
        # Update ticket status based on resolution outcome
        if resolution_status == ResolutionStatus.SUCCESS:
            db_manager.update_ticket_status(
                session=session,
                ticket_id=ticket_id,
                status="resolved",
                message="Issue resolved through self-service",
                updated_by="ai_agent"
            )
            return f"RESOLVED: Ticket {ticket_id} successfully resolved. Resolution attempt #{resolution_attempt.attempt_number} recorded."
        
        elif resolution_status == ResolutionStatus.FAILED:
            db_manager.update_ticket_status(
                session=session,
                ticket_id=ticket_id,
                status="escalated",
                message="Self-service resolution failed, escalating to human team",
                updated_by="ai_agent"
            )
            return f"ESCALATION_NEEDED: Ticket {ticket_id} resolution failed. Escalating to human team. Resolution attempt #{resolution_attempt.attempt_number} recorded."
        
        elif resolution_status == ResolutionStatus.ESCALATED:
            db_manager.update_ticket_status(
                session=session,
                ticket_id=ticket_id,
                status="escalated",
                message="Issue escalated to human team",
                updated_by="ai_agent"
            )
            return f"ESCALATED: Ticket {ticket_id} escalated to human team. Resolution attempt #{resolution_attempt.attempt_number} recorded."
        
        else:
            return f"PENDING: Ticket {ticket_id} resolution attempt #{resolution_attempt.attempt_number} recorded. Awaiting user feedback."
    
    except Exception as e:
        return f"ERROR: Failed to track resolution attempt for ticket {ticket_id}: {str(e)}"
    
    finally:
        session.close()


def analyze_user_feedback(user_feedback: str) -> str:
    """
    Analyze user feedback using LLM-like logic.
    
    Args:
        user_feedback: User's response about the solution
        
    Returns:
        Analysis of the feedback
    """
    feedback_lower = user_feedback.lower()
    
    # Check for positive indicators
    positive_indicators = [
        "worked", "solved", "fixed", "resolved", "yes", "good", "thanks", 
        "thank you", "perfect", "great", "okay", "ok", "fine", "successful",
        "working", "better", "improved", "helped", "useful"
    ]
    
    # Check for negative indicators
    negative_indicators = [
        "didn't work", "not working", "still broken", "no", "failed", 
        "doesn't work", "can't", "unable", "error", "problem", "issue",
        "same", "still", "worse", "useless", "didn't help", "not fixed"
    ]
    
    # Check for escalation indicators
    escalation_indicators = [
        "escalate", "human", "support", "team", "expert", "specialist",
        "complex", "complicated", "urgent", "critical", "emergency"
    ]
    
    positive_count = sum(1 for indicator in positive_indicators if indicator in feedback_lower)
    negative_count = sum(1 for indicator in negative_indicators if indicator in feedback_lower)
    escalation_count = sum(1 for indicator in escalation_indicators if indicator in feedback_lower)
    
    if escalation_count > 0:
        return f"ESCALATION_REQUESTED: User explicitly requested escalation or human assistance. Positive indicators: {positive_count}, Negative indicators: {negative_count}, Escalation indicators: {escalation_count}"
    elif positive_count > negative_count:
        return f"POSITIVE_FEEDBACK: User indicated the solution worked. Positive indicators: {positive_count}, Negative indicators: {negative_count}"
    elif negative_count > positive_count:
        return f"NEGATIVE_FEEDBACK: User indicated the solution didn't work. Positive indicators: {positive_count}, Negative indicators: {negative_count}"
    else:
        return f"NEUTRAL_FEEDBACK: User feedback is ambiguous. Positive indicators: {positive_count}, Negative indicators: {negative_count}"


def determine_resolution_status(feedback_analysis: str) -> ResolutionStatus:
    """
    Determine resolution status based on feedback analysis.
    
    Args:
        feedback_analysis: Analysis of user feedback
        
    Returns:
        Resolution status
    """
    if "POSITIVE_FEEDBACK" in feedback_analysis:
        return ResolutionStatus.SUCCESS
    elif "NEGATIVE_FEEDBACK" in feedback_analysis:
        return ResolutionStatus.FAILED
    elif "ESCALATION_REQUESTED" in feedback_analysis:
        return ResolutionStatus.ESCALATED
    else:
        return ResolutionStatus.PENDING


def get_ticket_resolution_history(ticket_id: str) -> str:
    """
    Get resolution history for a ticket.
    
    Args:
        ticket_id: The ticket ID to get history for
        
    Returns:
        Formatted resolution history
    """
    session = db_manager.get_session()
    
    try:
        history = db_manager.get_ticket_history(session, ticket_id)
        if not history:
            return f"ERROR: Ticket {ticket_id} not found"
        
        ticket_info = history["ticket"]
        resolution_attempts = history["resolution_attempts"]
        
        result = f"""
**Ticket Resolution History: {ticket_id}**

**Ticket Info:**
- Subject: {ticket_info['subject']}
- Status: {ticket_info['status']}
- Priority: {ticket_info['priority']}
- Assigned Team: {ticket_info['assigned_team'] or 'Not assigned'}
- User: {ticket_info['user_email']}
- Created: {ticket_info['created_at']}

**Resolution Attempts: {len(resolution_attempts)}**
"""
        
        for attempt in resolution_attempts:
            result += f"""
**Attempt #{attempt['attempt_number']}** ({attempt['created_at']})
- Agent: {attempt['agent_type']}
- Status: {attempt['status']}
- Solution: {attempt['solution_provided'][:100]}...
- User Feedback: {attempt['user_feedback'] or 'None'}
- Analysis: {attempt['feedback_analysis'] or 'None'}
"""
        
        return result
    
    except Exception as e:
        return f"ERROR: Failed to get resolution history for ticket {ticket_id}: {str(e)}"
    
    finally:
        session.close()


# The tool is just the function itself
resolution_tracker_tool = track_resolution_attempt 