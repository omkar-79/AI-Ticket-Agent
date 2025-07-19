"""Escalation agent for routing complex IT problems to human teams."""

from google.adk.agents import Agent
from ai_ticket_agent import prompt
from ai_ticket_agent.tools.slack_handlers import slack_escalation_tool
from ai_ticket_agent.tools.team_router import team_router_tool
from ai_ticket_agent.tools.notification_sender import escalation_notification_tool


escalation_agent = Agent(
    model="gemini-2.5-flash",
    name="escalation_agent",
    description="Routes complex IT problems to appropriate human teams via Slack",
    instruction=prompt.ESCALATION_AGENT_INSTR,
    tools=[
        team_router_tool,
        slack_escalation_tool,
        escalation_notification_tool
    ],
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
) 