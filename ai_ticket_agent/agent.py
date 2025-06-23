"""Main agent orchestrator for IT Helpdesk Ticket Management."""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from ai_ticket_agent import prompt
from ai_ticket_agent.sub_agents.classifier.agent import classifier_agent
from ai_ticket_agent.sub_agents.assignment.agent import assignment_agent
from ai_ticket_agent.sub_agents.knowledge.agent import knowledge_agent
from ai_ticket_agent.sub_agents.escalation.agent import escalation_agent
from ai_ticket_agent.sub_agents.sla_tracker.agent import sla_tracker_agent
from ai_ticket_agent.sub_agents.follow_up.agent import follow_up_agent
from ai_ticket_agent.tools.memory import _load_initial_state
from ai_ticket_agent.tools.database import (
    get_current_workflow_status,
    get_workflow_summary,
    create_ticket_and_start_workflow
)


root_agent = Agent(
    model="gemini-2.5-flash",
    name="root_agent",
    description="Autonomous IT Helpdesk Ticket Orchestration System using multiple specialized agents",
    instruction=prompt.ROOT_AGENT_INSTR,
    sub_agents=[
        classifier_agent,
        assignment_agent,
        knowledge_agent,
        escalation_agent,
        sla_tracker_agent,
        follow_up_agent,
    ],
    tools=[
        FunctionTool(func=create_ticket_and_start_workflow),
        FunctionTool(func=get_current_workflow_status),
        FunctionTool(func=get_workflow_summary),
    ],
    before_agent_callback=_load_initial_state,
) 