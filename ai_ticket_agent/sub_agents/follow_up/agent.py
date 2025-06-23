"""Follow-up Agent for managing ticket follow-ups and customer satisfaction."""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from ai_ticket_agent import prompt
from .tools import build_feedback_prompt, store_feedback_memory, get_feedback_history
from ai_ticket_agent.tools.database import get_ticket, update_ticket_fields, get_step_data, set_step_data
from ai_ticket_agent.tools.notifications import send_slack_notification
from ai_ticket_agent.tools.database import get_ticket
from ai_ticket_agent.tools.notifications import send_email_notification
import os
import json


def process_feedback_tool(ticket_id: str, user_feedback: str) -> str:
    """
    Process user feedback using LLM sentiment analysis and take action (close or reopen ticket).
    This tool uses LLM to analyze feedback sentiment and updates the ticket status accordingly.
    """
    try:
        # Get the ticket to check if it exists
        ticket = get_ticket(ticket_id)
        if not ticket:
            return f"❌ Ticket {ticket_id} not found."
        
        # Check if this feedback was already processed to prevent infinite loops
        feedback_data = get_step_data(ticket_id, "FEEDBACK_PROCESSING")
        if feedback_data and feedback_data.get("processed_feedback") == user_feedback:
            return f"✅ Feedback for ticket {ticket_id} was already processed."
        
        # Use LLM for sentiment analysis
        sentiment_result = analyze_feedback_sentiment(user_feedback)
        
        # Extract decision from LLM analysis
        decision = sentiment_result.get("decision", "reopen")  # Default to reopen for safety
        confidence = sentiment_result.get("confidence", 0.0)
        reasoning = sentiment_result.get("reasoning", "No reasoning provided")
        
        print(f"🤖 LLM Sentiment Analysis: {decision} (confidence: {confidence:.2f})")
        print(f"🤖 Reasoning: {reasoning}")
        
        slack_channel = os.getenv("SLACK_CHANNEL_ID")
        
        if decision == "close":
            update_ticket_fields(ticket_id, {"status": "closed"}, "follow_up_agent")
            print(f"✅ Ticket {ticket_id} closed after LLM feedback analysis.")
            # Notify Slack
            if slack_channel:
                message = f"✅ Ticket `{ticket_id}` has been closed by the user (LLM analysis: satisfied, confidence: {confidence:.2f})."
                send_slack_notification(slack_channel, message)
            
            # Mark feedback as processed
            set_step_data(ticket_id, "FEEDBACK_PROCESSING", {
                "processed_feedback": user_feedback,
                "decision": decision,
                "confidence": confidence,
                "reasoning": reasoning
            })
            
            return f"✅ Ticket {ticket_id} closed successfully. LLM analysis indicated satisfaction (confidence: {confidence:.2f})."
        else:
            # Reopen and assign to the original team
            update_ticket_fields(ticket_id, {"status": "in_progress", "assigned_team": ticket.assigned_team}, "follow_up_agent")
            print(f"🔄 Ticket {ticket_id} reopened and assigned to {ticket.assigned_team} after LLM feedback analysis.")
            # Notify Slack
            if slack_channel:
                message = f"🔄 Ticket `{ticket_id}` has been reopened by the user (LLM analysis: not satisfied, confidence: {confidence:.2f}). Assigned back to {ticket.assigned_team}."
                send_slack_notification(slack_channel, message)
            
            # Mark feedback as processed
            set_step_data(ticket_id, "FEEDBACK_PROCESSING", {
                "processed_feedback": user_feedback,
                "decision": decision,
                "confidence": confidence,
                "reasoning": reasoning
            })
            
            return f"🔄 Ticket {ticket_id} reopened and assigned back to {ticket.assigned_team}. LLM analysis indicated dissatisfaction (confidence: {confidence:.2f})."
            
    except Exception as e:
        print(f"❌ Error processing feedback: {e}")
        return f"❌ Error processing feedback for ticket {ticket_id}: {e}"


def analyze_feedback_sentiment(feedback_text: str) -> dict:
    """
    Use simple sentiment analysis to determine if ticket should be closed or reopened.
    This avoids recursive agent calls and uses direct analysis.
    """
    try:
        print(f"🤖 Analyzing feedback sentiment: '{feedback_text}'")
        
        # Use a simple but effective sentiment analysis approach
        feedback_lower = feedback_text.lower().strip()
        
        # Define sentiment patterns with confidence scores
        positive_patterns = [
            ("thank", 0.9, "User expressed gratitude"),
            ("thanks", 0.9, "User expressed gratitude"),
            ("great", 0.85, "User expressed positive sentiment"),
            ("good", 0.8, "User expressed satisfaction"),
            ("excellent", 0.95, "User expressed high satisfaction"),
            ("perfect", 0.95, "User expressed perfect satisfaction"),
            ("awesome", 0.9, "User expressed enthusiasm"),
            ("satisfied", 0.9, "User explicitly stated satisfaction"),
            ("happy", 0.85, "User expressed happiness"),
            ("resolved", 0.8, "User indicated issue is resolved"),
            ("fixed", 0.8, "User indicated issue is fixed"),
            ("working", 0.8, "User indicated solution is working"),
            ("solved", 0.8, "User indicated problem is solved")
        ]
        
        negative_patterns = [
            ("not satisfied", 0.95, "User explicitly stated dissatisfaction"),
            ("unsatisfied", 0.9, "User explicitly stated dissatisfaction"),
            ("not working", 0.9, "User indicated solution is not working"),
            ("still broken", 0.9, "User indicated issue persists"),
            ("issue persists", 0.9, "User indicated problem continues"),
            ("not resolved", 0.9, "User indicated issue is not resolved"),
            ("not fixed", 0.9, "User indicated issue is not fixed"),
            ("not good", 0.8, "User expressed dissatisfaction"),
            ("not great", 0.8, "User expressed dissatisfaction"),
            ("not happy", 0.85, "User expressed unhappiness"),
            ("dissatisfied", 0.9, "User explicitly stated dissatisfaction"),
            ("disappointed", 0.85, "User expressed disappointment"),
            ("broken", 0.7, "User indicated something is broken"),
            ("problem", 0.7, "User indicated there is still a problem"),
            ("issue", 0.6, "User mentioned an issue")
        ]
        
        # Check for negative patterns first (higher priority)
        for pattern, confidence, reasoning in negative_patterns:
            if pattern in feedback_lower:
                result = {
                    "decision": "reopen",
                    "confidence": confidence,
                    "reasoning": reasoning
                }
                print(f"🤖 Negative pattern detected: '{pattern}' → {result}")
                return result
        
        # Check for positive patterns
        for pattern, confidence, reasoning in positive_patterns:
            if pattern in feedback_lower:
                result = {
                    "decision": "close",
                    "confidence": confidence,
                    "reasoning": reasoning
                }
                print(f"🤖 Positive pattern detected: '{pattern}' → {result}")
                return result
        
        # If no clear patterns found, analyze the overall sentiment
        # Count positive and negative words
        positive_words = ["thank", "great", "good", "excellent", "perfect", "awesome", "satisfied", "happy", "resolved", "fixed", "working", "solved"]
        negative_words = ["not", "broken", "problem", "issue", "bad", "terrible", "awful", "horrible", "disappointed", "dissatisfied", "unsatisfied"]
        
        positive_count = sum(1 for word in positive_words if word in feedback_lower)
        negative_count = sum(1 for word in negative_words if word in feedback_lower)
        
        if positive_count > negative_count:
            result = {
                "decision": "close",
                "confidence": 0.6,
                "reasoning": f"Overall positive sentiment detected (positive words: {positive_count}, negative words: {negative_count})"
            }
        elif negative_count > positive_count:
            result = {
                "decision": "reopen",
                "confidence": 0.6,
                "reasoning": f"Overall negative sentiment detected (positive words: {positive_count}, negative words: {negative_count})"
            }
        else:
            # Ambiguous feedback - default to reopen for safety
            result = {
                "decision": "reopen",
                "confidence": 0.5,
                "reasoning": f"Ambiguous feedback, defaulting to reopen for safety: '{feedback_text}'"
            }
        
        print(f"🤖 Sentiment analysis result: {result}")
        return result
            
    except Exception as e:
        print(f"❌ Error in sentiment analysis: {e}")
        return fallback_sentiment_analysis(feedback_text)


def fallback_sentiment_analysis(feedback_text: str) -> dict:
    """
    Fallback sentiment analysis using simple keyword matching.
    """
    feedback_lower = feedback_text.lower()
    
    # Check for negative feedback FIRST (before positive feedback)
    negative_phrases = [
        "not satisfied", "unsatisfied", "not working", "still broken", 
        "issue persists", "not resolved", "not fixed", "not good", 
        "not great", "not happy", "dissatisfied", "disappointed"
    ]
    positive_phrases = [
        "satisfied", "thank", "great", "good", "resolved", "fixed", 
        "working", "happy", "excellent", "perfect", "awesome"
    ]
    
    # Check for negative feedback first
    if any(phrase in feedback_lower for phrase in negative_phrases):
        return {
            "decision": "reopen",
            "confidence": 0.8,
            "reasoning": f"Fallback analysis detected negative phrases in: {feedback_text}"
        }
    elif any(phrase in feedback_lower for phrase in positive_phrases):
        return {
            "decision": "close",
            "confidence": 0.7,
            "reasoning": f"Fallback analysis detected positive phrases in: {feedback_text}"
        }
    else:
        return {
            "decision": "reopen",
            "confidence": 0.5,
            "reasoning": f"Fallback analysis: ambiguous feedback, defaulting to reopen: {feedback_text}"
        }


follow_up_agent = Agent(
    model="gemini-2.5-flash",
    name="follow_up_agent",
    description="Manages follow-up actions and customer satisfaction surveys",
    instruction=prompt.FOLLOW_UP_AGENT_INSTR,
    tools=[
        FunctionTool(func=process_feedback_tool),
        FunctionTool(func=store_feedback_memory),
        FunctionTool(func=get_feedback_history),
    ],
)

def send_resolution_and_request_feedback(ticket_id: str) -> bool:
    """
    Send the resolution notes to the user and ask for feedback.
    """
    ticket = get_ticket(ticket_id)
    if not ticket:
        print(f"❌ Ticket {ticket_id} not found.")
        return False
    if not ticket.user_email:
        print(f"❌ No user email for ticket {ticket_id}.")
        return False
    if not ticket.resolution_notes:
        print(f"❌ No resolution notes for ticket {ticket_id}.")
        return False

    subject = f"Resolution for your IT Support Ticket {ticket.id}"
    body = f"""
Hello,

Your ticket has been marked as resolved. Here is the solution provided by our support team:

---
{ticket.resolution_notes}
---

Are you satisfied with this resolution?
- Reply to this email with 'satisfied' to close the ticket.
- Reply with 'not satisfied' to reopen the ticket and continue working with our team.

Thank you!
"""
    
    print(f"📧 Sending resolution and feedback request to {ticket.user_email}")
    return send_email_notification(
        to_email=ticket.user_email,
        subject=subject,
        body=body
    )

