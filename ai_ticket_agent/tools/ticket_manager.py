"""Ticket manager tool for creating and managing tickets with database persistence."""

from google.adk.tools import ToolContext
from typing import Dict, Any, Optional
from ai_ticket_agent.database import db_manager
from ai_ticket_agent.models import TicketStatus, TicketPriority, TicketCategory


def create_ticket(
    subject: str,
    description: str,
    user_email: str,
    priority: str = "medium",
    category: Optional[str] = None,
    tool_context: Optional[ToolContext] = None
) -> str:
    """
    Create a new ticket in the database.
    
    Args:
        subject: Ticket subject/summary
        description: Detailed problem description
        user_email: User's email address
        priority: Ticket priority (low, medium, high, critical)
        category: Ticket category (software, hardware, network, etc.)
        tool_context: The ADK tool context
        
    Returns:
        Ticket creation confirmation with ticket ID
    """
    
    session = db_manager.get_session()
    
    try:
        # Validate priority
        try:
            priority_enum = TicketPriority(priority.lower())
        except ValueError:
            return f"ERROR: Invalid priority '{priority}'. Valid options: low, medium, high, critical"
        
        # Validate category if provided
        category_enum = None
        if category:
            try:
                category_enum = TicketCategory(category.lower())
            except ValueError:
                return f"ERROR: Invalid category '{category}'. Valid options: software, hardware, network, security, access, infrastructure, general"
        
        # Create ticket
        ticket = db_manager.create_ticket(
            session=session,
            subject=subject,
            description=description,
            user_email=user_email,
            priority=priority_enum,
            category=category_enum,
            status=TicketStatus.OPEN
        )
        
        # Create initial status update
        db_manager.update_ticket_status(
            session=session,
            ticket_id=ticket.ticket_id,
            status="open",
            message="Ticket created",
            updated_by="ai_agent"
        )
        
        return f"""
**Ticket Created Successfully** ✅

**Ticket ID:** {ticket.ticket_id}
**Subject:** {ticket.subject}
**Status:** {ticket.status.value}
**Priority:** {ticket.priority.value}
**Category:** {ticket.category.value if ticket.category else 'Not specified'}
**User:** {ticket.user_email}
**Created:** {ticket.created_at.strftime('%Y-%m-%d %H:%M:%S') if ticket.created_at else 'N/A'}

The ticket has been created and is ready for processing.
        """
    
    except Exception as e:
        return f"ERROR: Failed to create ticket: {str(e)}"
    
    finally:
        session.close()


def update_ticket(
    ticket_id: str,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_team: Optional[str] = None,
    slack_channel: Optional[str] = None,
    slack_message_ts: Optional[str] = None,
    message: Optional[str] = None,
    tool_context: Optional[ToolContext] = None
) -> str:
    """
    Update ticket information.
    
    Args:
        ticket_id: The ticket ID to update
        status: New status (open, in_progress, resolved, closed, escalated)
        priority: New priority (low, medium, high, critical)
        assigned_team: Team assigned to the ticket
        slack_channel: Slack channel where ticket was posted
        slack_message_ts: Slack message timestamp
        message: Status update message
        tool_context: The ADK tool context
        
    Returns:
        Update confirmation
    """
    
    session = db_manager.get_session()
    
    try:
        # Get existing ticket
        ticket = db_manager.get_ticket(session, ticket_id)
        if not ticket:
            return f"ERROR: Ticket {ticket_id} not found"
        
        # Update fields if provided
        if status:
            try:
                ticket.status = TicketStatus(status.lower())
            except ValueError:
                return f"ERROR: Invalid status '{status}'. Valid options: open, in_progress, resolved, closed, escalated"
        
        if priority:
            try:
                ticket.priority = TicketPriority(priority.lower())
            except ValueError:
                return f"ERROR: Invalid priority '{priority}'. Valid options: low, medium, high, critical"
        
        if assigned_team:
            ticket.assigned_team = assigned_team
        
        if slack_channel:
            ticket.slack_channel = slack_channel
        
        if slack_message_ts:
            ticket.slack_message_ts = slack_message_ts
        
        # Create status update if status changed
        if status:
            db_manager.update_ticket_status(
                session=session,
                ticket_id=ticket_id,
                status=status.lower(),
                message=message or f"Status updated to {status}",
                updated_by="ai_agent"
            )
        else:
            session.commit()
        
        return f"""
**Ticket Updated Successfully** ✅

**Ticket ID:** {ticket.ticket_id}
**Subject:** {ticket.subject}
**Status:** {ticket.status.value}
**Priority:** {ticket.priority.value}
**Assigned Team:** {ticket.assigned_team or 'Not assigned'}
**Slack Channel:** {ticket.slack_channel or 'Not posted'}
**Last Updated:** {ticket.updated_at.strftime('%Y-%m-%d %H:%M:%S') if ticket.updated_at else 'N/A'}
        """
    
    except Exception as e:
        return f"ERROR: Failed to update ticket {ticket_id}: {str(e)}"
    
    finally:
        session.close()


def get_ticket_info(ticket_id: str, tool_context: Optional[ToolContext] = None) -> str:
    """
    Get detailed information about a ticket.
    
    Args:
        ticket_id: The ticket ID to get info for
        tool_context: The ADK tool context
        
    Returns:
        Detailed ticket information
    """
    
    session = db_manager.get_session()
    
    try:
        history = db_manager.get_ticket_history(session, ticket_id)
        if not history:
            return f"ERROR: Ticket {ticket_id} not found"
        
        ticket_info = history["ticket"]
        status_updates = history["status_updates"]
        resolution_attempts = history["resolution_attempts"]
        
        result = f"""
**Ticket Information: {ticket_id}**

**Basic Info:**
- Subject: {ticket_info['subject']}
- Status: {ticket_info['status']}
- Priority: {ticket_info['priority']}
- Category: {ticket_info['category'] or 'Not specified'}
- Assigned Team: {ticket_info['assigned_team'] or 'Not assigned'}
- User: {ticket_info['user_email']}
- Created: {ticket_info['created_at']}
- Updated: {ticket_info['updated_at']}

**Status Updates: {len(status_updates)}**
"""
        
        for update in status_updates:
            result += f"- {update['created_at']}: {update['status']} by {update['updated_by']}"
            if update['message']:
                result += f" - {update['message']}"
            result += "\n"
        
        result += f"""
**Resolution Attempts: {len(resolution_attempts)}**
"""
        
        for attempt in resolution_attempts:
            result += f"- Attempt #{attempt['attempt_number']} ({attempt['created_at']}): {attempt['status']} by {attempt['agent_type']}\n"
        
        return result
    
    except Exception as e:
        return f"ERROR: Failed to get ticket info for {ticket_id}: {str(e)}"
    
    finally:
        session.close()


def search_tickets(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    assigned_team: Optional[str] = None,
    user_email: Optional[str] = None,
    limit: int = 10,
    tool_context: Optional[ToolContext] = None
) -> str:
    """
    Search for tickets with various filters.
    
    Args:
        status: Filter by status
        priority: Filter by priority
        category: Filter by category
        assigned_team: Filter by assigned team
        user_email: Filter by user email
        limit: Maximum number of results
        tool_context: The ADK tool context
        
    Returns:
        Search results
    """
    
    session = db_manager.get_session()
    
    try:
        # Build filters
        filters = {}
        if status:
            filters['status'] = status
        if priority:
            filters['priority'] = priority
        if category:
            filters['category'] = category
        if assigned_team:
            filters['assigned_team'] = assigned_team
        if user_email:
            filters['user_email'] = user_email
        
        filters['limit'] = limit
        
        # Search tickets
        tickets = db_manager.search_tickets(session, **filters)
        
        if not tickets:
            return f"No tickets found matching the criteria."
        
        result = f"""
**Ticket Search Results: {len(tickets)} tickets found**

"""
        
        for ticket in tickets:
            result += f"""
**{ticket.ticket_id}** - {ticket.subject}
- Status: {ticket.status.value}
- Priority: {ticket.priority.value}
- Team: {ticket.assigned_team or 'Not assigned'}
- User: {ticket.user_email}
- Created: {ticket.created_at.strftime('%Y-%m-%d %H:%M:%S') if ticket.created_at else 'N/A'}
"""
        
        return result
    
    except Exception as e:
        return f"ERROR: Failed to search tickets: {str(e)}"
    
    finally:
        session.close()


# The tools are just the functions themselves
create_ticket_tool = create_ticket
update_ticket_tool = update_ticket
get_ticket_info_tool = get_ticket_info
search_tickets_tool = search_tickets 