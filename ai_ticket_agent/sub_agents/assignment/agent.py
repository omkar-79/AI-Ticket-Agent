"""Ticket Assignment Agent for routing tickets to appropriate teams."""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from ai_ticket_agent import prompt
from .tools import assign_ticket, get_team_workload
from ai_ticket_agent.tools.database import continue_workflow


assignment_agent = Agent(
    model="gemini-2.5-flash",
    name="assignment_agent",
    description="Routes tickets to appropriate support teams based on classification",
    instruction=prompt.ASSIGNMENT_AGENT_INSTR,
    tools=[
        FunctionTool(func=assign_ticket),
        FunctionTool(func=get_team_workload),
        FunctionTool(func=continue_workflow),
    ],
) 