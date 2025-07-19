"""Resolution tracker tool for monitoring self-service success."""

from google.adk.tools import ToolContext
from typing import Dict, Any


def track_resolution_attempt(problem_description: str, solution_provided: str, user_feedback: str, tool_context: ToolContext) -> str:
    """
    Track resolution attempts and determine if escalation is needed.
    
    Args:
        problem_description: The original problem reported by user
        solution_provided: The solution that was provided
        user_feedback: User's response about whether the solution worked
        
    Returns:
        Status of resolution attempt
    """
    # Simple logic to determine if escalation is needed
    feedback_lower = user_feedback.lower()
    
    # Check for positive indicators
    positive_indicators = [
        "worked", "solved", "fixed", "resolved", "yes", "good", "thanks", 
        "thank you", "perfect", "great", "okay", "ok", "fine"
    ]
    
    # Check for negative indicators
    negative_indicators = [
        "didn't work", "not working", "still broken", "no", "failed", 
        "doesn't work", "can't", "unable", "error", "problem", "issue"
    ]
    
    positive_count = sum(1 for indicator in positive_indicators if indicator in feedback_lower)
    negative_count = sum(1 for indicator in negative_indicators if indicator in feedback_lower)
    
    if positive_count > negative_count:
        return "RESOLVED: User confirmed the solution worked. No escalation needed."
    elif negative_count > positive_count:
        return "ESCALATION_NEEDED: User indicates the solution didn't work. Escalating to human team."
    else:
        return "UNCLEAR: User feedback is ambiguous. Escalating to human team for clarification."


# The tool is just the function itself
resolution_tracker_tool = track_resolution_attempt 