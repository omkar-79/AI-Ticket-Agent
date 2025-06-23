"""Knowledge Base Agent for searching and retrieving IT support solutions."""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from ai_ticket_agent import prompt
from .tools import search_knowledge_base, continue_workflow


knowledge_agent = Agent(
    model="gemini-2.5-flash",
    name="knowledge_agent",
    description="Uses LLM to search knowledge base for relevant solutions and evaluate their applicability",
    instruction=prompt.KNOWLEDGE_AGENT_INSTR,
    tools=[
        FunctionTool(func=search_knowledge_base),
        FunctionTool(func=continue_workflow),
    ],
) 