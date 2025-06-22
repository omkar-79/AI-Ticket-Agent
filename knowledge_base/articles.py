"""Local knowledge base articles for IT support."""

from typing import List, Dict, Any, Optional
from datetime import datetime


# Sample knowledge base articles
KNOWLEDGE_ARTICLES = [
    {
        "id": "kb-001",
        "title": "VPN Connection Troubleshooting Guide",
        "content": """
# VPN Connection Troubleshooting Guide

## Common VPN Issues and Solutions

### Issue: VPN keeps disconnecting
**Solution:**
1. Check your internet connection
2. Restart the VPN client
3. Clear VPN cache and cookies
4. Update VPN client to latest version
5. Check firewall settings

### Issue: Cannot connect to VPN
**Solution:**
1. Verify VPN server is accessible
2. Check credentials are correct
3. Ensure VPN client is properly installed
4. Try connecting from different network
5. Contact IT support if issue persists

### Issue: Slow VPN connection
**Solution:**
1. Close unnecessary applications
2. Check internet bandwidth
3. Try connecting to different VPN server
4. Update network drivers
5. Restart your computer
        """,
        "category": "network",
        "tags": ["vpn", "connectivity", "remote", "network"],
        "author": "Network Team",
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-01-15T10:00:00Z",
        "relevance_score": 0.95
    },
    {
        "id": "kb-002",
        "title": "Password Reset and Account Access",
        "content": """
# Password Reset and Account Access

## How to Reset Your Password

### Self-Service Password Reset
1. Go to the password reset portal
2. Enter your email address
3. Verify your identity with security questions
4. Create a new strong password
5. Log in with new credentials

### Account Lockout Resolution
1. Wait 15 minutes for automatic unlock
2. Contact IT support if still locked
3. Provide employee ID for verification
4. Reset password through IT support
5. Enable multi-factor authentication

### Password Requirements
- Minimum 8 characters
- Include uppercase and lowercase letters
- Include numbers and special characters
- Cannot reuse last 5 passwords
- Change every 90 days
        """,
        "category": "access",
        "tags": ["password", "reset", "account", "lockout", "authentication"],
        "author": "Access Management",
        "created_at": "2024-01-10T09:00:00Z",
        "updated_at": "2024-01-10T09:00:00Z",
        "relevance_score": 0.90
    },
    {
        "id": "kb-003",
        "title": "Email Configuration and Troubleshooting",
        "content": """
# Email Configuration and Troubleshooting

## Setting Up Email Client

### Outlook Configuration
1. Open Outlook
2. Add new account
3. Enter email address and password
4. Configure server settings:
   - IMAP: imap.company.com
   - SMTP: smtp.company.com
   - Port: 587 (TLS)
5. Test connection

### Common Email Issues

#### Cannot Send Emails
1. Check internet connection
2. Verify SMTP settings
3. Check email size limits
4. Ensure recipient address is correct
5. Check for antivirus interference

#### Cannot Receive Emails
1. Check IMAP settings
2. Verify email filters
3. Check spam/junk folder
4. Ensure email client is running
5. Check server status

#### Email Sync Issues
1. Restart email client
2. Clear cache and cookies
3. Check sync settings
4. Update email client
5. Contact IT support
        """,
        "category": "email",
        "tags": ["email", "outlook", "configuration", "sync", "smtp", "imap"],
        "author": "Email Support",
        "created_at": "2024-01-12T11:00:00Z",
        "updated_at": "2024-01-12T11:00:00Z",
        "relevance_score": 0.85
    },
    {
        "id": "kb-004",
        "title": "Hardware Troubleshooting Guide",
        "content": """
# Hardware Troubleshooting Guide

## Common Hardware Issues

### Laptop Won't Turn On
1. Check power adapter connection
2. Try different power outlet
3. Remove battery and reinsert
4. Hold power button for 10 seconds
5. Contact IT support if issue persists

### Printer Issues
1. Check power and USB connections
2. Restart printer
3. Clear print queue
4. Update printer drivers
5. Check for paper jams

### Monitor Problems
1. Check power and video cables
2. Try different monitor
3. Update graphics drivers
4. Check display settings
5. Test with different computer

### Keyboard/Mouse Issues
1. Check USB connections
2. Try different USB ports
3. Replace batteries (wireless)
4. Clean devices
5. Update drivers
        """,
        "category": "hardware",
        "tags": ["hardware", "laptop", "printer", "monitor", "keyboard", "mouse"],
        "author": "Hardware Support",
        "created_at": "2024-01-08T14:00:00Z",
        "updated_at": "2024-01-08T14:00:00Z",
        "relevance_score": 0.80
    },
    {
        "id": "kb-005",
        "title": "Software Installation and Updates",
        "content": """
# Software Installation and Updates

## Installing Company Software

### Software Center
1. Open Software Center from Start menu
2. Browse available applications
3. Click "Install" on desired software
4. Wait for installation to complete
5. Restart computer if prompted

### Manual Installation
1. Download software from approved sources
2. Run installer as administrator
3. Follow installation wizard
4. Accept license agreements
5. Complete installation

### Software Updates
1. Check for updates regularly
2. Install critical security updates immediately
3. Schedule non-critical updates
4. Restart computer after updates
5. Verify software functionality

### Troubleshooting Installation Issues
1. Check administrator privileges
2. Disable antivirus temporarily
3. Clear temporary files
4. Check disk space
5. Contact IT support
        """,
        "category": "software",
        "tags": ["software", "installation", "updates", "applications", "admin"],
        "author": "Software Support",
        "created_at": "2024-01-14T16:00:00Z",
        "updated_at": "2024-01-14T16:00:00Z",
        "relevance_score": 0.75
    },
    {
        "id": "kb-006",
        "title": "Security Best Practices",
        "content": """
# Security Best Practices

## Password Security
1. Use strong, unique passwords
2. Enable multi-factor authentication
3. Never share passwords
4. Change passwords regularly
5. Use password manager

## Email Security
1. Don't click suspicious links
2. Verify sender addresses
3. Don't open unexpected attachments
4. Report phishing attempts
5. Use company email for work only

## Device Security
1. Lock computer when away
2. Keep software updated
3. Use company antivirus
4. Don't install unauthorized software
5. Report lost/stolen devices immediately

## Data Protection
1. Don't store sensitive data locally
2. Use approved cloud storage
3. Encrypt sensitive files
4. Follow data classification guidelines
5. Report security incidents
        """,
        "category": "security",
        "tags": ["security", "password", "email", "device", "data", "phishing"],
        "author": "Security Team",
        "created_at": "2024-01-05T13:00:00Z",
        "updated_at": "2024-01-05T13:00:00Z",
        "relevance_score": 0.90
    }
]


def get_articles() -> List[Dict[str, Any]]:
    """Get all knowledge base articles."""
    return KNOWLEDGE_ARTICLES


def search_articles(query: str, category: Optional[str] = None, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search knowledge base articles.
    
    Args:
        query: Search query
        category: Filter by category
        max_results: Maximum number of results
        
    Returns:
        List of matching articles
    """
    query_lower = query.lower()
    results = []
    
    for article in KNOWLEDGE_ARTICLES:
        # Skip if category filter doesn't match
        if category and article["category"] != category:
            continue
        
        # Check if query matches title, content, or tags
        title_match = query_lower in article["title"].lower()
        content_match = query_lower in article["content"].lower()
        tag_match = any(query_lower in tag.lower() for tag in article["tags"])
        
        if title_match or content_match or tag_match:
            results.append(article)
            
            if len(results) >= max_results:
                break
    
    # Sort by relevance score
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    return results


def get_article_by_id(article_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific article by ID.
    
    Args:
        article_id: The article ID
        
    Returns:
        The article if found, None otherwise
    """
    for article in KNOWLEDGE_ARTICLES:
        if article["id"] == article_id:
            return article
    return None


def get_articles_by_category(category: str) -> List[Dict[str, Any]]:
    """
    Get all articles in a specific category.
    
    Args:
        category: The category to filter by
        
    Returns:
        List of articles in the category
    """
    return [article for article in KNOWLEDGE_ARTICLES if article["category"] == category] 