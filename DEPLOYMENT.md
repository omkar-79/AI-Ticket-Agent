# AI Ticket Agent - Deployment Guide

This guide covers deploying the AI Ticket Agent system with all its components.

## 🏗️ System Architecture

The AI Ticket Agent consists of multiple services:

- **ADK API Server** (Port 8000) - Main agent API for ticket processing
- **ADK Web Interface** (Port 8080) - Web UI for ticket creation (run separately with `adk web`)
- **Slack App** (Port 5001) - Handle Slack button interactions
- **Email Feedback Monitor** - Background process for email feedback
- **Database** - SQLite file (`helpdesk.db`)

## 📋 Prerequisites

### 1. Environment Setup
```bash
# Copy environment template
cp env.example .env

# Edit .env with your configuration
nano .env
```

### 2. Required Environment Variables
```bash
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_CHANNEL_ID=C0123456789

# Email Configuration
SUPPORT_EMAIL=your-support@company.com
SUPPORT_EMAIL_PASSWORD=your-app-password

# Database (optional, defaults to SQLite)
DATABASE_URL=sqlite:///helpdesk.db
```

### 3. Install Dependencies
```bash
# Install Python dependencies
poetry install

# Or with pip
pip install -r requirements.txt
```

## 🚀 Deployment Options

### Option 1: Local Development (Recommended for testing)

Use the deployment script for easy management:

```bash
# Check system requirements
python deploy.py check

# Start all services
python deploy.py start

# Check status
python deploy.py status

# Start individual services
python deploy.py api      # ADK API Server only
python deploy.py slack    # Slack App only
python deploy.py email    # Email Monitor only
```

### Option 2: Docker Compose (Recommended for production)

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Start with production profile (includes Nginx)
docker-compose --profile production up -d
```

### Option 3: Manual Service Management

#### Start ADK API Server
```bash
python -m uvicorn ai_ticket_agent.main:app --host 0.0.0.0 --port 8000
```

#### Start Slack App
```bash
python slack_app.py
```

#### Start Email Monitor
```bash
python ai_ticket_agent/tools/email_feedback_reader.py
```

#### Start ADK Web Interface (separate terminal)
```bash
adk web
```

## 🔧 Service Configuration

### Port Configuration
- **8000**: ADK API Server (main agent API)
- **5001**: Slack App (interactions)
- **8080**: ADK Web Interface (ticket creation UI)
- **80/443**: Nginx (production reverse proxy)

### Database Configuration
The system uses SQLite by default. For production, consider:
- PostgreSQL
- MySQL
- Cloud SQL

Update `DATABASE_URL` in `.env` for different databases.

### Slack Configuration
1. Create a Slack app at https://api.slack.com/apps
2. Add bot token to `.env`
3. Configure interactive endpoints:
   - Request URL: `https://yourdomain.com/slack/interactivity`
   - Add required scopes: `chat:write`, `channels:read`

### Email Configuration
1. Enable IMAP in your email provider
2. Use app-specific passwords for security
3. Configure email monitoring in `.env`

## 📊 Monitoring & Health Checks

### Health Check Endpoints
- API Server: `http://localhost:8000/health`
- Slack App: `http://localhost:5001/health`

### Logs
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f api-server
docker-compose logs -f slack-app
docker-compose logs -f email-monitor
```

### Database Monitoring
```bash
# Check database size
ls -lh helpdesk.db

# Backup database
cp helpdesk.db helpdesk.db.backup.$(date +%Y%m%d)
```

## 🔒 Security Considerations

### Production Security
1. **Use HTTPS**: Configure SSL certificates
2. **Environment Variables**: Never commit `.env` files
3. **Database Security**: Use strong passwords and encrypted connections
4. **Rate Limiting**: Configure Nginx rate limits
5. **Firewall**: Restrict access to necessary ports only

### SSL Configuration
```bash
# Generate SSL certificates (Let's Encrypt)
certbot certonly --standalone -d api.yourdomain.com
certbot certonly --standalone -d slack.yourdomain.com

# Copy certificates to nginx/ssl/
cp /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem nginx/ssl/cert.pem
cp /etc/letsencrypt/live/api.yourdomain.com/privkey.pem nginx/ssl/key.pem
```

## 🚨 Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check dependencies
python deploy.py check

# Check logs
docker-compose logs [service-name]

# Check port conflicts
netstat -tulpn | grep :8000
```

#### Database Issues
```bash
# Check database file
ls -la helpdesk.db

# Reset database (WARNING: loses all data)
rm helpdesk.db
python -c "from ai_ticket_agent.tools.database import init_db; init_db()"
```

#### Slack Integration Issues
1. Verify bot token in `.env`
2. Check Slack app configuration
3. Verify request URL in Slack app settings
4. Check Slack app logs

#### Email Monitor Issues
1. Verify email credentials in `.env`
2. Check IMAP settings
3. Verify app-specific password
4. Check email monitor logs

### Performance Optimization

#### Database Optimization
```sql
-- Add indexes for better performance
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_created_at ON tickets(created_at);
CREATE INDEX idx_workflow_ticket_id ON workflow_states(ticket_id);
```

#### Memory Optimization
- Monitor memory usage with `docker stats`
- Adjust container memory limits in `docker-compose.yml`
- Consider using Redis for caching

## 📈 Scaling

### Horizontal Scaling
```yaml
# docker-compose.yml
services:
  api-server:
    deploy:
      replicas: 3
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/helpdesk
```

### Load Balancing
- Use Nginx for load balancing
- Configure sticky sessions if needed
- Monitor performance metrics

## 🔄 Backup & Recovery

### Automated Backups
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
cp helpdesk.db backups/helpdesk_$DATE.db
gzip backups/helpdesk_$DATE.db
find backups/ -name "*.gz" -mtime +7 -delete
```

### Recovery
```bash
# Restore from backup
cp backups/helpdesk_20250101_120000.db.gz helpdesk.db.gz
gunzip helpdesk.db.gz
```

## 📞 Support

For deployment issues:
1. Check the troubleshooting section
2. Review logs for error messages
3. Verify environment configuration
4. Test individual services

## 🎯 Quick Start Checklist

- [ ] Copy `env.example` to `.env`
- [ ] Configure environment variables
- [ ] Install dependencies (`poetry install`)
- [ ] Test system requirements (`python deploy.py check`)
- [ ] Start services (`python deploy.py start`)
- [ ] Verify health checks
- [ ] Test ticket creation via ADK web interface
- [ ] Test Slack integration
- [ ] Test email feedback processing 