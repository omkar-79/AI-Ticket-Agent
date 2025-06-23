"""Tools for the Knowledge Base Agent."""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from knowledge_base.articles import search_articles
from ai_ticket_agent.tools.database import get_workflow_state, get_step_data, update_workflow_state, get_ticket_user_email
from ai_ticket_agent.tools.notifications import draft_and_send_ticket_email


class KnowledgeArticle(BaseModel):
    """Knowledge base article or solution."""
    
    title: str = Field(description="Article title")
    content: str = Field(description="Article content")
    category: str = Field(description="Article category")
    relevance_score: float = Field(description="Relevance score 0.0-1.0")
    last_updated: str = Field(description="Last update date")
    author: str = Field(description="Article author")


class GeneratedResponse(BaseModel):
    """Generated response for a ticket."""
    
    response_text: str = Field(description="Response content")
    solution_steps: List[str] = Field(description="Step-by-step solution")
    related_articles: List[str] = Field(description="Related knowledge articles")
    escalation_instructions: str = Field(description="Instructions if self-service fails")
    confidence: float = Field(description="Confidence in the solution")


class ResourceSuggestion(BaseModel):
    """Suggested resources for a ticket."""
    
    documentation_links: List[str] = Field(description="Relevant documentation URLs")
    training_materials: List[str] = Field(description="Training material links")
    tools: List[str] = Field(description="Recommended tools")
    contacts: List[str] = Field(description="Relevant contact information")


def search_knowledge_base(
    ticket_id: str,
    query: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 5
) -> List[KnowledgeArticle]:
    """
    Search the knowledge base for relevant articles and solutions.
    
    Args:
        ticket_id: The ticket identifier for workflow state management.
        query: The search query.
        category: The category to search within.
        limit: Maximum number of results to return.
        
    Returns:
        List[KnowledgeArticle]: Relevant knowledge articles.
    """
    # Get classification data from the previous step to enrich the search
    classification_data = get_step_data(ticket_id, "CLASSIFICATION")
    if classification_data:
        if not query:
            query = " ".join(classification_data.get("keywords", []))
        if not category:
            category = classification_data.get("category")
    
    articles = search_articles(query=query, category=category, max_results=limit)
    
    knowledge_articles = []
    for article in articles:
        knowledge_articles.append(KnowledgeArticle(
            title=article["title"],
            content=article["content"],
            category=article["category"],
            relevance_score=article.get("relevance_score", 0.0),
            last_updated=article["updated_at"],
            author=article["author"]
        ))
    
    # Update workflow state based on search results
    if ticket_id:
        if knowledge_articles:
            # Found solutions, move to follow-up
            next_step = "FOLLOW_UP"
            status = "resolved"
            print(f"Knowledge base search found {len(knowledge_articles)} solutions, moving to {next_step}")
            
            # Send solution email to user
            _send_solution_email_to_user(ticket_id, classification_data, knowledge_articles)
            
        else:
            # No solutions found, move to assignment
            next_step = "ASSIGNMENT"
            status = "open"
            print(f"No knowledge base solutions found, moving to {next_step}")
        
        # Store knowledge search results
        update_workflow_state(
            ticket_id=ticket_id,
            current_step="KNOWLEDGE_SEARCH",
            next_step=next_step,
            step_data={
                "KNOWLEDGE_SEARCH": {
                    "articles_found": len(knowledge_articles),
                    "articles": [{"title": a.title, "category": a.category} for a in knowledge_articles],
                    "query": query,
                    "category": category
                }
            },
            status=status
        )
    
    print(f"Knowledge base search found {len(knowledge_articles)} articles")
    return knowledge_articles


def _send_solution_email_to_user(
    ticket_id: str,
    classification_data: Dict[str, Any],
    knowledge_articles: List[KnowledgeArticle]
) -> bool:
    """
    Send a solution email to the user when knowledge base solutions are found.
    
    Args:
        ticket_id: The ticket identifier
        classification_data: Classification data from previous step
        knowledge_articles: Found knowledge base articles
        
    Returns:
        bool: True if email was sent successfully
    """
    try:
        # Get user email from database (primary source) or classification data (fallback)
        user_email = get_ticket_user_email(ticket_id)
        if not user_email:
            user_email = classification_data.get("user_email", "user@company.com")
            print(f"⚠️ WARNING: Using fallback email from classification data: {user_email}")
        else:
            print(f"✅ Using email from database: {user_email}")
        
        # Prepare ticket data
        ticket_data = {
            "subject": classification_data.get("subject", "IT Support Request"),
            "priority": classification_data.get("priority", "MEDIUM"),
            "category": classification_data.get("category", "general"),
            "user_name": classification_data.get("user_name", "Valued Customer")
        }
        
        # Prepare solution data from the best matching article
        if knowledge_articles:
            best_article = knowledge_articles[0]  # Most relevant article
            
            # Generate response using the existing function
            response = generate_response(
                ticket_content=classification_data.get("description", ""),
                knowledge_articles=[{
                    "title": best_article.title,
                    "content": best_article.content,
                    "relevance_score": best_article.relevance_score
                }],
                user_context={"role": classification_data.get("user_role", "employee")}
            )
            
            solution_data = {
                "response_text": response.response_text,
                "solution_steps": response.solution_steps,
                "related_articles": response.related_articles,
                "confidence": response.confidence
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


def generate_response(
    ticket_content: str,
    knowledge_articles: List[Dict[str, Any]],
    user_context: Dict[str, Any]
) -> GeneratedResponse:
    """
    Generate a response based on knowledge base articles and ticket content.
    
    Args:
        ticket_content: The original ticket content
        knowledge_articles: Relevant knowledge articles
        user_context: User context and preferences
        
    Returns:
        GeneratedResponse: Generated response with solution steps
    """
    if not knowledge_articles:
        return GeneratedResponse(
            response_text="I couldn't find a specific solution for your issue. Please contact IT support for assistance.",
            solution_steps=["Contact IT support"],
            related_articles=[],
            escalation_instructions="Please contact IT support for personalized assistance.",
            confidence=0.1
        )
    
    # Use the first (most relevant) article
    article = knowledge_articles[0]
    
    # Extract solution steps from content
    content_lines = article["content"].split('\n')
    solution_steps = []
    for line in content_lines:
        line = line.strip()
        if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
            solution_steps.append(line)
    
    # Generate response text
    response_text = f"Based on your issue, here's a solution from our knowledge base:\n\n{article['title']}\n\n{article['content'][:500]}..."
    
    return GeneratedResponse(
        response_text=response_text,
        solution_steps=solution_steps[:5],  # Limit to 5 steps
        related_articles=[article["title"]],
        escalation_instructions="If these steps don't resolve the issue, please reply to this ticket and we'll escalate to a specialist.",
        confidence=article.get("relevance_score", 0.0)
    )


def suggest_resources(
    issue_type: str,
    user_role: str
) -> ResourceSuggestion:
    """
    Suggest relevant resources for a specific issue type.
    
    Args:
        issue_type: The type of issue
        user_role: The user's role or department
        
    Returns:
        ResourceSuggestion: Suggested resources and tools
    """
    resource_map = {
        "wifi": {
            "documentation_links": [
                "https://company.com/wifi-setup-guide",
                "https://company.com/network-troubleshooting"
            ],
            "training_materials": [
                "https://company.com/training/wifi-basics",
                "https://company.com/training/network-security"
            ],
            "tools": ["Network Diagnostics Tool", "WiFi Analyzer"],
            "contacts": ["network-support@company.com", "IT Helpdesk: x1234"]
        },
        "vpn": {
            "documentation_links": [
                "https://company.com/vpn-setup-guide",
                "https://company.com/network-troubleshooting"
            ],
            "training_materials": [
                "https://company.com/training/vpn-basics",
                "https://company.com/training/network-security"
            ],
            "tools": ["VPN Client", "Network Diagnostics Tool"],
            "contacts": ["network-support@company.com", "IT Helpdesk: x1234"]
        },
        "password": {
            "documentation_links": [
                "https://company.com/password-reset-guide",
                "https://company.com/account-security"
            ],
            "training_materials": [
                "https://company.com/training/password-security",
                "https://company.com/training/mfa-setup"
            ],
            "tools": ["Password Reset Portal", "MFA Setup Tool"],
            "contacts": ["access-management@company.com", "IT Helpdesk: x1234"]
        },
        "email": {
            "documentation_links": [
                "https://company.com/email-setup-guide",
                "https://company.com/outlook-configuration"
            ],
            "training_materials": [
                "https://company.com/training/email-basics",
                "https://company.com/training/outlook-tips"
            ],
            "tools": ["Outlook", "Email Diagnostics Tool"],
            "contacts": ["email-support@company.com", "IT Helpdesk: x1234"]
        },
        "hardware": {
            "documentation_links": [
                "https://company.com/hardware-troubleshooting",
                "https://company.com/device-setup-guides"
            ],
            "training_materials": [
                "https://company.com/training/hardware-basics",
                "https://company.com/training/device-maintenance"
            ],
            "tools": ["Hardware Diagnostics", "Device Manager"],
            "contacts": ["hardware-support@company.com", "IT Helpdesk: x1234"]
        }
    }
    
    default_resources = {
        "documentation_links": ["https://company.com/it-helpdesk"],
        "training_materials": ["https://company.com/training"],
        "tools": ["IT Support Portal"],
        "contacts": ["it-helpdesk@company.com", "IT Helpdesk: x1234"]
    }
    
    issue_lower = issue_type.lower()
    resources = default_resources
    
    for key, value in resource_map.items():
        if key in issue_lower:
            resources = value
            break
    
    return ResourceSuggestion(**resources) 