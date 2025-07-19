# Slack Setup Guide for IT Support Notifications

This guide will help you set up Slack notifications for the AI Ticket Agent system.

## 🚀 Quick Setup

### 1. Create a Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click "Create New App"
3. Choose "From scratch"
4. Name your app: `AI Ticket Agent`
5. Select your workspace

### 2. Configure Bot Token Scopes

In your Slack app settings, go to "OAuth & Permissions" and add these scopes:

**Bot Token Scopes:**
- `chat:write` - Send messages to channels
- `channels:read` - Read channel information
- `channels:join` - Join channels (optional)

### 3. Install the App

1. Go to "Install App" in your Slack app settings
2. Click "Install to Workspace"
3. Copy the **Bot User OAuth Token** (starts with `xoxb-`)

### 4. Create Team Channels

Create these channels in your Slack workspace:

```
#it-network-support
#it-security-support
#it-hardware-support
#it-software-support
#it-access-support
#it-infrastructure-support
#it-general-support
```

### 5. Invite the Bot to Channels

Invite your bot to each channel:
```
/invite @AI Ticket Agent
```

### 6. Configure Environment Variables

Add these to your `.env` file:

```bash
# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-actual-bot-token-here
SLACK_CHANNEL_ID=C1234567890  # Your default channel ID (optional)
```

## 🔧 Advanced Configuration

### Custom Channel Mapping

You can customize the team-to-channel mapping in `ai_ticket_agent/tools/slack_handlers.py`:

```python
team_channel_map = {
    "Network Team": "#your-network-channel",
    "Security Team": "#your-security-channel", 
    "Hardware Team": "#your-hardware-channel",
    "Software Team": "#your-software-channel",
    "Access Management": "#your-access-channel",
    "Infrastructure Team": "#your-infrastructure-channel",
    "General IT Support": "#your-general-channel"
}
```

### Fallback Channel

If team-specific channels don't exist, the system will use:
1. `SLACK_CHANNEL_ID` from environment (if set)
2. `#it-general-support` as default

## 🧪 Testing the Setup

Run the test script to verify your Slack configuration:

```bash
python test_slack_notifications.py
```

Expected output:
```
✅ SLACK_BOT_TOKEN: Configured
✅ slack_sdk: Installed
✅ Success: Software Team
✅ Success: Security Team
...
```

## 📋 Message Format

The system sends rich Slack messages with:

- **Header**: Priority emoji + team name
- **User Info**: Email address and priority level
- **Problem Description**: Full issue details
- **Next Steps**: Action items for the team
- **Footer**: AI agent attribution

Example message:
```
🚨 IT Support Ticket - Software Team

User: sales.manager@company.com
Priority: CRITICAL

Problem Description:
Our CRM system is completely broken. Users can't log in...

Next Steps:
• Please acknowledge this ticket
• Update status in the thread
• Contact user when resolved

🤖 Automatically escalated by AI Support Agent
```

## 🔄 Interactive Features

The system supports Slack interactive elements:

- **Acknowledge Ticket**: Team can acknowledge receipt
- **Escalate Further**: Escalate to senior team member
- **Mark Resolved**: Mark ticket as resolved
- **Add Notes**: Add resolution notes

## 🚨 Troubleshooting

### Common Issues

**"channel_not_found" error:**
- Channel doesn't exist in your workspace
- Bot hasn't been invited to the channel
- Channel name is incorrect

**"not_in_channel" error:**
- Bot needs to be invited to the channel
- Use `/invite @YourBotName`

**"missing_scope" error:**
- Add required scopes in Slack app settings
- Reinstall the app after adding scopes

### Debug Mode

Enable debug logging by setting:
```bash
LOG_LEVEL=DEBUG
```

### Test Without Slack

If you don't have Slack set up, the system will simulate notifications:
```
🔄 Simulated: Software Team (no Slack credentials)
```

## 📞 Support

If you encounter issues:

1. Check the Slack API documentation
2. Verify your bot token and permissions
3. Ensure channels exist and bot is invited
4. Check the logs for detailed error messages

## 🔐 Security Notes

- Keep your bot token secure
- Don't commit tokens to version control
- Use environment variables for configuration
- Regularly rotate bot tokens
- Monitor bot permissions and usage 