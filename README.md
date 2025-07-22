# AI Ticket Agent - Multi-Agent IT Support System

An intelligent multi-agent system built with Google Agent Development Kit (ADK) that provides automated IT support with intelligent routing and escalation.

## 📋 Overview

The AI Ticket Agent system uses LLM-powered agents to:

- **Analyze IT problems** using natural language understanding
- **Route issues** to appropriate human teams via Slack
- **Provide self-service solutions** for common problems
- **Collect user emails** for notifications and tracking
- **Escalate complex issues** to human teams with proper context

## 🤖 Multi-Agent Architecture

| Agent | Role | Capabilities |
|-------|------|--------------|
| 🎯 **Root Agent** | Orchestrates the system | Analyzes problems, routes to sub-agents, collects emails |
| 🛠️ **Self-Service Agent** | Handles common issues | Provides solutions, searches knowledge base, sends notifications |
| ⚠️ **Escalation Agent** | Manages complex issues | Routes to human teams via Slack, sets priorities |

## 🏗️ System Flow

![AI Ticket Agent System Flowchart](images/Flowchart.jpeg)


## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Google Cloud Project (for Gemini API)
- Slack workspace (for team notifications)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd AI-Ticket-Agent
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

3. **Set up environment variables:**
   ```bash
   cp env.example .env
   ```
   
   Configure the following in `.env`:
   ```env
   # Google Cloud Configuration
   GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account.json
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   
   # Slack Configuration
   SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
   SLACK_CHANNEL_ID=C1234567890
   
   # Email Configuration (Optional)
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```

4. **Set up Slack** (see `SLACK_SETUP.md` for detailed instructions):
   - Create Slack app with `chat:write` scope
   - Create team channels
   - Invite bot to channels

5. **Initialize database:**
   ```bash
   python run.py init-db
   ```

## 🎯 Usage

### Running the System

```bash
# Check system status
python run.py status

# Start ADK web interface
python run.py web

# Start ADK CLI interface
python run.py cli

# Run tests
python run.py test

# Initialize database
python run.py init-db

# Start dashboard
python run.py dashboard
```

### Example Interactions

**Self-Service Scenario:**
```
User: "I forgot my password and need to reset it. My email is john@company.com"
System: Routes to Self-Service Agent → Provides password reset steps → Sends email notification
```

**Escalation Scenario:**
```
User: "Our CRM system is completely broken. Users can't log in and we're getting database errors."
System: Routes to Escalation Agent → Analyzes as Software Team issue → Sends to #it-software-support Slack channel
```

## 🧪 Testing

```bash
# Run basic agent tests
python test_agents.py

# Test Slack notifications
python test_slack_notifications.py

# Run all tests
python run.py test
```

## 📋 Team Routing

The system routes issues to these teams:

| Team | Channel | Issues |
|------|---------|--------|
| **Software Team** | `#it-software-support` | Application bugs, CRM/ERP issues, software conflicts |
| **Security Team** | `#it-security-support` | Security incidents, malware, data breaches |
| **Hardware Team** | `#it-hardware-support` | Hardware failures, device issues, physical damage |
| **Network Team** | `#it-network-support` | VPN issues, connectivity problems, firewall issues |
| **Infrastructure Team** | `#it-infrastructure-support` | Server issues, core infrastructure, system outages |
| **Access Management** | `#it-access-support` | Account creation, permissions, user provisioning |
| **General IT Support** | `#it-general-support` | Multiple issues, general troubleshooting |

## 🔔 Slack Notifications

The system sends rich Slack messages with:

- **Priority indicators** (🚨 Critical, ⚠️ High, 📋 Medium, ℹ️ Low)
- **User information** and problem description
- **Team assignment** and next steps
- **AI agent attribution**

## 📧 Email Notifications

Users receive email notifications for:
- **Solution steps** (self-service scenarios)
- **Escalation confirmations** (human team assignment)
- **Status updates** (when available)

## 🗄️ Ticket Lifecycle Tracking

The system now includes comprehensive ticket tracking with database persistence:

### **Database Features:**
- **Complete ticket lifecycle** from creation to resolution
- **Status tracking** with audit trail of all changes
- **Resolution attempts** with user feedback analysis
- **Team assignments** and routing history
- **Search and filtering** capabilities

### **Ticket States:**
- **Open** → **In Progress** → **Resolved** → **Closed**
- **Escalated** (when human team intervention needed)

### **Resolution Tracking:**
- **Self-service attempts** with success/failure tracking
- **User feedback analysis** using LLM-like logic
- **Escalation reasons** and team assignments
- **Complete audit trail** of all interactions

### **Database Commands:**
```bash
# Initialize database
python run.py init-db

# Test ticket lifecycle
python test_ticket_lifecycle.py

# Start Streamlit dashboard
python run.py dashboard
```

## 📊 Streamlit Dashboard

The system includes a comprehensive Streamlit dashboard for real-time ticket monitoring and analytics:

### **Dashboard Features:**
- **📈 Real-time Metrics** - Total, open, resolved, and escalated tickets
- **📊 Interactive Charts** - Status, priority, category, and team distributions
- **🎫 Ticket Management** - Filter, search, and view detailed ticket information
- **📈 Analytics** - Time-based analysis, resolution times, team performance
- **⚙️ Settings** - Database status and system configuration

### **Dashboard Sections:**

#### **Main Dashboard:**
- Key performance metrics
- Status distribution pie chart
- Priority distribution bar chart
- Category and team analysis
- Resolution success rates

#### **Ticket Management:**
- Filter tickets by status, priority, team
- View detailed ticket information
- Track resolution attempts and user feedback
- Complete audit trail

#### **Analytics:**
- Daily ticket volume trends
- Resolution time analysis
- Team performance metrics
- Success rate comparisons

### **Starting the Dashboard:**
```bash
# Using run.py
python run.py dashboard

# Direct Streamlit command
streamlit run dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

## 🛠️ Configuration

### Customizing Team Channels

Edit `ai_ticket_agent/tools/slack_handlers.py`:
```python
team_channel_map = {
    "Software Team": "#your-software-channel",
    "Security Team": "#your-security-channel",
    # ... customize as needed
}
```

### Adding Knowledge Base Content

Edit `ai_ticket_agent/tools/knowledge_base.py` to add common solutions.

## 🚨 Troubleshooting

### Common Issues

**"channel_not_found" error:**
- Create the required Slack channels
- Invite the bot to each channel
- Check channel names in configuration

**"missing_scope" error:**
- Add `chat:write` scope to your Slack app
- Reinstall the app after adding scopes

**Google Cloud authentication:**
- Set up service account credentials
- Ensure `GOOGLE_APPLICATION_CREDENTIALS` points to valid JSON file

## 📁 Project Structure

```
ai_ticket_agent/
├── agent.py              # Root agent orchestrator
├── models.py             # Database models and schemas
├── database.py           # Database connection and management
├── prompt.py             # LLM prompts and instructions
├── tools/                # Agent tools and utilities
│   ├── problem_analyzer.py
│   ├── team_router.py
│   ├── knowledge_base.py
│   ├── resolution_tracker.py
│   ├── ticket_manager.py
│   ├── slack_handlers.py
│   ├── email_collector.py
│   └── notification_sender.py
├── sub_agents/           # Specialized agent implementations
└── __init__.py

# Dashboard and utilities
dashboard.py              # Streamlit dashboard application
init_database.py          # Database initialization script
run.py                    # Main runner script
test_ticket_lifecycle.py  # Ticket lifecycle testing
test_dashboard.py         # Dashboard functionality testing
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

Apache License 2.0 