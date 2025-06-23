"""Tools for the Follow-up Agent."""

from google.adk.tools import ToolContext
from ai_ticket_agent.tools.database import get_ticket
from datetime import datetime


def build_feedback_prompt(ticket_id: str, user_feedback: str) -> str:
    """
    Build the prompt text for LLM feedback analysis.
    """
    ticket = get_ticket(ticket_id)
    if not ticket:
        print(f"❌ Ticket {ticket_id} not found for LLM analysis.")
        return ""
    
    prompt_text = f"""
A user has provided the following feedback after receiving the resolution notes for their IT support ticket:

---
Ticket ID: {ticket_id}
Ticket Subject: {ticket.subject}
Assigned Team: {ticket.assigned_team}
Resolution Notes: {ticket.resolution_notes}
User Feedback: {user_feedback}
---

Based on this feedback, should the ticket be closed (user is satisfied) or reopened (user is not satisfied)?
Consider the following:
- If the user expresses satisfaction, gratitude, or confirms the solution worked, respond with 'close'
- If the user expresses dissatisfaction, mentions issues, or requests further assistance, respond with 'reopen'
- If the feedback is ambiguous, default to 'reopen' to ensure user satisfaction

Respond with only one word: 'close' or 'reopen'.
"""
    return prompt_text


def store_feedback_memory(ticket_id: str, feedback: str, decision: str, tool_context: ToolContext):
    """
    Store feedback analysis in memory for future reference.
    Inspired by travel-concierge memory pattern.
    """
    if "feedback_history" not in tool_context.state:
        tool_context.state["feedback_history"] = []
    
    feedback_record = {
        "ticket_id": ticket_id,
        "feedback": feedback,
        "decision": decision,
        "timestamp": str(datetime.now())
    }
    
    tool_context.state["feedback_history"].append(feedback_record)
    return {"status": f"Stored feedback analysis for ticket {ticket_id}"}


def get_feedback_history(tool_context: ToolContext):
    """
    Retrieve feedback history for analysis.
    """
    return tool_context.state.get("feedback_history", [])


