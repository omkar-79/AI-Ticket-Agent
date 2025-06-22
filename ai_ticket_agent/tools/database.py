"""Database tools for the AI Ticket Agent."""

import uuid
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class Ticket(BaseModel):
    """IT support ticket model."""
    
    id: str = Field(description="Unique ticket identifier")
    subject: str = Field(description="Ticket subject")
    description: str = Field(description="Ticket description")
    status: str = Field(description="Ticket status: open, in_progress, resolved, closed")
    priority: str = Field(description="Priority: critical, high, medium, low")
    category: str = Field(description="Category: hardware, software, network, access, security, email, general")
    assigned_team: str = Field(description="Assigned support team")
    assigned_agent: Optional[str] = Field(description="Assigned agent")
    created_by: str = Field(description="User who created the ticket")
    created_at: str = Field(description="Creation timestamp")
    updated_at: str = Field(description="Last update timestamp")
    resolved_at: Optional[str] = Field(description="Resolution timestamp")
    sla_target: str = Field(description="SLA target time")
    tags: List[str] = Field(description="Ticket tags")


class TicketUpdate(BaseModel):
    """Ticket update information."""
    
    ticket_id: str = Field(description="Ticket identifier")
    field: str = Field(description="Field to update")
    old_value: str = Field(description="Previous value")
    new_value: str = Field(description="New value")
    updated_by: str = Field(description="Who made the update")
    timestamp: str = Field(description="Update timestamp")


# SQLite database setup
DB_PATH = "helpdesk.db"


def init_database():
    """Initialize the SQLite database with required tables."""
    db_path = os.getenv("DATABASE_URL", "sqlite:///./helpdesk.db").replace("sqlite:///", "")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tickets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id TEXT PRIMARY KEY,
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'open',
            priority TEXT NOT NULL DEFAULT 'medium',
            category TEXT NOT NULL,
            assigned_team TEXT,
            assigned_agent TEXT,
            created_by TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            resolved_at TEXT,
            sla_target TEXT NOT NULL DEFAULT '8 hours',
            tags TEXT
        )
    ''')
    
    # Create ticket_updates table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ticket_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT NOT NULL,
            field TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT NOT NULL,
            updated_by TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (ticket_id) REFERENCES tickets (id)
        )
    ''')
    
    # Create knowledge_articles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_articles (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT NOT NULL,
            author TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            tags TEXT
        )
    ''')
    
    conn.commit()
    conn.close()


# Remove automatic initialization - let it be called explicitly when needed
# init_database()


def create_ticket(
    subject: str,
    description: str,
    category: str,
    priority: str,
    created_by: str,
    tags: List[str]
) -> Ticket:
    """
    Create a new IT support ticket.
    
    Args:
        subject: The ticket subject
        description: The ticket description
        category: The ticket category
        priority: The ticket priority
        created_by: The user creating the ticket
        tags: List of tags for the ticket
        
    Returns:
        Ticket: The created ticket
    """
    # Initialize database if needed
    init_database()
    
    # Generate ticket ID
    ticket_id = f"TICKET-{datetime.now().strftime('%Y%m%d')}-{os.urandom(4).hex().upper()}"
    
    # Set SLA target based on priority
    sla_targets = {
        "critical": "2 hours",
        "high": "4 hours",
        "medium": "8 hours",
        "low": "24 hours"
    }
    sla_target = sla_targets.get(priority, "8 hours")
    
    # Create ticket
    ticket = Ticket(
        id=ticket_id,
        subject=subject,
        description=description,
        status="open",
        priority=priority,
        category=category,
        assigned_team="",
        assigned_agent=None,
        created_by=created_by,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
        resolved_at=None,
        sla_target=sla_target,
        tags=tags
    )
    
    # Save to database
    db_path = os.getenv("DATABASE_URL", "sqlite:///./helpdesk.db").replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO tickets (id, subject, description, status, priority, category, 
                           assigned_team, assigned_agent, created_by, created_at, 
                           updated_at, resolved_at, sla_target, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        ticket.id, ticket.subject, ticket.description, ticket.status, ticket.priority,
        ticket.category, ticket.assigned_team, ticket.assigned_agent, ticket.created_by,
        ticket.created_at, ticket.updated_at, ticket.resolved_at, ticket.sla_target,
        ",".join(ticket.tags) if ticket.tags else ""
    ))
    
    conn.commit()
    conn.close()
    
    return ticket


def get_ticket(
    ticket_id: str
) -> Optional[Ticket]:
    """
    Retrieve a ticket by its ID.
    
    Args:
        ticket_id: The ticket identifier
        
    Returns:
        Optional[Ticket]: The ticket if found, None otherwise
    """
    init_database()
    
    db_path = os.getenv("DATABASE_URL", "sqlite:///./helpdesk.db").replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return Ticket(
            id=row[0],
            subject=row[1],
            description=row[2],
            status=row[3],
            priority=row[4],
            category=row[5],
            assigned_team=row[6] or "",
            assigned_agent=row[7],
            created_by=row[8],
            created_at=row[9],
            updated_at=row[10],
            resolved_at=row[11],
            sla_target=row[12],
            tags=row[13].split(",") if row[13] else []
        )
    
    return None


def update_ticket(
    ticket_id: str,
    field: str,
    new_value: str,
    updated_by: str
) -> bool:
    """
    Update a ticket field.
    
    Args:
        ticket_id: The ticket identifier
        field: The field to update
        new_value: The new value
        updated_by: Who is making the update
        
    Returns:
        bool: True if update was successful
    """
    init_database()
    
    db_path = os.getenv("DATABASE_URL", "sqlite:///./helpdesk.db").replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get current value
    cursor.execute(f'SELECT {field} FROM tickets WHERE id = ?', (ticket_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return False
    
    old_value = str(result[0]) if result[0] is not None else ""
    
    # Update the field
    cursor.execute(f'UPDATE tickets SET {field} = ?, updated_at = ? WHERE id = ?',
                  (new_value, datetime.now().isoformat(), ticket_id))
    
    # Log the update
    cursor.execute('''
        INSERT INTO ticket_updates (ticket_id, field, old_value, new_value, updated_by, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (ticket_id, field, old_value, new_value, updated_by, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    return True


def update_ticket_fields(
    ticket_id: str,
    updates: Dict[str, str],
    updated_by: str = "system"
) -> Optional[Ticket]:
    """
    Update multiple ticket fields at once.
    
    Args:
        ticket_id: The ticket identifier
        updates: Dictionary of field_name: new_value pairs
        updated_by: Who is making the updates
        
    Returns:
        Optional[Ticket]: The updated ticket if successful, None otherwise
    """
    init_database()
    
    db_path = os.getenv("DATABASE_URL", "sqlite:///./helpdesk.db").replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if ticket exists
    cursor.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,))
    if not cursor.fetchone():
        conn.close()
        return None
    
    # Update each field
    for field, new_value in updates.items():
        # Get current value
        cursor.execute(f'SELECT {field} FROM tickets WHERE id = ?', (ticket_id,))
        result = cursor.fetchone()
        
        if result:
            old_value = str(result[0]) if result[0] is not None else ""
            
            # Update the field
            cursor.execute(f'UPDATE tickets SET {field} = ? WHERE id = ?', (new_value, ticket_id))
            
            # Log the update
            cursor.execute('''
                INSERT INTO ticket_updates (ticket_id, field, old_value, new_value, updated_by, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (ticket_id, field, old_value, new_value, updated_by, datetime.now().isoformat()))
    
    # Update the updated_at timestamp
    cursor.execute('UPDATE tickets SET updated_at = ? WHERE id = ?', 
                  (datetime.now().isoformat(), ticket_id))
    
    conn.commit()
    
    # Get the updated ticket
    cursor.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return Ticket(
            id=row[0],
            subject=row[1],
            description=row[2],
            status=row[3],
            priority=row[4],
            category=row[5],
            assigned_team=row[6] or "",
            assigned_agent=row[7],
            created_by=row[8],
            created_at=row[9],
            updated_at=row[10],
            resolved_at=row[11],
            sla_target=row[12],
            tags=row[13].split(",") if row[13] else []
        )
    
    return None


def search_tickets(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    assigned_team: Optional[str] = None,
    limit: int = 50
) -> List[Ticket]:
    """
    Search for tickets with various filters.
    
    Args:
        status: Filter by ticket status
        priority: Filter by priority level
        category: Filter by category
        assigned_team: Filter by assigned team
        limit: Maximum number of results
        
    Returns:
        List[Ticket]: List of matching tickets
    """
    init_database()
    
    db_path = os.getenv("DATABASE_URL", "sqlite:///./helpdesk.db").replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Build query
    query = 'SELECT * FROM tickets WHERE 1=1'
    params = []
    
    if status:
        query += ' AND status = ?'
        params.append(status)
    
    if priority:
        query += ' AND priority = ?'
        params.append(priority)
    
    if category:
        query += ' AND category = ?'
        params.append(category)
    
    if assigned_team:
        query += ' AND assigned_team = ?'
        params.append(assigned_team)
    
    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    conn.close()
    
    tickets = []
    for row in rows:
        tickets.append(Ticket(
            id=row[0],
            subject=row[1],
            description=row[2],
            status=row[3],
            priority=row[4],
            category=row[5],
            assigned_team=row[6] or "",
            assigned_agent=row[7],
            created_by=row[8],
            created_at=row[9],
            updated_at=row[10],
            resolved_at=row[11],
            sla_target=row[12],
            tags=row[13].split(",") if row[13] else []
        ))
    
    return tickets


def close_ticket_db(
    ticket_id: str,
    resolution: str
) -> Ticket:
    """
    Close a ticket with resolution details.
    
    Args:
        ticket_id: The ticket identifier
        resolution: Resolution details
        
    Returns:
        Ticket: The closed ticket
    """
    return update_ticket(ticket_id, "status", "closed", "") 