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
    user_email: str = Field(description="User email address for notifications")
    created_at: str = Field(description="Creation timestamp")
    updated_at: str = Field(description="Last update timestamp")
    resolved_at: Optional[str] = Field(description="Resolution timestamp")
    resolution_notes: Optional[str] = Field(description="Notes on how the ticket was resolved")
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


class WorkflowState(BaseModel):
    """Workflow state for ticket processing."""
    
    ticket_id: str = Field(description="Ticket identifier")
    current_step: str = Field(description="Current workflow step")
    next_step: str = Field(description="Next workflow step")
    completed_steps: List[str] = Field(description="List of completed steps")
    step_data: Dict[str, Any] = Field(description="Data from each step")
    status: str = Field(description="Workflow status: active, completed, failed")
    created_at: str = Field(description="Creation timestamp")
    updated_at: str = Field(description="Last update timestamp")


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
            user_email TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            resolved_at TEXT,
            resolution_notes TEXT,
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
    
    # Create workflow_state table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workflow_state (
            ticket_id TEXT PRIMARY KEY,
            current_step TEXT NOT NULL,
            next_step TEXT NOT NULL,
            completed_steps TEXT NOT NULL,
            step_data TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
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
    user_email: str,
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
        user_email: The user's email address for notifications
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
        user_email=user_email,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
        resolved_at=None,
        resolution_notes=None,
        sla_target=sla_target,
        tags=tags
    )
    
    # Save to database
    db_path = os.getenv("DATABASE_URL", "sqlite:///./helpdesk.db").replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO tickets (id, subject, description, status, priority, category, 
                       assigned_team, assigned_agent, created_by, user_email, created_at, 
                       updated_at, resolved_at, resolution_notes, sla_target, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        ticket.id, ticket.subject, ticket.description, ticket.status, ticket.priority,
        ticket.category, ticket.assigned_team, ticket.assigned_agent, ticket.created_by,
        ticket.user_email, ticket.created_at, ticket.updated_at, ticket.resolved_at, ticket.resolution_notes, ticket.sla_target,
        ",".join(ticket.tags) if ticket.tags else ""
    ))
    
    conn.commit()
    conn.close()
    
    return ticket


def create_ticket_and_start_workflow(
    subject: str,
    description: str,
    user_email: str,
    source: str = "user_message"
) -> Dict[str, Any]:
    """
    Creates a new ticket and initializes its workflow state in the database.
    This should be the very first action for any new user issue.

    Args:
        subject: The subject line of the ticket.
        description: The full description of the issue.
        user_email: The email address of the user reporting the issue (MANDATORY).
        source: The source of the ticket (e.g., 'user_message', 'email').

    Returns:
        A dictionary containing the new ticket_id and the initial workflow state.
    """
    # Validate that user_email is provided and not empty
    if not user_email or not user_email.strip():
        return {
            "error": "user_email is mandatory and cannot be empty. Please provide a valid email address."
        }
    
    # Basic email validation
    if "@" not in user_email or "." not in user_email:
        return {
            "error": "Invalid email format. Please provide a valid email address."
        }
    
    try:
        # Create the ticket with a default 'needs classification' state
        ticket = create_ticket(
            subject=subject,
            description=description,
            category="uncategorized",
            priority="medium",
            created_by=user_email,
            user_email=user_email,
            tags=[]
        )

        # Initialize the workflow for the new ticket
        workflow_state = create_workflow_state(
            ticket_id=ticket.id,
            current_step="START",
            next_step="CLASSIFICATION"
        )
        
        print(f"✅ Ticket created successfully: {ticket.id}")
        print(f"📧 User email stored: {user_email}")
        
        return {
            "ticket_id": ticket.id,
            "message": "Ticket created and workflow initiated.",
            "next_step": workflow_state.next_step,
            "user_email": user_email
        }
    except Exception as e:
        print(f"❌ Error in create_ticket_and_start_workflow: {e}")
        return {"error": str(e)}


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
        # Handle NULL values properly
        updated_at = row[11] if row[11] is not None else row[10]  # Use created_at if updated_at is NULL
        resolved_at = row[12] if row[12] is not None else None
        resolution_notes = row[13] if row[13] is not None else None
        assigned_agent = row[7] if row[7] is not None else None
        
        return Ticket(
            id=row[0],
            subject=row[1],
            description=row[2],
            status=row[3],
            priority=row[4],
            category=row[5],
            assigned_team=row[6] or "",
            assigned_agent=assigned_agent,
            created_by=row[8],
            user_email=row[9],
            created_at=row[10],
            updated_at=updated_at,
            resolved_at=resolved_at,
            resolution_notes=resolution_notes,
            sla_target=row[14],
            tags=row[15].split(",") if row[15] else []
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
        # Handle NULL values properly
        updated_at = row[11] if row[11] is not None else row[10]  # Use created_at if updated_at is NULL
        resolved_at = row[12] if row[12] is not None else None
        resolution_notes = row[13] if row[13] is not None else None
        assigned_agent = row[7] if row[7] is not None else None
        
        return Ticket(
            id=row[0],
            subject=row[1],
            description=row[2],
            status=row[3],
            priority=row[4],
            category=row[5],
            assigned_team=row[6] or "",
            assigned_agent=assigned_agent,
            created_by=row[8],
            user_email=row[9],
            created_at=row[10],
            updated_at=updated_at,
            resolved_at=resolved_at,
            resolution_notes=resolution_notes,
            sla_target=row[14],
            tags=row[15].split(",") if row[15] else []
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
        # Handle NULL values properly
        updated_at = row[11] if row[11] is not None else row[10]  # Use created_at if updated_at is NULL
        resolved_at = row[12] if row[12] is not None else None
        resolution_notes = row[13] if row[13] is not None else None
        assigned_agent = row[7] if row[7] is not None else None
        
        tickets.append(Ticket(
            id=row[0],
            subject=row[1],
            description=row[2],
            status=row[3],
            priority=row[4],
            category=row[5],
            assigned_team=row[6] or "",
            assigned_agent=assigned_agent,
            created_by=row[8],
            user_email=row[9],
            created_at=row[10],
            updated_at=updated_at,
            resolved_at=resolved_at,
            resolution_notes=resolution_notes,
            sla_target=row[14],
            tags=row[15].split(",") if row[15] else []
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


def create_workflow_state(
    ticket_id: str,
    current_step: str = "CLASSIFICATION",
    next_step: str = "KNOWLEDGE_SEARCH"
) -> WorkflowState:
    """
    Create a new workflow state for a ticket.
    
    Args:
        ticket_id: The ticket identifier
        current_step: The current workflow step
        next_step: The next workflow step
        
    Returns:
        WorkflowState: The created workflow state
    """
    init_database()
    
    workflow_state = WorkflowState(
        ticket_id=ticket_id,
        current_step=current_step,
        next_step=next_step,
        completed_steps=[],
        step_data={},
        status="active",
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )
    
    # Save to database
    db_path = os.getenv("DATABASE_URL", "sqlite:///./helpdesk.db").replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO workflow_state 
        (ticket_id, current_step, next_step, completed_steps, step_data, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        workflow_state.ticket_id,
        workflow_state.current_step,
        workflow_state.next_step,
        ",".join(workflow_state.completed_steps),
        str(workflow_state.step_data),
        workflow_state.status,
        workflow_state.created_at,
        workflow_state.updated_at
    ))
    
    conn.commit()
    conn.close()
    
    return workflow_state


def get_workflow_state(
    ticket_id: str
) -> Optional[WorkflowState]:
    """
    Get the workflow state for a ticket.
    
    Args:
        ticket_id: The ticket identifier
        
    Returns:
        Optional[WorkflowState]: The workflow state if found, None otherwise
    """
    init_database()
    
    print(f"DEBUG: get_workflow_state called for ticket_id: {ticket_id}")
    
    db_path = os.getenv("DATABASE_URL", "sqlite:///./helpdesk.db").replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT ticket_id, current_step, next_step, completed_steps, step_data, status, created_at, updated_at
        FROM workflow_state
        WHERE ticket_id = ?
    ''', (ticket_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    print(f"DEBUG: Database query result: {row}")
    
    if row:
        # Parse step_data from string back to dict
        import ast
        step_data_raw = row[4]
        print(f"DEBUG: Raw step_data from database: {step_data_raw}")
        
        try:
            step_data = ast.literal_eval(step_data_raw) if step_data_raw else {}
            print(f"DEBUG: Parsed step_data: {step_data}")
        except Exception as e:
            print(f"DEBUG: Error parsing step_data: {e}")
            step_data = {}
        
        completed_steps = row[3].split(",") if row[3] else []
        
        workflow_state = WorkflowState(
            ticket_id=row[0],
            current_step=row[1],
            next_step=row[2],
            completed_steps=completed_steps,
            step_data=step_data,
            status=row[5],
            created_at=row[6],
            updated_at=row[7]
        )
        
        print(f"DEBUG: Created WorkflowState: {workflow_state}")
        return workflow_state
    
    print(f"DEBUG: No workflow state found for ticket_id: {ticket_id}")
    return None


def update_workflow_state(
    ticket_id: str,
    current_step: str = None,
    next_step: str = None,
    step_data: Dict[str, Any] = None,
    status: str = None
) -> WorkflowState:
    """
    Update the workflow state for a ticket.
    
    Args:
        ticket_id: The ticket identifier
        current_step: The current workflow step
        next_step: The next workflow step
        step_data: Data to store for the current step
        status: The workflow status
        
    Returns:
        WorkflowState: The updated workflow state
    """
    init_database()
    
    print(f"DEBUG: update_workflow_state called with step_data: {step_data}")
    
    # Get current state
    current_state = get_workflow_state(ticket_id)
    if not current_state:
        print(f"DEBUG: No current state found, creating new workflow state")
        return create_workflow_state(ticket_id, current_step or "CLASSIFICATION", next_step or "KNOWLEDGE_SEARCH")
    
    print(f"DEBUG: Current state step_data before update: {current_state.step_data}")
    
    # Update fields
    if current_step:
        current_state.current_step = current_step
        if current_step not in current_state.completed_steps:
            current_state.completed_steps.append(current_step)
    
    if next_step:
        current_state.next_step = next_step
    
    if step_data:
        print(f"DEBUG: Updating step_data with: {step_data}")
        current_state.step_data.update(step_data)
        print(f"DEBUG: Step_data after update: {current_state.step_data}")
    
    if status:
        current_state.status = status
    
    current_state.updated_at = datetime.now().isoformat()
    
    # Save to database
    db_path = os.getenv("DATABASE_URL", "sqlite:///./helpdesk.db").replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    step_data_str = str(current_state.step_data)
    print(f"DEBUG: Storing step_data as string: {step_data_str}")
    
    cursor.execute('''
        UPDATE workflow_state 
        SET current_step = ?, next_step = ?, completed_steps = ?, step_data = ?, status = ?, updated_at = ?
        WHERE ticket_id = ?
    ''', (
        current_state.current_step,
        current_state.next_step,
        ",".join(current_state.completed_steps),
        step_data_str,
        current_state.status,
        current_state.updated_at,
        current_state.ticket_id
    ))
    
    conn.commit()
    conn.close()
    
    print(f"DEBUG: Workflow state updated successfully")
    return current_state


def get_next_workflow_step(
    ticket_id: str
) -> Optional[str]:
    """
    Get the next workflow step for a ticket.
    
    Args:
        ticket_id: The ticket identifier
        
    Returns:
        Optional[str]: The next step if found, None otherwise
    """
    workflow_state = get_workflow_state(ticket_id)
    return workflow_state.next_step if workflow_state else None


def get_step_data(
    ticket_id: str,
    step: str
) -> Dict[str, Any]:
    """
    Get data from a specific workflow step.
    
    Args:
        ticket_id: The ticket identifier
        step: The workflow step
        
    Returns:
        Dict[str, Any]: The step data
    """
    workflow_state = get_workflow_state(ticket_id)
    if workflow_state and step in workflow_state.step_data:
        return workflow_state.step_data[step]
    return {}


def set_step_data(
    ticket_id: str,
    step: str,
    data: Dict[str, Any]
) -> WorkflowState:
    """
    Set data for a specific workflow step.
    
    Args:
        ticket_id: The ticket identifier
        step: The workflow step
        data: The data to store
        
    Returns:
        WorkflowState: The updated workflow state
    """
    workflow_state = get_workflow_state(ticket_id)
    if not workflow_state:
        workflow_state = create_workflow_state(ticket_id)
    
    step_data = {step: data}
    return update_workflow_state(ticket_id, step_data=step_data)


def get_current_workflow_status(
    ticket_id: str
) -> Dict[str, Any]:
    """
    Get the current workflow status for a ticket.
    
    Args:
        ticket_id: The ticket identifier
        
    Returns:
        Dict[str, Any]: Current workflow status with next step and completed steps
    """
    workflow_state = get_workflow_state(ticket_id)
    if not workflow_state:
        return {
            "status": "not_found",
            "current_step": None,
            "next_step": "CLASSIFICATION",
            "completed_steps": [],
            "message": "No workflow state found for this ticket"
        }
    
    return {
        "status": workflow_state.status,
        "current_step": workflow_state.current_step,
        "next_step": workflow_state.next_step,
        "completed_steps": workflow_state.completed_steps,
        "message": f"Current step: {workflow_state.current_step}, Next step: {workflow_state.next_step}"
    }


def get_workflow_summary(
    ticket_id: str
) -> Dict[str, Any]:
    """
    Get a summary of the workflow for a ticket including all step data.
    
    Args:
        ticket_id: The ticket identifier
        
    Returns:
        Dict[str, Any]: Complete workflow summary
    """
    workflow_state = get_workflow_state(ticket_id)
    if not workflow_state:
        return {"error": "No workflow state found"}
    
    return {
        "ticket_id": workflow_state.ticket_id,
        "status": workflow_state.status,
        "current_step": workflow_state.current_step,
        "next_step": workflow_state.next_step,
        "completed_steps": workflow_state.completed_steps,
        "step_data": workflow_state.step_data,
        "created_at": workflow_state.created_at,
        "updated_at": workflow_state.updated_at
    }


def continue_workflow(
    ticket_id: str
) -> Dict[str, Any]:
    """
    Continue the workflow by checking the current status and determining the next action.
    
    Args:
        ticket_id: The ticket identifier
        
    Returns:
        Dict[str, Any]: Information about the next step in the workflow
    """
    workflow_state = get_workflow_state(ticket_id)
    if not workflow_state:
        return {
            "error": "No workflow state found",
            "next_action": "create_workflow",
            "message": "Workflow state not found for this ticket"
        }
    
    next_step = workflow_state.next_step
    
    # Map next steps to agent names
    step_to_agent = {
        "CLASSIFICATION": "classifier_agent",
        "KNOWLEDGE_SEARCH": "knowledge_agent", 
        "ASSIGNMENT": "assignment_agent"
        # FOLLOW_UP removed from main workflow
    }
    
    if next_step in step_to_agent:
        return {
            "status": "continue",
            "next_step": next_step,
            "next_agent": step_to_agent[next_step],
            "ticket_id": ticket_id,
            "message": f"Continue workflow: transfer to {step_to_agent[next_step]} for {next_step}"
        }
    elif next_step == "COMPLETE":
        # Workflow is complete - solution found or ticket assigned
        return {
            "status": "complete",
            "next_step": "COMPLETE",
            "message": "Workflow complete. Solution provided or ticket assigned for human processing."
        }
    # FOLLOW_UP is only for feedback, not main workflow
    else:
        return {
            "status": "complete",
            "next_step": next_step,
            "message": f"Workflow complete. Final step: {next_step}"
        }


def get_ticket_user_email(ticket_id: str) -> Optional[str]:
    """
    Get the user email for a ticket.
    
    Args:
        ticket_id: The ticket identifier
        
    Returns:
        str: The user email address, or None if not found
    """
    db_path = os.getenv("DATABASE_URL", "sqlite:///./helpdesk.db").replace("sqlite:///", "")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT user_email FROM tickets WHERE id = ?
    ''', (ticket_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else None


def get_ticket_info(ticket_id: str) -> Optional[Dict[str, Any]]:
    """
    Get ticket information as a dictionary for use by sub-agents.
    
    Args:
        ticket_id: The ticket identifier
        
    Returns:
        Dict[str, Any]: Ticket information as a dictionary, or None if not found
    """
    db_path = os.getenv("DATABASE_URL", "sqlite:///./helpdesk.db").replace("sqlite:///", "")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, subject, description, status, priority, category, 
               assigned_team, assigned_agent, created_by, user_email, 
               created_at, updated_at, resolved_at, resolution_notes, 
               sla_target, tags
        FROM tickets WHERE id = ?
    ''', (ticket_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return None
    
    # Convert to dictionary
    ticket_info = {
        "id": result[0],
        "subject": result[1],
        "description": result[2],
        "status": result[3],
        "priority": result[4],
        "category": result[5],
        "assigned_team": result[6],
        "assigned_agent": result[7],
        "created_by": result[8],
        "user_email": result[9],
        "created_at": result[10],
        "updated_at": result[11],
        "resolved_at": result[12],
        "resolution_notes": result[13],
        "sla_target": result[14],
        "tags": result[15].split(',') if result[15] else []
    }
    
    return ticket_info 