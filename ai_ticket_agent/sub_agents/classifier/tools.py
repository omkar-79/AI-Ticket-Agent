"""Tools for the Ticket Classification Agent."""

from typing import Dict, List, Any
from pydantic import BaseModel, Field
from ai_ticket_agent.tools.database import update_ticket_fields, update_workflow_state, get_ticket_info
import asyncio


class TicketClassification(BaseModel):
    """Classification result for an IT support ticket."""
    
    ticket_id: str = Field(description="The unique identifier for the created ticket")
    category: str = Field(description="Primary category: hardware, software, network, access, security, email, general")
    priority: str = Field(description="Priority level: critical, high, medium, low")
    keywords: List[str] = Field(description="Key terms extracted from the ticket")
    suggested_team: str = Field(description="Recommended support team")


def classify_ticket(ticket_id: str) -> dict:
    """
    Uses LLM to classify the ticket based on its content.
    """
    # Get ticket information from database
    ticket_info = get_ticket_info(ticket_id)
    if not ticket_info:
        return {"error": f"Ticket {ticket_id} not found"}
    
    subject = ticket_info.get("subject", "")
    description = ticket_info.get("description", "")
    user_email = ticket_info.get("user_email", "")
    
    print(f"DEBUG: Classifying ticket {ticket_id}")
    print(f"DEBUG: Subject: {subject}")
    print(f"DEBUG: Description: {description}")
    
    # Import here to avoid circular import
    from ai_ticket_agent.sub_agents.classifier.agent import classifier_agent as llm_classifier_agent
    
    # Prepare the input for the LLM
    llm_input = {
        "ticket_id": ticket_id,
        "subject": subject,
        "description": description,
        "user_email": user_email
    }
    
    # Call the LLM classifier agent
    try:
        llm_response = asyncio.run(llm_classifier_agent(llm_input))
        print(f"DEBUG: LLM classifier response: {llm_response}")
    except Exception as e:
        print(f"ERROR: LLM classifier agent call failed: {e}")
        # Fallback classification
        llm_response = {
            "category": "general",
            "priority": "medium",
            "keywords": ["support", "help"],
            "suggested_team": "General IT"
        }
    
    # Parse the LLM response
    classification = llm_response if isinstance(llm_response, dict) else {}
    
    # Ensure required fields exist
    classification.setdefault("category", "general")
    classification.setdefault("priority", "medium")
    classification.setdefault("keywords", [])
    classification.setdefault("suggested_team", "General IT")
    
    print(f"DEBUG: Final classification: {classification}")
    
    try:
        # Update the ticket in the database with the classification details
        update_ticket_fields(
            ticket_id=ticket_id,
            updates={
                "category": classification["category"],
                "priority": classification["priority"],
            }
        )
        
        # Update the workflow state
        update_workflow_state(
            ticket_id=ticket_id,
            current_step="CLASSIFICATION",
            next_step="KNOWLEDGE_SEARCH",
            step_data={"CLASSIFICATION": classification},
            status="active"
        )
        
        print(f"DEBUG: Ticket {ticket_id} classified successfully. Next step: KNOWLEDGE_SEARCH")
        
    except Exception as e:
        print(f"ERROR in classify_ticket: {e}")
        return {"error": str(e)}
    
    return classification


def continue_workflow(ticket_id: str) -> dict:
    """
    Continue the workflow after classification.
    """
    return {
        "next_agent": "knowledge_agent",
        "ticket_id": ticket_id,
        "status": "ready_for_knowledge_search"
    } 