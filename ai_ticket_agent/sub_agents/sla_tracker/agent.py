"""SLA Tracking Agent for monitoring service level agreements."""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from ai_ticket_agent import prompt
from .tools import check_sla_status, generate_sla_alert, get_team_sla_report


sla_tracker_agent = Agent(
    model="gemini-2.5-flash",
    name="sla_tracker_agent",
    description="Monitors SLA compliance and generates alerts for at-risk tickets",
    instruction=prompt.SLA_TRACKER_AGENT_INSTR,
    tools=[
        FunctionTool(func=check_sla_status),
        FunctionTool(func=generate_sla_alert),
        FunctionTool(func=get_team_sla_report),
    ],
) 