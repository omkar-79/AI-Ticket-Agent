"""Escalation Agent for managing ticket escalations and routing."""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from ai_ticket_agent import prompt
from .tools import (
    evaluate_escalation_need, 
    get_escalation_criteria,
    run_escalation_monitoring,
    get_tickets_at_risk,
    manual_escalate_ticket
)


escalation_agent = Agent(
    model="gemini-2.5-flash",
    name="escalation_agent",
    description="Evaluates and manages ticket escalations based on SLA breaches and complexity",
    instruction=prompt.ESCALATION_AGENT_INSTR,
    tools=[
        FunctionTool(func=evaluate_escalation_need),
        FunctionTool(func=get_escalation_criteria),
        FunctionTool(func=run_escalation_monitoring),
        FunctionTool(func=get_tickets_at_risk),
        FunctionTool(func=manual_escalate_ticket),
    ],
) 