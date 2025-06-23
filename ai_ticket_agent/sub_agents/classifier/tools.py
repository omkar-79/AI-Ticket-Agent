"""Tools for the Ticket Classification Agent."""

from typing import Dict, List, Any
from pydantic import BaseModel, Field
from ai_ticket_agent.tools.database import create_ticket, create_workflow_state, set_step_data, update_ticket_fields, update_workflow_state


class TicketClassification(BaseModel):
    """Classification result for an IT support ticket."""
    
    ticket_id: str = Field(description="The unique identifier for the created ticket")
    category: str = Field(description="Primary category: hardware, software, network, access, security, email, general")
    priority: str = Field(description="Priority level: critical, high, medium, low")
    urgency: str = Field(description="Urgency level: immediate, high, medium, low")
    confidence: float = Field(description="Confidence score 0.0-1.0")
    keywords: List[str] = Field(description="Key terms extracted from the ticket")
    business_impact: str = Field(description="Estimated business impact")
    suggested_team: str = Field(description="Recommended support team")


class PriorityIndicators(BaseModel):
    """Priority indicators extracted from ticket content."""
    
    urgency_keywords: List[str] = Field(description="Words indicating urgency")
    business_terms: List[str] = Field(description="Business-critical terms")
    user_role: str = Field(description="Inferred user role or department")
    affected_users: int = Field(description="Estimated number of affected users")
    time_sensitivity: str = Field(description="Time sensitivity assessment")


def classify_ticket(
    ticket_id: str,
    subject: str,
    description: str,
    user_email: str
) -> Dict[str, Any]:
    """
    Analyzes an existing ticket's content and updates it with classification details.

    Args:
        ticket_id: The unique identifier of the ticket to classify.
        subject: The ticket subject line.
        description: The detailed ticket description.
        user_email: The user's email address.

    Returns:
        A dictionary containing the classification results.
    """
    # This would integrate with an LLM for actual classification.
    # For now, returning a hardcoded response.
    classification = {
        "category": "network",
        "priority": "medium",
        "urgency": "medium",
        "confidence": 0.85,
        "keywords": ["wifi", "connection", "network"],
        "business_impact": "Individual productivity",
        "suggested_team": "Network Support"
    }
    
    try:
        # Update the ticket in the database with the classification details
        update_ticket_fields(
            ticket_id=ticket_id,
            updates={
                "category": classification["category"],
                "priority": classification["priority"],
            }
        )
        
        # Update the workflow state to reflect that classification is complete
        update_workflow_state(
            ticket_id=ticket_id,
            current_step="CLASSIFICATION",
            next_step="KNOWLEDGE_SEARCH",
            step_data={"CLASSIFICATION": classification},
            status="classified"
        )
        
        print(f"Ticket {ticket_id} classified. Next step: KNOWLEDGE_SEARCH")
        
    except Exception as e:
        print(f"Error in classify_ticket: {e}")
        return {"error": str(e)}
    
    return classification


def extract_priority_indicators(
    content: str
) -> PriorityIndicators:
    """
    Extract priority indicators from ticket content.
    
    Args:
        content: The ticket content to analyze
        
    Returns:
        PriorityIndicators: Extracted priority indicators
    """
    # This would use NLP/LLM to extract priority indicators
    return PriorityIndicators(
        urgency_keywords=["urgent", "broken", "down"],
        business_terms=["production", "customer", "revenue"],
        user_role="Employee",
        affected_users=1,
        time_sensitivity="Medium"
    ) 