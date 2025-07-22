"""Database models for ticket tracking and lifecycle management."""

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime

Base = declarative_base()


class TicketStatus(enum.Enum):
    """Ticket status enumeration."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ESCALATED = "escalated"


class TicketPriority(enum.Enum):
    """Ticket priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketCategory(enum.Enum):
    """Ticket category enumeration."""
    SOFTWARE = "software"
    HARDWARE = "hardware"
    NETWORK = "network"
    SECURITY = "security"
    ACCESS = "access"
    INFRASTRUCTURE = "infrastructure"
    GENERAL = "general"


class ResolutionStatus(enum.Enum):
    """Resolution attempt status."""
    SUCCESS = "success"
    FAILED = "failed"
    ESCALATED = "escalated"
    PENDING = "pending"


class Ticket(Base):
    """Main ticket table."""
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(50), unique=True, index=True, nullable=False)
    subject = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    user_email = Column(String(100), nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN, nullable=False)
    priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM, nullable=False)
    category = Column(Enum(TicketCategory), nullable=True)
    assigned_team = Column(String(100), nullable=True)
    slack_channel = Column(String(100), nullable=True)
    slack_message_ts = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    metadata_json = Column(JSON, nullable=True)  # Store additional data like LLM analysis
    
    # Relationships
    status_updates = relationship("TicketStatusUpdate", back_populates="ticket", cascade="all, delete-orphan")
    resolution_attempts = relationship("ResolutionAttempt", back_populates="ticket", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Ticket(id={self.id}, ticket_id='{self.ticket_id}', status='{self.status.value}')>"


class TicketStatusUpdate(Base):
    """Track status changes for tickets."""
    __tablename__ = "ticket_status_updates"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    status = Column(Enum(TicketStatus), nullable=False)
    message = Column(Text, nullable=True)
    updated_by = Column(String(100), nullable=False)  # "ai_agent", "human_team", "user"
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="status_updates")
    
    def __repr__(self):
        return f"<TicketStatusUpdate(id={self.id}, ticket_id={self.ticket_id}, status='{self.status.value}')>"


class ResolutionAttempt(Base):
    """Track resolution attempts and their outcomes."""
    __tablename__ = "resolution_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    attempt_number = Column(Integer, nullable=False, default=1)
    agent_type = Column(String(50), nullable=False)  # "self_service", "escalation"
    solution_provided = Column(Text, nullable=False)
    user_feedback = Column(Text, nullable=True)
    status = Column(Enum(ResolutionStatus), default=ResolutionStatus.PENDING, nullable=False)
    feedback_analysis = Column(Text, nullable=True)  # LLM analysis of user feedback
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="resolution_attempts")
    
    def __repr__(self):
        return f"<ResolutionAttempt(id={self.id}, ticket_id={self.ticket_id}, status='{self.status.value}')>"


class TeamAssignment(Base):
    """Track team assignments and routing decisions."""
    __tablename__ = "team_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    team_name = Column(String(100), nullable=False)
    channel_name = Column(String(100), nullable=False)
    priority = Column(Enum(TicketPriority), nullable=False)
    routing_reason = Column(Text, nullable=True)  # LLM reasoning for routing
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<TeamAssignment(id={self.id}, ticket_id={self.ticket_id}, team='{self.team_name}')>"


# Helper functions for ticket lifecycle management
def generate_ticket_id() -> str:
    """Generate a unique ticket ID."""
    import uuid
    return f"TICKET-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"


def get_ticket_summary(ticket: Ticket) -> dict:
    """Get a summary of ticket information."""
    return {
        "ticket_id": ticket.ticket_id,
        "subject": ticket.subject,
        "status": ticket.status.value,
        "priority": ticket.priority.value,
        "category": ticket.category.value if ticket.category else None,
        "assigned_team": ticket.assigned_team,
        "user_email": ticket.user_email,
        "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
        "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else None,
        "resolution_attempts": len(ticket.resolution_attempts),
        "status_updates": len(ticket.status_updates)
    } 