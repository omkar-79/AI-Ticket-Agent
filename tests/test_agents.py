"""Unit tests for AI Ticket Agent agents."""

import pytest
from unittest.mock import Mock, patch
from ai_ticket_agent.sub_agents.classifier.tools import classify_ticket, extract_priority_indicators
from ai_ticket_agent.sub_agents.assignment.tools import assign_ticket, get_team_workload
from ai_ticket_agent.sub_agents.knowledge.tools import search_knowledge_base, generate_response
from ai_ticket_agent.tools.database import create_ticket, get_ticket, update_ticket


class TestClassifierAgent:
    """Test cases for the Classifier Agent."""
    
    def test_classify_ticket(self):
        """Test ticket classification functionality."""
        result = classify_ticket(
            subject="VPN Connection Issues",
            description="My VPN keeps disconnecting every 30 minutes",
            user_email="user@company.com",
            source="email"
        )
        
        assert result.category == "network"
        assert result.priority == "medium"
        assert result.confidence > 0.8
        assert "VPN" in result.keywords
    
    def test_extract_priority_indicators(self):
        """Test priority indicator extraction."""
        result = extract_priority_indicators(
            content="URGENT: Production server is down, customers cannot access the system"
        )
        
        assert "urgent" in result.urgency_keywords
        assert "production" in result.business_terms
        assert result.affected_users > 1


class TestAssignmentAgent:
    """Test cases for the Assignment Agent."""
    
    def test_assign_ticket(self):
        """Test ticket assignment functionality."""
        classification = {
            "category": "network",
            "priority": "medium",
            "suggested_team": "Network Support"
        }
        
        result = assign_ticket(
            ticket_id="TICKET-001",
            classification=classification,
            priority="medium",
            category="network"
        )
        
        assert result.team == "Network Support"
        assert result.queue in ["urgent", "high", "standard", "low"]
        assert result.sla_target is not None
    
    def test_get_team_workload(self):
        """Test team workload retrieval."""
        result = get_team_workload(team="Network Support")
        
        assert result.team == "Network Support"
        assert result.active_tickets >= 0
        assert result.available_agents >= 0
        assert 0 <= result.sla_compliance_rate <= 1


class TestKnowledgeAgent:
    """Test cases for the Knowledge Agent."""
    
    def test_search_knowledge_base(self):
        """Test knowledge base search."""
        results = search_knowledge_base(
            query="VPN troubleshooting",
            category="network",
            max_results=3
        )
        
        assert len(results) > 0
        assert all(result.category == "network" for result in results)
        assert all(result.relevance_score > 0.5 for result in results)
    
    def test_generate_response(self):
        """Test response generation."""
        ticket_content = "My VPN keeps disconnecting"
        knowledge_articles = [
            {
                "title": "VPN Troubleshooting Guide",
                "content": "Step-by-step guide to resolve VPN issues"
            }
        ]
        user_context = {"role": "employee", "department": "engineering"}
        
        result = generate_response(
            ticket_content=ticket_content,
            knowledge_articles=knowledge_articles,
            user_context=user_context
        )
        
        assert result.response_text is not None
        assert len(result.solution_steps) > 0
        assert result.confidence > 0.5


class TestDatabaseTools:
    """Test cases for database tools."""
    
    def test_create_ticket(self):
        """Test ticket creation."""
        ticket = create_ticket(
            subject="Test Ticket",
            description="This is a test ticket",
            user_email="test@company.com",
            priority="medium",
            category="general",
            source="test"
        )
        
        assert ticket.id is not None
        assert ticket.subject == "Test Ticket"
        assert ticket.status == "open"
        assert ticket.assigned_team == "unassigned"
    
    def test_get_ticket(self):
        """Test ticket retrieval."""
        # First create a ticket
        created_ticket = create_ticket(
            subject="Test Ticket",
            description="This is a test ticket",
            user_email="test@company.com",
            priority="medium",
            category="general",
            source="test"
        )
        
        # Then retrieve it
        retrieved_ticket = get_ticket(created_ticket.id)
        
        assert retrieved_ticket is not None
        assert retrieved_ticket.id == created_ticket.id
        assert retrieved_ticket.subject == created_ticket.subject
    
    def test_update_ticket(self):
        """Test ticket update."""
        # First create a ticket
        ticket = create_ticket(
            subject="Test Ticket",
            description="This is a test ticket",
            user_email="test@company.com",
            priority="medium",
            category="general",
            source="test"
        )
        
        # Then update it
        updates = {
            "status": "in_progress",
            "assigned_team": "Network Support"
        }
        
        updated_ticket = update_ticket(ticket.id, updates)
        
        assert updated_ticket.status == "in_progress"
        assert updated_ticket.assigned_team == "Network Support"


if __name__ == "__main__":
    pytest.main([__file__]) 