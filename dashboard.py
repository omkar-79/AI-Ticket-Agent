#!/usr/bin/env python3
"""Streamlit Dashboard for AI Ticket Agent - Ticket Tracking and Analytics."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_ticket_agent.database import db_manager
from ai_ticket_agent.models import TicketStatus, TicketPriority, TicketCategory, ResolutionStatus


# Page configuration
st.set_page_config(
    page_title="AI Ticket Agent Dashboard",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .status-open { color: #ff7f0e; }
    .status-resolved { color: #2ca02c; }
    .status-escalated { color: #d62728; }
    .priority-critical { color: #d62728; font-weight: bold; }
    .priority-high { color: #ff7f0e; font-weight: bold; }
    .priority-medium { color: #1f77b4; }
    .priority-low { color: #2ca02c; }
</style>
""", unsafe_allow_html=True)


def load_data():
    """Load data from database."""
    session = db_manager.get_session()
    try:
        # Get all tickets with eager loading
        from ai_ticket_agent.models import Ticket
        from sqlalchemy.orm import joinedload
        tickets = session.query(Ticket).options(
            joinedload(Ticket.resolution_attempts),
            joinedload(Ticket.status_updates)
        ).limit(1000).all()
        
        # Convert to DataFrame
        tickets_data = []
        for ticket in tickets:
            tickets_data.append({
                'ticket_id': ticket.ticket_id,
                'subject': ticket.subject,
                'status': ticket.status.value,
                'priority': ticket.priority.value,
                'category': ticket.category.value if ticket.category else 'Not specified',
                'assigned_team': ticket.assigned_team or 'Not assigned',
                'user_email': ticket.user_email,
                'created_at': ticket.created_at,
                'updated_at': ticket.updated_at,
                'resolved_at': ticket.resolved_at,
                'slack_channel': ticket.slack_channel or 'Not posted',
                'resolution_attempts': len(ticket.resolution_attempts),
                'status_updates': len(ticket.status_updates)
            })
        
        df = pd.DataFrame(tickets_data)
        
        # Get resolution attempts data
        resolution_data = []
        for ticket in tickets:
            for attempt in ticket.resolution_attempts:
                resolution_data.append({
                    'ticket_id': ticket.ticket_id,
                    'attempt_number': attempt.attempt_number,
                    'agent_type': attempt.agent_type,
                    'status': attempt.status.value,
                    'created_at': attempt.created_at,
                    'user_feedback': attempt.user_feedback or 'None'
                })
        
        resolution_df = pd.DataFrame(resolution_data)
        
        return df, resolution_df
        
    finally:
        session.close()


def main_dashboard():
    """Main dashboard view."""
    st.markdown('<h1 class="main-header">🎫 AI Ticket Agent Dashboard</h1>', unsafe_allow_html=True)
    
    # Show last updated time
    st.caption(f"🕐 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load data
    df, resolution_df = load_data()
    
    if df.empty:
        st.warning("No tickets found in the database. Create some tickets first!")
        return
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_tickets = len(df)
        st.metric("Total Tickets", total_tickets)
    
    with col2:
        open_tickets = len(df[df['status'] == 'open'])
        st.metric("Open Tickets", open_tickets, delta=open_tickets)
    
    with col3:
        resolved_tickets = len(df[df['status'] == 'resolved'])
        st.metric("Resolved Tickets", resolved_tickets)
    
    with col4:
        escalated_tickets = len(df[df['status'] == 'escalated'])
        st.metric("Escalated Tickets", escalated_tickets)
    
    st.divider()
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        # Status Distribution
        status_counts = df['status'].value_counts()
        fig_status = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Ticket Status Distribution",
            color_discrete_map={
                'open': '#ff7f0e',
                'resolved': '#2ca02c',
                'escalated': '#d62728',
                'in_progress': '#1f77b4',
                'closed': '#9467bd'
            }
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Priority Distribution
        priority_counts = df['priority'].value_counts()
        fig_priority = px.bar(
            x=priority_counts.index,
            y=priority_counts.values,
            title="Ticket Priority Distribution",
            color=priority_counts.values,
            color_continuous_scale='RdYlGn_r'
        )
        fig_priority.update_layout(xaxis_title="Priority", yaxis_title="Count")
        st.plotly_chart(fig_priority, use_container_width=True)
    
    # Category and Team Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Category Distribution
        category_counts = df['category'].value_counts()
        fig_category = px.bar(
            x=category_counts.index,
            y=category_counts.values,
            title="Ticket Category Distribution",
            color=category_counts.values,
            color_continuous_scale='viridis'
        )
        fig_category.update_layout(xaxis_title="Category", yaxis_title="Count")
        st.plotly_chart(fig_category, use_container_width=True)
    
    with col2:
        # Team Assignment
        team_counts = df['assigned_team'].value_counts()
        fig_team = px.bar(
            x=team_counts.index,
            y=team_counts.values,
            title="Team Assignment Distribution",
            color=team_counts.values,
            color_continuous_scale='plasma'
        )
        fig_team.update_layout(xaxis_title="Team", yaxis_title="Count")
        st.plotly_chart(fig_team, use_container_width=True)
    
    # Resolution Analysis
    if not resolution_df.empty:
        st.subheader("📊 Resolution Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Resolution Success Rate
            success_rate = len(resolution_df[resolution_df['status'] == 'success']) / len(resolution_df) * 100
            st.metric("Resolution Success Rate", f"{success_rate:.1f}%")
        
        with col2:
            # Average Resolution Attempts
            avg_attempts = resolution_df.groupby('ticket_id')['attempt_number'].max().mean()
            st.metric("Avg Resolution Attempts", f"{avg_attempts:.1f}")
        
        # Resolution Attempts Timeline
        resolution_df['date'] = pd.to_datetime(resolution_df['created_at']).dt.date
        daily_attempts = resolution_df.groupby('date').size().reset_index(name='attempts')
        
        fig_timeline = px.line(
            daily_attempts,
            x='date',
            y='attempts',
            title="Daily Resolution Attempts",
            markers=True
        )
        fig_timeline.update_layout(xaxis_title="Date", yaxis_title="Resolution Attempts")
        st.plotly_chart(fig_timeline, use_container_width=True)


def ticket_management():
    """Ticket management interface."""
    st.header("🎫 Ticket Management")
    
    # Load data
    df, _ = load_data()
    
    if df.empty:
        st.warning("No tickets to display.")
        return
    
    # Search functionality
    st.subheader("🔍 Search Tickets")
    search_term = st.text_input("Search by ticket ID, subject, or user email:")
    
    if search_term:
        # Filter tickets based on search term
        filtered_df = df[
            df['ticket_id'].str.contains(search_term, case=False, na=False) |
            df['subject'].str.contains(search_term, case=False, na=False) |
            df['user_email'].str.contains(search_term, case=False, na=False)
        ]
        st.success(f"Found {len(filtered_df)} tickets matching '{search_term}'")
    else:
        filtered_df = df
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All"] + list(df['status'].unique())
        )
    
    with col2:
        priority_filter = st.selectbox(
            "Filter by Priority",
            ["All"] + list(df['priority'].unique())
        )
    
    with col3:
        team_filter = st.selectbox(
            "Filter by Team",
            ["All"] + list(df['assigned_team'].unique())
        )
    
    # Apply filters
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    if priority_filter != "All":
        filtered_df = filtered_df[filtered_df['priority'] == priority_filter]
    if team_filter != "All":
        filtered_df = filtered_df[filtered_df['assigned_team'] == team_filter]
    
    # Display tickets
    st.subheader(f"Tickets ({len(filtered_df)} found)")
    
    for _, ticket in filtered_df.iterrows():
        with st.expander(f"🎫 {ticket['ticket_id']} - {ticket['subject']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Status:** <span class='status-{ticket['status']}'>{ticket['status'].title()}</span>", unsafe_allow_html=True)
                st.write(f"**Priority:** <span class='priority-{ticket['priority']}'>{ticket['priority'].title()}</span>", unsafe_allow_html=True)
                st.write(f"**Category:** {ticket['category']}")
                st.write(f"**Team:** {ticket['assigned_team']}")
            
            with col2:
                st.write(f"**User:** {ticket['user_email']}")
                st.write(f"**Created:** {ticket['created_at'].strftime('%Y-%m-%d %H:%M')}")
                st.write(f"**Resolution Attempts:** {ticket['resolution_attempts']}")
                st.write(f"**Status Updates:** {ticket['status_updates']}")
            
            # Show ticket details
            if st.button(f"View Details", key=f"details_{ticket['ticket_id']}"):
                show_ticket_details(ticket['ticket_id'])


def show_ticket_details(ticket_id):
    """Show detailed information for a specific ticket."""
    session = db_manager.get_session()
    try:
        history = db_manager.get_ticket_history(session, ticket_id)
        if not history:
            st.error(f"Ticket {ticket_id} not found")
            return
        
        ticket_info = history["ticket"]
        status_updates = history["status_updates"]
        resolution_attempts = history["resolution_attempts"]
        
        st.subheader(f"📋 Ticket Details: {ticket_id}")
        
        # Basic info
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Subject:** {ticket_info['subject']}")
            st.write(f"**Status:** {ticket_info['status']}")
            st.write(f"**Priority:** {ticket_info['priority']}")
            st.write(f"**Category:** {ticket_info['category']}")
        
        with col2:
            st.write(f"**User:** {ticket_info['user_email']}")
            st.write(f"**Team:** {ticket_info['assigned_team']}")
            st.write(f"**Created:** {ticket_info['created_at']}")
            st.write(f"**Updated:** {ticket_info['updated_at']}")
        
        # Status updates
        st.subheader("📈 Status Updates")
        for update in status_updates:
            st.write(f"**{update['created_at']}:** {update['status']} by {update['updated_by']}")
            if update['message']:
                st.write(f"  *{update['message']}*")
        
        # Resolution attempts
        st.subheader("🔧 Resolution Attempts")
        for attempt in resolution_attempts:
            with st.expander(f"Attempt #{attempt['attempt_number']} - {attempt['status']}"):
                st.write(f"**Agent:** {attempt['agent_type']}")
                st.write(f"**Status:** {attempt['status']}")
                st.write(f"**Created:** {attempt['created_at']}")
                st.write(f"**Solution:** {attempt['solution_provided']}")
                if attempt['user_feedback']:
                    st.write(f"**User Feedback:** {attempt['user_feedback']}")
                if attempt['feedback_analysis']:
                    st.write(f"**Analysis:** {attempt['feedback_analysis']}")
    
    finally:
        session.close()


def analytics():
    """Analytics and insights."""
    st.header("📊 Analytics & Insights")
    
    # Load data
    df, resolution_df = load_data()
    
    if df.empty:
        st.warning("No data available for analytics.")
        return
    
    # Time-based analysis
    st.subheader("⏰ Time-based Analysis")
    
    df['created_date'] = pd.to_datetime(df['created_at']).dt.date
    daily_tickets = df.groupby('created_date').size().reset_index(name='tickets')
    
    fig_daily = px.line(
        daily_tickets,
        x='created_date',
        y='tickets',
        title="Daily Ticket Volume",
        markers=True
    )
    fig_daily.update_layout(xaxis_title="Date", yaxis_title="Tickets Created")
    st.plotly_chart(fig_daily, use_container_width=True)
    
    # Resolution time analysis
    resolved_df = df[df['status'] == 'resolved'].copy()
    if not resolved_df.empty:
        resolved_df['resolution_time'] = (
            pd.to_datetime(resolved_df['resolved_at']) - 
            pd.to_datetime(resolved_df['created_at'])
        ).dt.total_seconds() / 3600  # Convert to hours
        
        fig_resolution = px.histogram(
            resolved_df,
            x='resolution_time',
            title="Resolution Time Distribution (Hours)",
            nbins=20
        )
        fig_resolution.update_layout(xaxis_title="Resolution Time (Hours)", yaxis_title="Count")
        st.plotly_chart(fig_resolution, use_container_width=True)
        
        avg_resolution_time = resolved_df['resolution_time'].mean()
        st.metric("Average Resolution Time", f"{avg_resolution_time:.1f} hours")
    
    # Team performance
    st.subheader("👥 Team Performance")
    
    team_stats = df.groupby('assigned_team').agg({
        'ticket_id': 'count',
        'status': lambda x: (x == 'resolved').sum()
    }).rename(columns={'ticket_id': 'total_tickets', 'status': 'resolved_tickets'})
    
    team_stats['resolution_rate'] = (team_stats['resolved_tickets'] / team_stats['total_tickets'] * 100).round(1)
    
    fig_team_perf = px.bar(
        team_stats.reset_index(),
        x='assigned_team',
        y='resolution_rate',
        title="Team Resolution Rate (%)",
        color='resolution_rate',
        color_continuous_scale='RdYlGn'
    )
    fig_team_perf.update_layout(xaxis_title="Team", yaxis_title="Resolution Rate (%)")
    st.plotly_chart(fig_team_perf, use_container_width=True)
    
    # Display team stats table
    st.dataframe(team_stats, use_container_width=True)


def settings():
    """Settings and configuration."""
    st.header("⚙️ Settings & Configuration")
    
    st.subheader("Database Information")
    
    # Check database connection
    try:
        session = db_manager.get_session()
        tickets = db_manager.search_tickets(session, limit=1)
        st.success("✅ Database connection successful")
        
        # Database stats
        total_tickets = len(db_manager.search_tickets(session, limit=10000))
        st.metric("Total Tickets in Database", total_tickets)
        
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
    
    finally:
        session.close()
    
    st.subheader("System Information")
    
    # Environment variables
    env_vars = [
        "GOOGLE_CLOUD_PROJECT",
        "GOOGLE_CLOUD_LOCATION",
        "SLACK_BOT_TOKEN",
        "DATABASE_URL"
    ]
    
    for var in env_vars:
        value = os.getenv(var, "Not set")
        if "TOKEN" in var and value != "Not set":
            value = value[:10] + "..."  # Mask tokens
        st.write(f"**{var}:** {value}")


def main():
    """Main application."""
    # Sidebar navigation
    st.sidebar.title("🎫 AI Ticket Agent")
    
    # Add refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.rerun()
    
    page = st.sidebar.selectbox(
        "Navigation",
        ["Dashboard", "Ticket Management", "Analytics", "Settings"]
    )
    
    # Sidebar metrics
    st.sidebar.markdown("---")
    st.sidebar.subheader("Quick Stats")
    
    try:
        df, _ = load_data()
        if not df.empty:
            open_count = len(df[df['status'] == 'open'])
            resolved_count = len(df[df['status'] == 'resolved'])
            escalated_count = len(df[df['status'] == 'escalated'])
            
            st.sidebar.metric("Open", open_count)
            st.sidebar.metric("Resolved", resolved_count)
            st.sidebar.metric("Escalated", escalated_count)
    except:
        pass
    
    # Page routing
    if page == "Dashboard":
        main_dashboard()
    elif page == "Ticket Management":
        ticket_management()
    elif page == "Analytics":
        analytics()
    elif page == "Settings":
        settings()


if __name__ == "__main__":
    main() 