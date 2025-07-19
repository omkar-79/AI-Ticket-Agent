"""Self-service agent for resolving common IT problems."""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from ai_ticket_agent import prompt
from ai_ticket_agent.tools.knowledge_base import knowledge_search_tool
from ai_ticket_agent.tools.resolution_tracker import resolution_tracker_tool
from ai_ticket_agent.tools.notification_sender import solution_notification_tool
from ai_ticket_agent.sub_agents.escalation.agent import escalation_agent

# Agent tool for escalating to human team when self-service fails
escalation_tool = AgentTool(agent=escalation_agent)

self_service_agent = Agent(
    model="gemini-2.5-flash",
    name="self_service_agent",
    description="Resolves common IT problems through self-service solutions",
    instruction=prompt.SELF_SERVICE_AGENT_INSTR,
    tools=[
        knowledge_search_tool,
        resolution_tracker_tool,
        solution_notification_tool,
        escalation_tool
    ],
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
) 