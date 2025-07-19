"""Root agent for IT Support multi-agent system."""

from google.adk.agents import Agent
from ai_ticket_agent import prompt
from ai_ticket_agent.sub_agents import self_service_agent, escalation_agent
from ai_ticket_agent.tools.problem_analyzer import problem_analyzer_tool
from ai_ticket_agent.tools.email_collector import email_collector_tool


root_agent = Agent(
    model="gemini-2.5-flash",
    name="it_support_root_agent",
    description="IT Support orchestrator that routes problems to appropriate sub-agents",
    instruction=prompt.ROOT_AGENT_INSTR,
    sub_agents=[
        self_service_agent,
        escalation_agent,
    ],
    tools=[problem_analyzer_tool, email_collector_tool],
)
