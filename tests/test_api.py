"""API tests for AI Ticket Agent."""

import pytest
from fastapi.testclient import TestClient
from ai_ticket_agent.main import app

client = TestClient(app)


class TestAPIEndpoints:
    """Test cases for API endpoints."""
    
    def test_root_endpoint(self):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "AI Ticket Agent API"
        assert data["version"] == "0.1.0"
    
    def test_health_check(self):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_create_ticket(self):
        """Test ticket creation endpoint."""
        ticket_data = {
            "subject": "Test VPN Issue",
            "description": "My VPN keeps disconnecting",
            "user_email": "test@company.com",
            "priority": "medium",
            "category": "network",
            "source": "api"
        }
        
        response = client.post("/tickets", json=ticket_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["subject"] == ticket_data["subject"]
        assert data["user_email"] == ticket_data["user_email"]
        assert data["status"] == "open"
        assert "id" in data
    
    def test_get_ticket(self):
        """Test ticket retrieval endpoint."""
        # First create a ticket
        ticket_data = {
            "subject": "Test Ticket",
            "description": "Test description",
            "user_email": "test@company.com",
            "priority": "low",
            "category": "general",
            "source": "api"
        }
        
        create_response = client.post("/tickets", json=ticket_data)
        ticket_id = create_response.json()["id"]
        
        # Then retrieve it
        response = client.get(f"/tickets/{ticket_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == ticket_id
        assert data["subject"] == ticket_data["subject"]
    
    def test_get_nonexistent_ticket(self):
        """Test retrieving a non-existent ticket."""
        response = client.get("/tickets/nonexistent-id")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_list_tickets(self):
        """Test ticket listing endpoint."""
        response = client.get("/tickets")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_list_tickets_with_filters(self):
        """Test ticket listing with filters."""
        response = client.get("/tickets?status=open&priority=medium")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_update_ticket(self):
        """Test ticket update endpoint."""
        # First create a ticket
        ticket_data = {
            "subject": "Test Ticket",
            "description": "Test description",
            "user_email": "test@company.com",
            "priority": "low",
            "category": "general",
            "source": "api"
        }
        
        create_response = client.post("/tickets", json=ticket_data)
        ticket_id = create_response.json()["id"]
        
        # Then update it
        update_data = {
            "status": "in_progress",
            "assigned_team": "Network Support"
        }
        
        response = client.put(f"/tickets/{ticket_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "in_progress"
        assert data["assigned_team"] == "Network Support"
    
    def test_update_nonexistent_ticket(self):
        """Test updating a non-existent ticket."""
        update_data = {"status": "closed"}
        response = client.put("/tickets/nonexistent-id", json=update_data)
        assert response.status_code == 404
    
    def test_agent_process(self):
        """Test agent processing endpoint."""
        request_data = {
            "message": "I need help with VPN connectivity",
            "context": {"user_role": "employee"}
        }
        
        response = client.post("/agent/process", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data
        assert "actions_taken" in data
        assert "next_steps" in data
    
    def test_agent_process_with_ticket_id(self):
        """Test agent processing with ticket ID."""
        # First create a ticket
        ticket_data = {
            "subject": "Test Ticket",
            "description": "Test description",
            "user_email": "test@company.com",
            "priority": "low",
            "category": "general",
            "source": "api"
        }
        
        create_response = client.post("/tickets", json=ticket_data)
        ticket_id = create_response.json()["id"]
        
        # Then process with agent
        request_data = {
            "message": "Update this ticket",
            "ticket_id": ticket_id
        }
        
        response = client.post("/agent/process", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["ticket_id"] == ticket_id
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint."""
        response = client.get("/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_tickets" in data
        assert "open_tickets" in data
        assert "closed_tickets" in data
        assert "priority_distribution" in data
        assert "category_distribution" in data
        assert "team_distribution" in data
        assert "timestamp" in data


class TestAPIValidation:
    """Test cases for API validation."""
    
    def test_create_ticket_missing_required_fields(self):
        """Test ticket creation with missing required fields."""
        ticket_data = {
            "subject": "Test Ticket"
            # Missing description and user_email
        }
        
        response = client.post("/tickets", json=ticket_data)
        assert response.status_code == 422  # Validation error
    
    def test_create_ticket_invalid_priority(self):
        """Test ticket creation with invalid priority."""
        ticket_data = {
            "subject": "Test Ticket",
            "description": "Test description",
            "user_email": "test@company.com",
            "priority": "invalid_priority",
            "category": "general",
            "source": "api"
        }
        
        response = client.post("/tickets", json=ticket_data)
        # This should still work as we don't validate enum values in the mock
        assert response.status_code == 200
    
    def test_update_ticket_empty_updates(self):
        """Test ticket update with empty updates."""
        # First create a ticket
        ticket_data = {
            "subject": "Test Ticket",
            "description": "Test description",
            "user_email": "test@company.com",
            "priority": "low",
            "category": "general",
            "source": "api"
        }
        
        create_response = client.post("/tickets", json=ticket_data)
        ticket_id = create_response.json()["id"]
        
        # Then try to update with empty data
        response = client.put(f"/tickets/{ticket_id}", json={})
        assert response.status_code == 400
        assert "No valid updates provided" in response.json()["detail"]


if __name__ == "__main__":
    pytest.main([__file__]) 