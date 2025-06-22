"""Ticket Classification Agent for analyzing and categorizing IT support tickets."""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from ai_ticket_agent import prompt
from .tools import classify_ticket, extract_priority_indicators


classifier_agent = Agent(
    model="gemini-2.5-flash",
    name="classifier_agent",
    description="Analyzes incoming IT support tickets to determine category, priority, and urgency",
    instruction=prompt.CLASSIFIER_AGENT_INSTR,
    tools=[
        FunctionTool(func=classify_ticket),
        FunctionTool(func=extract_priority_indicators),
    ],
) 