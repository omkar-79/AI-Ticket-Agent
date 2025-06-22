"""Ticket Assignment Agent for routing tickets to appropriate teams and agents."""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from ai_ticket_agent import prompt
from .tools import assign_ticket, get_team_workload


assignment_agent = Agent(
    model="gemini-2.5-flash",
    name="assignment_agent",
    description="Routes tickets to appropriate teams and agents based on classification and workload",
    instruction=prompt.ASSIGNMENT_AGENT_INSTR,
    tools=[
        FunctionTool(func=assign_ticket),
        FunctionTool(func=get_team_workload),
    ],
) 