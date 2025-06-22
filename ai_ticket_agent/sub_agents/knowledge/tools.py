"""Tools for the Knowledge Base Agent."""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from knowledge_base.articles import search_articles, get_article_by_id, get_articles


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
    query: str,
    category: str = None,
    max_results: int = 5
) -> List[KnowledgeArticle]:
    """
    Search the knowledge base for relevant articles and solutions.
    
    Args:
        query: The search query
        category: The category to search within
        max_results: Maximum number of results to return
        
    Returns:
        List[KnowledgeArticle]: Relevant knowledge articles
    """
    # Use local knowledge base
    articles = search_articles(query, category, max_results)
    
    # Convert to KnowledgeArticle objects
    knowledge_articles = []
    for article in articles:
        knowledge_articles.append(KnowledgeArticle(
            title=article["title"],
            content=article["content"],
            category=article["category"],
            relevance_score=article["relevance_score"],
            last_updated=article["updated_at"],
            author=article["author"]
        ))
    
    return knowledge_articles


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
        confidence=article["relevance_score"]
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
    # Map issue types to resources
    resource_map = {
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
    
    # Default resources
    default_resources = {
        "documentation_links": ["https://company.com/it-helpdesk"],
        "training_materials": ["https://company.com/training"],
        "tools": ["IT Support Portal"],
        "contacts": ["it-helpdesk@company.com", "IT Helpdesk: x1234"]
    }
    
    # Find matching resources
    issue_lower = issue_type.lower()
    resources = default_resources
    
    for key, value in resource_map.items():
        if key in issue_lower:
            resources = value
            break
    
    return ResourceSuggestion(**resources) 