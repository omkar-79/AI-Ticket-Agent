"""Ticket Assignment Agent for routing tickets to appropriate teams."""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from ai_ticket_agent import prompt
from .tools import assign_ticket, continue_workflow


assignment_agent = Agent(
    model="gemini-2.5-flash",
    name="assignment_agent",
    description="Assigns tickets to appropriate support teams when knowledge base solutions are not available",
    instruction=prompt.ASSIGNMENT_AGENT_INSTR,
    tools=[
        FunctionTool(func=assign_ticket),
        FunctionTool(func=continue_workflow),
    ],
) 