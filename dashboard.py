import streamlit as st
import pandas as pd
from ai_ticket_agent.tools.database import search_tickets, get_ticket, get_workflow_state

st.set_page_config(page_title="AI Ticket Agent Dashboard", layout="wide")
st.title("🎫 AI Ticket Agent - Ticket Management Dashboard")

# Sidebar filters
st.sidebar.header("Filter Tickets")
status = st.sidebar.selectbox("Status", [None, "open", "in_progress", "resolved", "closed"], index=0)
priority = st.sidebar.selectbox("Priority", [None, "critical", "high", "medium", "low"], index=0)
category = st.sidebar.selectbox("Category", [None, "hardware", "software", "network", "access", "security", "email", "general"], index=0)
team = st.sidebar.text_input("Assigned Team")

# Fetch tickets
tickets = search_tickets(status=status, priority=priority, category=category, assigned_team=team or None, limit=100)

ticket_data = [
    {
        "ID": t.id,
        "Subject": t.subject,
        "Status": t.status,
        "Priority": t.priority,
        "Category": t.category,
        "Team": t.assigned_team,
        "Agent": t.assigned_agent,
        "Created": t.created_at,
        "Updated": t.updated_at,
    }
    for t in tickets
]

df = pd.DataFrame(ticket_data)

st.subheader(f"Tickets ({len(df)})")
st.dataframe(df, use_container_width=True)

# Ticket selection
selected_id = st.selectbox("Select a ticket to view details", ["-"] + [t.id for t in tickets])
if selected_id and selected_id != "-":
    ticket = get_ticket(selected_id)
    workflow = get_workflow_state(selected_id)
    st.markdown(f"## Ticket: {ticket.subject}")
    st.write(ticket)
    if workflow:
        st.markdown("### Workflow State")
        st.json({
            "Current Step": workflow.current_step,
            "Next Step": workflow.next_step,
            "Completed Steps": workflow.completed_steps,
            "Status": workflow.status,
            "Step Data": workflow.step_data,
        })

# Stats
st.sidebar.header("Ticket Stats")
if len(df) > 0:
    st.sidebar.metric("Open Tickets", len(df[df["Status"] == "open"]))
    st.sidebar.metric("Closed Tickets", len(df[df["Status"] == "closed"]))
    st.sidebar.metric("Critical", len(df[df["Priority"] == "critical"]))
    st.sidebar.metric("High", len(df[df["Priority"] == "high"]))
    st.sidebar.metric("Medium", len(df[df["Priority"] == "medium"]))
    st.sidebar.metric("Low", len(df[df["Priority"] == "low"])) 