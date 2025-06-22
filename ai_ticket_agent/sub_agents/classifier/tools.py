"""Tools for the Ticket Classification Agent."""

from typing import Dict, List, Any
from pydantic import BaseModel, Field


class TicketClassification(BaseModel):
    """Classification result for an IT support ticket."""
    
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
    subject: str,
    description: str,
    user_email: str,
    source: str
) -> TicketClassification:
    """
    Analyze and classify an IT support ticket based on its content.
    
    Args:
        subject: The ticket subject line
        description: The detailed ticket description
        user_email: The user's email address
        source: The source of the ticket
        
    Returns:
        TicketClassification: Structured classification result
    """
    # This would integrate with an LLM for actual classification
    # For now, returning a structured response
    return TicketClassification(
        category="network",
        priority="medium",
        urgency="medium",
        confidence=0.85,
        keywords=["VPN", "disconnect", "connection"],
        business_impact="Individual productivity",
        suggested_team="Network Support"
    )


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