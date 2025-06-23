"""Follow-up Agent for managing ticket follow-ups and customer satisfaction."""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from ai_ticket_agent import prompt
from .tools import schedule_follow_up, send_satisfaction_survey, check_follow_up_due
from ai_ticket_agent.tools.database import continue_workflow


follow_up_agent = Agent(
    model="gemini-2.5-flash",
    name="follow_up_agent",
    description="Manages follow-up actions and customer satisfaction surveys",
    instruction=prompt.FOLLOW_UP_AGENT_INSTR,
    tools=[
        FunctionTool(func=schedule_follow_up),
        FunctionTool(func=send_satisfaction_survey),
        FunctionTool(func=check_follow_up_due),
        FunctionTool(func=continue_workflow),
    ],
) 