"""AI Ticket Agent - Multi-agent IT Support System using Google ADK."""

from .agent import root_agent
from .sub_agents import self_service_agent, escalation_agent

__version__ = "0.1.0"
__all__ = [
    "root_agent",
    "self_service_agent", 
    "escalation_agent"
] 