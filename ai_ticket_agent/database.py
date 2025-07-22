"""Database connection and session management for ticket tracking."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from .models import Base
from typing import Optional

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tickets.db")

# Create engine
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration for development
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False  # Set to True for SQL debugging
    )
else:
    # PostgreSQL configuration for production
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=300
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_database():
    """Initialize the database and create tables."""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise


def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DatabaseManager:
    """Database manager for ticket operations."""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
    
    def create_ticket(self, session: Session, **ticket_data) -> 'Ticket':
        """Create a new ticket."""
        from .models import Ticket, generate_ticket_id
        
        # Generate ticket ID if not provided
        if 'ticket_id' not in ticket_data:
            ticket_data['ticket_id'] = generate_ticket_id()
        
        ticket = Ticket(**ticket_data)
        session.add(ticket)
        session.commit()
        session.refresh(ticket)
        return ticket
    
    def get_ticket(self, session: Session, ticket_id: str) -> Optional['Ticket']:
        """Get ticket by ID."""
        from .models import Ticket
        return session.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    
    def update_ticket_status(self, session: Session, ticket_id: str, status: str, message: Optional[str] = None, updated_by: str = "ai_agent") -> bool:
        """Update ticket status and create status update record."""
        from .models import Ticket, TicketStatus, TicketStatusUpdate
        
        ticket = self.get_ticket(session, ticket_id)
        if not ticket:
            return False
        
        # Update ticket status
        ticket.status = TicketStatus(status)
        
        # Create status update record
        status_update = TicketStatusUpdate(
            ticket_id=ticket.id,
            status=TicketStatus(status),
            message=message,
            updated_by=updated_by
        )
        
        session.add(status_update)
        session.commit()
        return True
    
    def add_resolution_attempt(self, session: Session, ticket_id: str, **attempt_data) -> 'ResolutionAttempt':
        """Add a resolution attempt to a ticket."""
        from .models import Ticket, ResolutionAttempt
        
        ticket = self.get_ticket(session, ticket_id)
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")
        
        # Get attempt number
        attempt_number = len(ticket.resolution_attempts) + 1
        
        resolution_attempt = ResolutionAttempt(
            ticket_id=ticket.id,
            attempt_number=attempt_number,
            **attempt_data
        )
        
        session.add(resolution_attempt)
        session.commit()
        session.refresh(resolution_attempt)
        return resolution_attempt
    
    def get_ticket_history(self, session: Session, ticket_id: str) -> dict:
        """Get complete ticket history including status updates and resolution attempts."""
        from .models import Ticket, get_ticket_summary
        
        ticket = self.get_ticket(session, ticket_id)
        if not ticket:
            return None
        
        history = {
            "ticket": get_ticket_summary(ticket),
            "status_updates": [
                {
                    "status": update.status.value,
                    "message": update.message,
                    "updated_by": update.updated_by,
                    "created_at": update.created_at.isoformat() if update.created_at else None
                }
                for update in ticket.status_updates
            ],
            "resolution_attempts": [
                {
                    "attempt_number": attempt.attempt_number,
                    "agent_type": attempt.agent_type,
                    "solution_provided": attempt.solution_provided,
                    "user_feedback": attempt.user_feedback,
                    "status": attempt.status.value,
                    "feedback_analysis": attempt.feedback_analysis,
                    "created_at": attempt.created_at.isoformat() if attempt.created_at else None
                }
                for attempt in ticket.resolution_attempts
            ]
        }
        
        return history
    
    def search_tickets(self, session: Session, **filters) -> list:
        """Search tickets with various filters."""
        from .models import Ticket, TicketStatus, TicketPriority, TicketCategory
        
        query = session.query(Ticket)
        
        # Apply filters
        if 'status' in filters:
            query = query.filter(Ticket.status == TicketStatus(filters['status']))
        
        if 'priority' in filters:
            query = query.filter(Ticket.priority == TicketPriority(filters['priority']))
        
        if 'category' in filters:
            query = query.filter(Ticket.category == TicketCategory(filters['category']))
        
        if 'assigned_team' in filters:
            query = query.filter(Ticket.assigned_team == filters['assigned_team'])
        
        if 'user_email' in filters:
            query = query.filter(Ticket.user_email == filters['user_email'])
        
        # Order by creation date (newest first)
        query = query.order_by(Ticket.created_at.desc())
        
        # Apply limit if specified
        if 'limit' in filters:
            query = query.limit(filters['limit'])
        
        return query.all()


# Global database manager instance
db_manager = DatabaseManager() 