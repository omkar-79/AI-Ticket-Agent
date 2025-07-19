"""Problem analyzer tool that provides context for LLM-based problem classification."""

from google.adk.tools import ToolContext
from typing import Dict, Any


def analyze_problem(problem_description: str, tool_context: ToolContext) -> str:
    """
    Provide context and guidance for LLM-based problem analysis.
    
    Args:
        problem_description: The user's IT problem description
        tool_context: The ADK tool context
        
    Returns:
        Context and guidance for the LLM to analyze the problem
    """
    
    return f"""
    **Problem Analysis Context:**
    
    Problem Description: {problem_description}
    
    **Analysis Guidelines for LLM:**
    
    Consider the following factors when analyzing this IT problem:
    
    1. **Complexity Assessment:**
       - LOW: Common issues with known solutions (password resets, basic troubleshooting, software installation)
       - MEDIUM: Issues that may require some investigation but are generally resolvable
       - HIGH: Complex technical issues, security incidents, hardware failures, system outages
    
    2. **Self-Service Candidates:**
       - Password resets and account unlocks
       - VPN connectivity problems
       - Email configuration and troubleshooting
       - Software installation and updates
       - Basic network connectivity issues
       - Printer setup and configuration
       - Browser and application issues
       - Mobile device setup
    
    3. **Escalation Required:**
       - Security incidents, breaches, malware
       - Hardware failures and physical damage
       - System outages and critical failures
       - Data loss or corruption
       - Access violations
       - Complex technical issues requiring specialized expertise
    
    4. **Routing Decision:**
       - If the problem is common and has known solutions → SELF_SERVICE
       - If the problem is complex, urgent, or requires specialized expertise → ESCALATION
       - If uncertain, start with SELF_SERVICE and escalate if needed
    
    **Your Task:** Analyze the problem above and provide your recommendation with reasoning.
    """


# The tool is just the function itself
problem_analyzer_tool = analyze_problem 