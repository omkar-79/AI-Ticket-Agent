"""Tools for the Knowledge Base Agent."""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from knowledge_base.simple_search import search_knowledge_base_simple, has_relevant_solution
from ai_ticket_agent.tools.database import get_workflow_state, get_step_data, update_workflow_state, get_ticket_info, update_ticket_fields
from ai_ticket_agent.tools.notifications import draft_and_send_ticket_email
import asyncio


class KnowledgeArticle(BaseModel):
    """Knowledge base article or solution."""
    
    title: str = Field(description="Article title")
    content: str = Field(description="Article content")
    category: str = Field(description="Article category")
    relevance_score: float = Field(description="Relevance score 0.0-1.0")


def search_knowledge_base(ticket_id: str) -> List[KnowledgeArticle]:
    """
    Search the knowledge base for relevant articles using simple text file approach.
    STRONG LIMIT: Only returns solutions if relevance score >= 0.8, otherwise assigns to team.
    """
    # Get ticket information and classification data
    ticket_info = get_ticket_info(ticket_id)
    classification_data = get_step_data(ticket_id, "CLASSIFICATION")
    
    if not ticket_info:
        return []
    
    # Prepare search query
    subject = ticket_info.get("subject", "")
    description = ticket_info.get("description", "")
    keywords = classification_data.get("keywords", []) if classification_data else []
    
    # Create search query from keywords and ticket content
    query = " ".join(keywords + [subject, description])
    
    print(f"DEBUG: Searching knowledge base for ticket {ticket_id}")
    print(f"DEBUG: Query: {query}")
    
    # Search knowledge base with STRONG threshold (0.8)
    articles = search_knowledge_base_simple(query, min_relevance_score=0.8)
    
    knowledge_articles = []
    for article in articles:
        knowledge_articles.append(KnowledgeArticle(
            title=article["title"],
            content=article["content"],
            category=article["category"],
            relevance_score=article["relevance_score"]
        ))
    
    print(f"DEBUG: Found {len(knowledge_articles)} articles with relevance >= 0.8")
    
    # STRONG LIMIT: Only proceed if we have highly relevant solutions
    if knowledge_articles and knowledge_articles[0].relevance_score >= 0.8:
        # Found a highly relevant solution, send to user and mark as resolved
        _send_solution_to_user(ticket_id, ticket_info, classification_data, knowledge_articles)
        
        # Update workflow state
        update_workflow_state(
            ticket_id=ticket_id,
            current_step="KNOWLEDGE_SEARCH",
            next_step="COMPLETE",
            step_data={"KNOWLEDGE_SEARCH": {"solution_found": True, "articles": len(knowledge_articles)}},
            status="resolved"
        )
        
        # Update ticket status to resolved
        update_ticket_fields(
            ticket_id=ticket_id,
            updates={"status": "resolved"},
            updated_by="knowledge_agent"
        )
        
        print(f"✅ Found highly relevant solution (score: {knowledge_articles[0].relevance_score:.2f}), resolving ticket")
    else:
        # No highly relevant solution found, move to assignment
        update_workflow_state(
            ticket_id=ticket_id,
            current_step="KNOWLEDGE_SEARCH",
            next_step="ASSIGNMENT",
            step_data={"KNOWLEDGE_SEARCH": {"solution_found": False, "articles": len(knowledge_articles)}},
            status="open"
        )
        
        if knowledge_articles:
            print(f"❌ No highly relevant solution found (best score: {knowledge_articles[0].relevance_score:.2f}), assigning to team")
        else:
            print(f"❌ No relevant solutions found, assigning to team")
    
    return knowledge_articles


def _send_solution_to_user(
    ticket_id: str,
    ticket_info: Dict[str, Any],
    classification_data: Dict[str, Any],
    articles: List[KnowledgeArticle]
) -> bool:
    """
    Send solution to user when knowledge base solutions are found.
    """
    try:
        user_email = ticket_info.get("user_email", "user@company.com")
        
        # Prepare ticket data
        ticket_data = {
            "subject": ticket_info.get("subject", "IT Support Request"),
            "priority": classification_data.get("priority", "MEDIUM") if classification_data else "MEDIUM",
            "category": classification_data.get("category", "general") if classification_data else "general",
            "user_name": "Valued Customer"
        }
        
        # Prepare solution data from the best matching article
        if articles:
            best_article = articles[0]  # Most relevant article
            
            solution_data = {
                "response_text": f"Here's a solution for your issue: {best_article.title}",
                "solution_steps": [best_article.content],
                "related_articles": [best_article.title],
                "confidence": best_article.relevance_score
            }
            
            # Send the solution email
            success = draft_and_send_ticket_email(
                ticket_id=ticket_id,
                user_email=user_email,
                email_type="solution_found",
                ticket_data=ticket_data,
                solution_data=solution_data
            )
            
            if success:
                print(f"✅ Solution email sent to {user_email} for ticket {ticket_id}")
            else:
                print(f"❌ Failed to send solution email to {user_email} for ticket {ticket_id}")
            
            return success
        else:
            print(f"No knowledge articles found for ticket {ticket_id}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending solution email: {e}")
        return False


def continue_workflow(ticket_id: str) -> dict:
    """
    Continue the workflow after knowledge base search.
    """
    workflow_state = get_workflow_state(ticket_id)
    
    # Fix: WorkflowState is a Pydantic model, access attributes directly
    if workflow_state:
        next_step = workflow_state.next_step
    else:
        next_step = "ASSIGNMENT"
    
    if next_step == "COMPLETE":
        return {
            "next_agent": None,
            "ticket_id": ticket_id,
            "status": "resolved"
        }
    else:
        return {
            "next_agent": "assignment_agent",
            "ticket_id": ticket_id,
            "status": "ready_for_assignment"
        } 