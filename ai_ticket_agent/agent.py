"""Main agent orchestrator for IT Helpdesk Ticket Management."""

from google.adk.agents import Agent

from ai_ticket_agent import prompt
from ai_ticket_agent.sub_agents.classifier.agent import classifier_agent
from ai_ticket_agent.sub_agents.assignment.agent import assignment_agent
from ai_ticket_agent.sub_agents.knowledge.agent import knowledge_agent
from ai_ticket_agent.sub_agents.escalation.agent import escalation_agent
from ai_ticket_agent.sub_agents.sla_tracker.agent import sla_tracker_agent
from ai_ticket_agent.sub_agents.follow_up.agent import follow_up_agent
from ai_ticket_agent.tools.memory import _load_initial_state


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
    before_agent_callback=_load_initial_state,
) 