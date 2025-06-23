#!/usr/bin/env python3
"""
Flask app for handling Slack interactive events.
"""

from flask import Flask, request, jsonify, make_response
import os
import json
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

# Import the Slack handler
from ai_ticket_agent.tools.slack_handlers import handle_slack_interaction

app = Flask(__name__)

@app.route("/slack/interactivity", methods=["POST"])
def slack_interactivity():
    """
    Handle Slack interactive events (button clicks, etc.)
    """
    try:
        print("DEBUG: Received Slack interaction request")
        print(f"DEBUG: Request method: {request.method}")
        print(f"DEBUG: Request headers: {dict(request.headers)}")
        
        # Slack sends payload as form data
        payload = request.form.get("payload")
        if not payload:
            print("DEBUG: No payload found in request")
            return make_response("No payload", 400)
        
        print(f"DEBUG: Raw payload: {payload}")
        
        # Parse the JSON payload
        try:
            payload_data = json.loads(payload)
            print(f"DEBUG: Parsed payload: {json.dumps(payload_data, indent=2)}")
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON decode error: {e}")
            return make_response("Invalid JSON payload", 400)
        
        # Route to the appropriate handler based on interaction type
        interaction_type = payload_data.get("type")
        
        if interaction_type == "block_actions":
            # Handle button clicks
            result = handle_slack_interaction(payload_data)
        elif interaction_type == "view_submission":
            # Handle modal submissions
            result = handle_slack_interaction(payload_data)
        else:
            result = {"error": f"Unsupported interaction type: {interaction_type}"}
            
        print(f"DEBUG: Handler result: {result}")
        
        # Acknowledge modal submissions immediately
        if interaction_type == "view_submission":
            if "error" in result:
                return jsonify({
                    "response_action": "errors",
                    "errors": {"resolution_notes": result["error"]}
                })
            else:
                return make_response("", 200) # Empty 200 response to close the modal
        
        # Respond to button clicks
        if "error" in result:
            response_text = f"❌ Error: {result['error']}"
        elif "message" in result:
            response_text = result["message"]
        else:
            response_text = "✅ Action processed successfully."
        
        print(f"DEBUG: Sending response: {response_text}")
        return jsonify({"text": response_text})
        
    except Exception as e:
        print(f"DEBUG: Exception in slack_interactivity: {e}")
        import traceback
        traceback.print_exc()
        return make_response(f"Internal server error: {str(e)}", 500)

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "slack-interactivity"})

@app.route("/", methods=["GET"])
def root():
    """Root endpoint."""
    return jsonify({
        "service": "Slack Interactivity Handler",
        "endpoints": {
            "/slack/interactivity": "Handle Slack button clicks and interactions",
            "/health": "Health check"
        }
    })

if __name__ == "__main__":
    # Load environment variables
    env_file = Path(".env")
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv()
    
    print("🚀 Starting Slack Interactivity Flask App...")
    print(f"📡 Server will be available at: http://localhost:5001")
    print(f"🔗 Slack endpoint: http://localhost:5001/slack/interactivity")
    print(f"💚 Health check: http://localhost:5001/health")
    
    # Check required environment variables
    required_vars = ["SLACK_BOT_TOKEN", "SLACK_CHANNEL_ID"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️  Warning: Missing environment variables: {missing_vars}")
        print("   Some features may not work correctly.")
    
    app.run(host="0.0.0.0", port=5001, debug=True) 