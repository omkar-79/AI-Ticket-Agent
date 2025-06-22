# Autonomous IT Helpdesk Ticket Orchestration

An intelligent multi-agent system built with Google Agent Development Kit (ADK) that autonomously handles IT helpdesk tickets from classification to resolution.

## 📋 Problem Statement

In large organizations, IT helpdesks face significant challenges:

- **Hundreds of tickets** flow in daily (IT issues, access requests, software bugs)
- **Tier 1 staff** spend excessive time reading, routing, and responding to common requests
- **High-priority tickets** sometimes get lost, misrouted, or delayed
- **Manual processes** lead to inconsistent responses and SLA breaches

## 🤖 Agent-Based Solution with ADK

Our ADK multi-agent system provides intelligent automation:

| Agent | Role | Capabilities |
|-------|------|--------------|
| 🎯 **Ticket Classifier Agent** | Analyzes incoming tickets | Uses LLM to detect issue type & urgency |
| 📋 **Assignment Agent** | Routes tickets to appropriate teams | Maps tickets to hardware, network, access, software queues |
| 📚 **Knowledge Agent** | Provides instant solutions | Searches knowledge base & drafts auto-responses for FAQs |
| ⚠️ **Escalation Agent** | Manages critical issues | Flags tickets needing human review (security, complex issues) |
| ⏰ **SLA Tracker Agent** | Monitors compliance | Tracks open tickets & alerts on SLA breaches |
| 📞 **Follow-Up Agent** | Ensures satisfaction | Checks user satisfaction & collects feedback |

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Ticket Input  │───▶│  Classifier     │───▶│   Assignment    │
│   (Email/Chat)  │    │   Agent         │    │    Agent        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Follow-Up     │◀───│   SLA Tracker   │◀───│   Escalation    │
│    Agent        │    │    Agent        │    │    Agent        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                ▲                       ▲
                                │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Knowledge     │───▶│   Resolution    │───▶│   Team Queues   │
│    Agent        │    │   Workflow      │    │   (Hardware,    │
└─────────────────┘    └─────────────────┘    │   Network, etc) │
                                              └─────────────────┘
```

## 🚀 Example Workflow

### 1. Ticket Reception
**User Email:** *"My VPN keeps disconnecting every 30 minutes"*

### 2. Classification
**Classifier Agent:** Detects "VPN connectivity issue", medium urgency, high frequency

### 3. Assignment
**Assignment Agent:** Routes to "Network Support" queue

### 4. Knowledge Search
**Knowledge Agent:** Finds VPN troubleshooting guide, drafts response with steps

### 5. Escalation Check
**Escalation Agent:** Monitors for unresolved issues, escalates if needed

### 6. SLA Monitoring
**SLA Tracker Agent:** Ensures resolution within 4-hour SLA window

### 7. Follow-Up
**Follow-Up Agent:** Checks satisfaction after resolution

## 🛠️ Setup and Installation

### Prerequisites

- Python 3.11+
- Google Cloud Project (for Vertex AI integration)
- PostgreSQL database
- Redis (for Celery task queue)
- Google Agent Development Kit 1.0+

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
   cp .env.example .env
   ```
   
   Configure the following in `.env`:
   ```env
   # Google Cloud Configuration
   GOOGLE_GENAI_USE_VERTEXAI=1
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   
   # Database Configuration
   DATABASE_URL=postgresql://user:password@localhost/helpdesk_db
   
   # Redis Configuration
   REDIS_URL=redis://localhost:6379/0
   
   # API Configuration
   API_KEY=your-api-key
   ```

4. **Set up database:**
   ```bash
   alembic upgrade head
   ```

5. **Start the services:**
   ```bash
   # Start Redis
   redis-server
   
   # Start Celery worker
   celery -A ai_ticket_agent.celery_app worker --loglevel=info
   
   # Start the API server
   uvicorn ai_ticket_agent.main:app --reload
   ```

## 🎯 Usage

### Running the Agent

```bash
# Using ADK CLI
adk run ai_ticket_agent

# Using web interface
adk web
```

### API Endpoints

- `POST /tickets` - Submit new ticket
- `GET /tickets/{ticket_id}` - Get ticket status
- `GET /tickets` - List all tickets
- `PUT /tickets/{ticket_id}` - Update ticket
- `DELETE /tickets/{ticket_id}` - Close ticket

### Example API Usage

```python
import requests

# Submit a new ticket
ticket_data = {
    "subject": "VPN Connection Issues",
    "description": "My VPN keeps disconnecting every 30 minutes",
    "priority": "medium",
    "category": "network",
    "user_email": "user@company.com"
}

response = requests.post("http://localhost:8000/tickets", json=ticket_data)
ticket_id = response.json()["ticket_id"]

# Check ticket status
status = requests.get(f"http://localhost:8000/tickets/{ticket_id}")
print(status.json())
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run with coverage
pytest --cov=ai_ticket_agent
```

## 🚀 Deployment

### Local Development
```bash
poetry install --with dev
adk web
```

### Production Deployment
```bash
# Deploy to Vertex AI Agent Engine
poetry install --with deployment
python deployment/deploy.py --create
```

## 📊 Features

### Core Capabilities
- **Intelligent Classification**: LLM-powered ticket categorization
- **Smart Routing**: Automatic assignment to appropriate teams
- **Knowledge Integration**: Instant FAQ responses and solutions
- **SLA Management**: Automated monitoring and alerts
- **Escalation Handling**: Human-in-the-loop for complex issues
- **Satisfaction Tracking**: Post-resolution feedback collection

### Integration Support
- **Email Integration**: SMTP/IMAP for email ticket processing
- **Chat Integration**: Slack, Teams, Discord webhooks
- **Ticketing Systems**: Jira, ServiceNow, Zendesk APIs
- **Knowledge Bases**: Confluence, Notion, custom databases
- **Monitoring**: Prometheus, Grafana metrics

### Advanced Features
- **Multi-language Support**: Global ticket processing
- **Priority Learning**: ML-based priority adjustment
- **Predictive Analytics**: Ticket volume forecasting
- **Automated Reporting**: Daily/weekly performance reports
- **Custom Workflows**: Configurable business rules

## 🔧 Configuration

### Agent Configuration
Each agent can be configured via environment variables or configuration files:

```yaml
# config/agents.yaml
classifier_agent:
  model: "gemini-2.5-flash"
  confidence_threshold: 0.8
  max_tokens: 1000

assignment_agent:
  routing_rules:
    - category: "hardware"
      team: "hardware-support"
    - category: "network"
      team: "network-support"
```

### SLA Configuration
```yaml
# config/sla.yaml
sla_rules:
  critical:
    response_time: "1 hour"
    resolution_time: "4 hours"
  high:
    response_time: "2 hours"
    resolution_time: "8 hours"
  medium:
    response_time: "4 hours"
    resolution_time: "24 hours"
  low:
    response_time: "8 hours"
    resolution_time: "72 hours"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the [documentation](docs/)
- Join our [Discord community](https://discord.gg/ai-ticket-agent)

## 🗺️ Roadmap

- [ ] Advanced ML models for ticket classification
- [ ] Voice-to-text ticket submission
- [ ] Mobile app for ticket tracking
- [ ] Integration with more ticketing platforms
- [ ] Advanced analytics dashboard
- [ ] Multi-tenant support
- [ ] AI-powered ticket resolution suggestions 