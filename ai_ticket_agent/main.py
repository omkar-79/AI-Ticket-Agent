"""Main FastAPI application for IT Helpdesk Ticket Orchestration."""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
from datetime import datetime

from ai_ticket_agent.agent import root_agent
from ai_ticket_agent.tools.database import create_ticket, get_ticket, search_tickets, update_ticket_fields
from ai_ticket_agent.tools.notifications import send_notification


app = FastAPI(
    title="AI Ticket Agent API",
    description="Autonomous IT Helpdesk Ticket Orchestration API",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API
class TicketCreate(BaseModel):
    subject: str
    description: str
    user_email: str
    priority: str = "medium"
    category: str = "general"
    source: str = "api"


class TicketUpdate(BaseModel):
    subject: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    assigned_team: Optional[str] = None


class TicketResponse(BaseModel):
    id: str
    subject: str
    description: str
    created_by: str
    priority: str
    category: str
    status: str
    assigned_team: str
    assigned_agent: Optional[str] = None
    created_at: str
    updated_at: str
    resolved_at: Optional[str] = None
    sla_target: str
    tags: List[str] = []


class AgentRequest(BaseModel):
    message: str
    ticket_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class AgentResponse(BaseModel):
    response: str
    ticket_id: Optional[str] = None
    actions_taken: List[str]
    next_steps: List[str]


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AI Ticket Agent API",
        "version": "0.1.0",
        "description": "Autonomous IT Helpdesk Ticket Orchestration",
        "endpoints": {
            "tickets": "/tickets",
            "agent": "/agent/process",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "AI Ticket Agent"
    }


@app.post("/tickets", response_model=TicketResponse)
async def create_new_ticket(ticket: TicketCreate):
    """Create a new IT support ticket."""
    try:
        created_ticket = create_ticket(
            subject=ticket.subject,
            description=ticket.description,
            category=ticket.category,
            priority=ticket.priority,
            created_by=ticket.user_email,
            user_email=ticket.user_email,
            tags=[]
        )
        
        # Send confirmation notification
        send_notification(
            recipient=ticket.user_email,
            subject=f"Ticket Created: {ticket.subject}",
            message=f"Your ticket has been created with ID: {created_ticket.id}",
            notification_type="email",
            priority="normal"
        )
        
        return TicketResponse(**created_ticket.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create ticket: {str(e)}")


@app.get("/tickets/{ticket_id}", response_model=TicketResponse)
async def get_ticket_by_id(ticket_id: str):
    """Get a specific ticket by ID."""
    ticket = get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return TicketResponse(**ticket.dict())


@app.get("/tickets", response_model=List[TicketResponse])
async def get_tickets(
    status: Optional[str] = None,
    team: Optional[str] = None,
    priority: Optional[str] = None
):
    """List tickets with optional filtering."""
    tickets = search_tickets(status=status, assigned_team=team, priority=priority)
    return [TicketResponse(**ticket.dict()) for ticket in tickets]


@app.put("/tickets/{ticket_id}", response_model=TicketResponse)
async def update_ticket_by_id(ticket_id: str, updates: TicketUpdate):
    """Update a specific ticket."""
    # Remove None values
    update_data = {k: v for k, v in updates.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid updates provided")
    
    try:
        updated_ticket = update_ticket_fields(ticket_id, update_data)
        return TicketResponse(**updated_ticket.dict())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update ticket: {str(e)}")


@app.post("/agent/process", response_model=AgentResponse)
async def process_with_agent(request: AgentRequest):
    """Process a request using the AI agent system."""
    try:
        # This would integrate with the ADK agent system
        # For now, returning a mock response
        response = f"Processing request: {request.message}"
        
        if request.ticket_id:
            response += f" for ticket {request.ticket_id}"
        
        return AgentResponse(
            response=response,
            ticket_id=request.ticket_id,
            actions_taken=["Request received", "Agent processing initiated"],
            next_steps=["Awaiting agent response", "Ticket classification"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent processing failed: {str(e)}")


@app.get("/metrics")
async def get_metrics():
    """Get system metrics and performance data."""
    tickets = search_tickets()
    
    metrics = {
        "total_tickets": len(tickets),
        "open_tickets": len([t for t in tickets if t.status == "open"]),
        "closed_tickets": len([t for t in tickets if t.status == "closed"]),
        "priority_distribution": {},
        "category_distribution": {},
        "team_distribution": {},
        "timestamp": datetime.now().isoformat()
    }
    
    # Calculate distributions
    for ticket in tickets:
        metrics["priority_distribution"][ticket.priority] = \
            metrics["priority_distribution"].get(ticket.priority, 0) + 1
        metrics["category_distribution"][ticket.category] = \
            metrics["category_distribution"].get(ticket.category, 0) + 1
        metrics["team_distribution"][ticket.assigned_team] = \
            metrics["team_distribution"].get(ticket.assigned_team, 0) + 1
    
    return metrics


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 