import os
import imaplib
import email
import re
import uuid
import datetime
import requests
from email.header import decode_header
from pathlib import Path
from dotenv import load_dotenv
import asyncio  # Add this at the top if not present

# ✅ ADK Client imports (needed for direct agent execution)
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai.types import Content, Part

# ✅ Load .env
env_file = Path(".env")
if env_file.exists():
    load_dotenv(dotenv_path=env_file)

IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
EMAIL_ACCOUNT = os.getenv("SUPPORT_EMAIL")
EMAIL_PASSWORD = os.getenv("SUPPORT_EMAIL_PASSWORD")
APP_NAME = "ai_ticket_agent"
USER_ID = "feedback_monitor"

# ✅ Ticket pattern
TICKET_ID_PATTERN = r"TICKET-\d{8}-[A-Z0-9]+"

# === Helper: Extract ID ===
def extract_ticket_id_and_feedback(body, subject):
    ticket_id_match = re.search(TICKET_ID_PATTERN, body) or re.search(TICKET_ID_PATTERN, subject)
    if not ticket_id_match:
        return None, None
    ticket_id = ticket_id_match.group(0)
    return ticket_id, body

# === Helper: Clean Feedback ===
def extract_feedback_content(full_text: str) -> str:
    lines = full_text.split("\n")
    feedback_lines = []
    keywords = ['satisfied', 'not satisfied', 'thank', 'working', 'broken',
                'issue', 'problem', 'fixed', 'resolved', 'great', 'good', 'bad', 'still', 'continue']

    for line in lines:
        line_lower = line.lower().strip()
        if not line_lower:
            continue
        if any(line_lower.startswith(prefix) for prefix in ['>', 'from:', 'to:', 'subject:', 'date:', 'sent:', 'received:', '--', '---']):
            continue
        if any(k in line_lower for k in keywords):
            feedback_lines.append(line.strip())
        elif len(line.strip()) < 50 and '@' not in line:
            feedback_lines.append(line.strip())

    return ' '.join(feedback_lines) if feedback_lines else "User provided feedback"

def send_feedback_to_adk_api(ticket_id: str, feedback_text: str):
    """
    Send feedback payload to the running ADK API server as user input.
    """
    try:
        app_name = "ai_ticket_agent"
        user_id = "feedback_monitor"
        session_id = f"feedback-{ticket_id}"  # Simple session ID based on ticket
        
        # Create explicit feedback message that matches the detection patterns
        feedback_message = f"SYSTEM: This is user feedback for an existing ticket. Process immediately.\n\nTicket ID: {ticket_id}\nFeedback: {feedback_text}"
        
        print(f"📝 Sending feedback message: {feedback_message}")
        
        # Send the message to the ADK API server using the /run endpoint
        run_url = "http://127.0.0.1:8000/run"
        
        payload = {
            "appName": app_name,
            "userId": user_id,
            "sessionId": session_id,
            "newMessage": {
                "role": "user",
                "parts": [
                    {
                        "text": feedback_message
                    }
                ]
            },
            "streaming": False
        }
        
        print(f"📤 Sending to ADK API: {run_url}")
        response = requests.post(run_url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ ADK API Response: {result}")
            
            # Extract the LLM response from the events
            if 'events' in result and result['events']:
                for event in result['events']:
                    if event.get('type') == 'final_response':
                        llm_response = event.get('content', {}).get('parts', [{}])[0].get('text', '')
                        print(f"🤖 LLM Response: {llm_response}")
                        return llm_response
                    elif event.get('type') == 'content':
                        llm_response = event.get('content', {}).get('parts', [{}])[0].get('text', '')
                        print(f"🤖 LLM Response: {llm_response}")
                        return llm_response
            else:
                print("⚠️ No LLM response found in events")
                return result
        else:
            print(f"❌ ADK API Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error sending feedback to ADK API: {e}")
        return None

def send_feedback_direct_to_agent(ticket_id: str, feedback_text: str):
    """
    Send feedback directly to the agent using ADK Runner (alternative to API server).
    """
    try:
        # Import the root agent
        from ai_ticket_agent.agent import root_agent
        
        # Setup ADK session and runner
        session_service = InMemorySessionService()
        runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
        
        # Generate unique session ID
        session_id = f"{ticket_id}-{uuid.uuid4().hex[:6]}"
        
        # Create session synchronously to avoid async issues
        session = session_service.create_session_sync(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)
        
        print(f"📨 Sending to ADK Agent: {ticket_id} → Session {session.id}")
        
        # Create explicit feedback message that matches the detection patterns
        feedback_message = f"SYSTEM: This is user feedback for an existing ticket. Process immediately.\n\nTicket ID: {ticket_id}\nFeedback: {feedback_text}"
        
        print(f"📝 Sending feedback message: {feedback_message}")
        
        # Create proper ADK Message object
        new_message = Content(
            role="user",
            parts=[Part(text=feedback_message)]
        )
        
        # Send message to agent and collect response
        response_text = ""
        try:
            events = runner.run(
                user_id=USER_ID,
                session_id=session.id,
                new_message=new_message
            )
            
            # Process the response with proper null checks
            for event in events:
                if hasattr(event, 'is_final_response') and event.is_final_response():
                    if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
                        if event.content.parts and len(event.content.parts) > 0:
                            # Check if it's a function call or text response
                            part = event.content.parts[0]
                            if hasattr(part, 'text') and part.text:
                                response_text = part.text
                                print(f"🤖 Agent Response: {response_text}")
                                return response_text
                            elif hasattr(part, 'function_call'):
                                # Handle function call response
                                func_name = part.function_call.name if hasattr(part.function_call, 'name') else 'unknown'
                                print(f"🤖 Agent executed function: {func_name}")
                                return f"Function executed: {func_name}"
                        else:
                            print("⚠️ Event has no content or parts")
                            continue
                    else:
                        print("⚠️ Event has no content or parts")
                        continue
                elif hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
                    if event.content.parts and len(event.content.parts) > 0:
                        part = event.content.parts[0]
                        if hasattr(part, 'text') and part.text:
                            response_text = part.text
                            print(f"🤖 Agent Response (non-final): {response_text}")
                        elif hasattr(part, 'function_call'):
                            func_name = part.function_call.name if hasattr(part.function_call, 'name') else 'unknown'
                            print(f"🤖 Agent executed function (non-final): {func_name}")
                            response_text = f"Function executed: {func_name}"
            
            # Check for function response events
            if hasattr(event, 'function_response'):
                func_name = event.function_response.name if hasattr(event.function_response, 'name') else 'unknown'
                print(f"🤖 Function response received: {func_name}")
                response_text = f"Function completed: {func_name}"
            
            if response_text:
                return response_text
            else:
                print("⚠️ No response text found in events")
                return "No response received"
                
        except Exception as run_error:
            print(f"❌ Error during runner.run: {run_error}")
            return f"Error during execution: {run_error}"
        
    except Exception as e:
        print(f"❌ Error sending feedback directly to agent: {e}")
        return None

def send_feedback_simple_agent_call(ticket_id: str, feedback_text: str):
    """
    Send feedback using a simple direct agent call without ADK Runner.
    """
    try:
        # Import the root agent
        from ai_ticket_agent.agent import root_agent
        from google.adk.sessions import InMemorySessionService
        from google.adk.runners import Runner
        from google.genai.types import Content, Part
        
        # Create explicit feedback message
        feedback_message = f"SYSTEM: This is user feedback for an existing ticket. Process immediately.\n\nTicket ID: {ticket_id}\nFeedback: {feedback_text}"
        
        print(f"📝 Sending feedback message: {feedback_message}")
        
        # Setup ADK session and runner
        session_service = InMemorySessionService()
        runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
        
        # Generate unique session ID
        session_id = f"feedback-{ticket_id}-{uuid.uuid4().hex[:6]}"
        
        # Create session synchronously
        session = session_service.create_session_sync(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)
        
        print(f"🤖 Calling agent directly for ticket: {ticket_id}")
        
        # Create proper ADK Message object
        new_message = Content(
            role="user",
            parts=[Part(text=feedback_message)]
        )
        
        # Send message to agent and collect response
        response_text = ""
        try:
            events = runner.run(
                user_id=USER_ID,
                session_id=session.id,
                new_message=new_message
            )
            
            # Process the response with proper null checks
            for event in events:
                if hasattr(event, 'is_final_response') and event.is_final_response():
                    if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
                        if event.content.parts and len(event.content.parts) > 0:
                            # Check if it's a function call or text response
                            part = event.content.parts[0]
                            if hasattr(part, 'text') and part.text:
                                response_text = part.text
                                print(f"🤖 Agent Response: {response_text}")
                                return response_text
                            elif hasattr(part, 'function_call'):
                                # Handle function call response
                                func_name = part.function_call.name if hasattr(part.function_call, 'name') else 'unknown'
                                print(f"🤖 Agent executed function: {func_name}")
                                return f"Function executed: {func_name}"
                        else:
                            print("⚠️ Event has no content or parts")
                            continue
                    else:
                        print("⚠️ Event has no content or parts")
                        continue
                elif hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
                    if event.content.parts and len(event.content.parts) > 0:
                        part = event.content.parts[0]
                        if hasattr(part, 'text') and part.text:
                            response_text = part.text
                            print(f"🤖 Agent Response (non-final): {response_text}")
                        elif hasattr(part, 'function_call'):
                            func_name = part.function_call.name if hasattr(part.function_call, 'name') else 'unknown'
                            print(f"🤖 Agent executed function (non-final): {func_name}")
                            response_text = f"Function executed: {func_name}"
                
                # Check for function response events
                if hasattr(event, 'function_response'):
                    func_name = event.function_response.name if hasattr(event.function_response, 'name') else 'unknown'
                    print(f"🤖 Function response received: {func_name}")
                    response_text = f"Function completed: {func_name}"
            
            if response_text:
                return response_text
            else:
                print("⚠️ No response text found in events")
                return "No response received"
                
        except Exception as run_error:
            print(f"❌ Error during runner.run: {run_error}")
            return f"Error during execution: {run_error}"
        
    except Exception as e:
        print(f"❌ Error in simple agent call: {e}")
        return None

# === 🧩 Main: Gmail + ADK (API Server or Direct) ===
def check_feedback_emails(use_api_server=True):
    """
    Monitor Gmail for feedback emails and send to ADK.
    
    Args:
        use_api_server (bool): If True, use ADK API server. If False, use direct agent execution.
    """
    if not EMAIL_ACCOUNT or not EMAIL_PASSWORD:
        print("❌ Email credentials missing.")
        return

    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select("inbox")

        today = datetime.date.today().strftime("%d-%b-%Y")
        status, messages = mail.search(None, f'(UNSEEN SINCE {today} SUBJECT "Resolution for your IT Support Ticket")')

        if status != "OK":
            print("📭 No new emails found.")
            return

        feedback_count = 0
        for num in messages[0].split():
            status, data = mail.fetch(num, '(RFC822)')
            msg = email.message_from_bytes(data[0][1])

            subject, encoding = decode_header(msg["Subject"])[0]
            subject = subject.decode(encoding or "utf-8") if isinstance(subject, bytes) else subject
            from_ = msg.get("From")

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain" and not part.get("Content-Disposition"):
                        body = part.get_payload(decode=True).decode(errors="ignore")
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors="ignore")

            print(f"📧 Found email from {from_} — Subject: {subject}")

            ticket_id, feedback_text = extract_ticket_id_and_feedback(body, subject)
            if ticket_id and feedback_text:
                feedback_content = extract_feedback_content(feedback_text)
                print(f"📨 Processing feedback for ticket: {ticket_id}")
                print(f"📝 Feedback content: {feedback_content}")
                
                # Try simple agent call first, then fallback to other methods
                result = send_feedback_simple_agent_call(ticket_id, feedback_content)
                
                if not result:
                    # Fallback to other methods
                    if use_api_server:
                        result = send_feedback_to_adk_api(ticket_id, feedback_content)
                    else:
                        result = send_feedback_direct_to_agent(ticket_id, feedback_content)
                
                if result:
                    print(f"✅ Successfully processed feedback for {ticket_id}")
                else:
                    print(f"❌ Failed to process feedback for {ticket_id}")
                
                feedback_count += 1
            else:
                print(f"⚠️ No ticket ID or feedback found for email from {from_}")

            mail.store(num, '+FLAGS', '\\Seen')

        mail.logout()
        print(f"✅ Processed {feedback_count} emails.")

    except Exception as e:
        print(f"❌ Error: {e}")

# === Run ===
if __name__ == "__main__":
    print("📬 Monitoring Gmail & forwarding to ADK...")
    
    # Choose your method:
    # True = Use ADK API Server (requires: adk api_server --port 8000)
    # False = Use Direct Agent Execution (no API server needed)
    USE_API_SERVER = False  # Changed to False to bypass API server issues
    
    if USE_API_SERVER:
        print("🔗 Using ADK API Server mode")
        check_feedback_emails(use_api_server=True)
    else:
        print("🤖 Using Direct Agent Execution mode")
        check_feedback_emails(use_api_server=False)
