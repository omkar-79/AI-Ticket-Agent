"""Ticket Classification Agent for analyzing and categorizing IT support tickets."""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from ai_ticket_agent import prompt
from .tools import classify_ticket, continue_workflow


classifier_agent = Agent(
    model="gemini-2.5-flash",
    name="classifier_agent",
    description="Uses LLM to analyze incoming IT support tickets and determine category, priority, and keywords",
    instruction=prompt.CLASSIFIER_AGENT_INSTR,
    tools=[
        FunctionTool(func=classify_ticket),
        FunctionTool(func=continue_workflow),
    ],
) 