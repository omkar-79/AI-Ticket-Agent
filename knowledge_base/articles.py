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
        """,
        "category": "software",
        "tags": ["software", "installation", "updates", "applications", "programs"],
        "author": "Software Support",
        "created_at": "2024-01-14T13:00:00Z",
        "updated_at": "2024-01-14T13:00:00Z",
        "relevance_score": 0.85
    },
    {
        "id": "kb-006",
        "title": "Sound and Audio Troubleshooting Guide",
        "content": """
# Sound and Audio Troubleshooting Guide

## Common Sound and Audio Issues

### Issue: No sound from speakers or headphones
**Solution:**
1. Check if audio is muted in system tray
2. Verify speaker/headphone connections
3. Test with different audio device
4. Check audio driver status in Device Manager
5. Restart audio service (Windows Audio)

### Issue: Sound is too quiet or distorted
**Solution:**
1. Adjust volume levels in system and application
2. Check audio cable connections
3. Test with different audio source
4. Update or reinstall audio drivers
5. Check for audio enhancements that may cause distortion

### Issue: Microphone not working
**Solution:**
1. Check microphone permissions in system settings
2. Verify microphone is set as default input device
3. Test microphone in different application
4. Check microphone cable connections
5. Update audio drivers

### Issue: Audio device not recognized
**Solution:**
1. Unplug and reconnect audio device
2. Try different USB port (for USB devices)
3. Check Device Manager for audio device status
4. Update or reinstall audio drivers
5. Restart computer and test again

### Issue: Audio lag or delay
**Solution:**
1. Close unnecessary applications
2. Check audio buffer settings
3. Update audio drivers
4. Disable audio enhancements
5. Check for system performance issues

### Issue: Bluetooth audio problems
**Solution:**
1. Remove and re-pair Bluetooth device
2. Check Bluetooth driver status
3. Ensure device is in pairing mode
4. Update Bluetooth drivers
5. Check for interference from other devices
        """,
        "category": "hardware",
        "tags": ["sound", "audio", "speaker", "microphone", "headphone", "speakers", "soundcard", "bluetooth", "volume", "mute"],
        "author": "Hardware Support",
        "created_at": "2024-01-20T15:00:00Z",
        "updated_at": "2024-01-20T15:00:00Z",
        "relevance_score": 0.95
    },
    {
        "id": "kb-007",
        "title": "WiFi Connection Troubleshooting Guide",
        "content": """
# WiFi Connection Troubleshooting Guide

## Common WiFi Issues and Solutions

### Issue: Cannot connect to WiFi
**Solution:**
1. Check if WiFi is enabled on your device
2. Verify you're connecting to the correct network
3. Enter the correct WiFi password
4. Restart your WiFi router/modem
5. Try connecting from a different location

### Issue: WiFi keeps disconnecting
**Solution:**
1. Check WiFi signal strength
2. Move closer to the WiFi router
3. Restart your device's WiFi adapter
4. Update WiFi drivers
5. Check for interference from other devices

### Issue: Slow WiFi connection
**Solution:**
1. Check internet speed with speed test
2. Restart WiFi router and modem
3. Update WiFi drivers
4. Check for background downloads
5. Contact ISP if issue persists

### Issue: WiFi network not visible
**Solution:**
1. Check if router is powered on
2. Restart WiFi router
3. Check router's WiFi settings
4. Update WiFi drivers
5. Try connecting via Ethernet cable
        """,
        "category": "network",
        "tags": ["wifi", "wireless", "internet", "connection", "router", "network", "signal"],
        "author": "Network Support",
        "created_at": "2024-01-18T12:00:00Z",
        "updated_at": "2024-01-18T12:00:00Z",
        "relevance_score": 0.90
    },
    {
        "id": "kb-008",
        "title": "Display and Monitor Troubleshooting",
        "content": """
# Display and Monitor Troubleshooting

## Common Display Issues

### Issue: Monitor shows no signal
**Solution:**
1. Check power and video cable connections
2. Try different video cable (HDMI, VGA, DisplayPort)
3. Test monitor with different computer
4. Check graphics card connections
5. Update graphics drivers

### Issue: Display resolution problems
**Solution:**
1. Adjust resolution in display settings
2. Update graphics drivers
3. Check monitor's native resolution
4. Try different refresh rates
5. Restart graphics driver service
        """,
        "category": "hardware",
        "tags": ["display", "monitor", "screen", "connection", "usb-c", "hdmi", "vga", "signal", "hardware"],
        "author": "Hardware Support",
        "created_at": "2024-01-25T10:00:00Z",
        "updated_at": "2024-01-25T10:00:00Z",
        "relevance_score": 0.95
    },
    {
        "id": "kb-009",
        "title": "CPU Overheating and Fan Issues",
        "content": """
# CPU Overheating and Fan Issues

## Common CPU Overheating Problems

### Issue: CPU overheating causing system shutdown
**Solution:**
1. Check if CPU fan is spinning properly
2. Clean dust from CPU heatsink and fan
3. Ensure proper thermal paste application
4. Check CPU temperature in BIOS/UEFI
5. Verify adequate airflow in computer case

### Issue: Loud or noisy CPU fan
**Solution:**
1. Clean dust and debris from fan blades
2. Check if fan is properly seated on heatsink
3. Replace worn-out fan bearings
4. Adjust fan speed settings in BIOS
5. Consider upgrading to a better CPU cooler

### Issue: CPU fan not spinning
**Solution:**
1. Check fan power connection to motherboard
2. Verify fan is properly connected to CPU_FAN header
3. Test fan in different motherboard header
4. Replace faulty CPU fan
5. Check motherboard fan control settings

### Issue: High CPU temperatures under load
**Solution:**
1. Monitor CPU usage and close unnecessary programs
2. Improve case ventilation and airflow
3. Upgrade CPU cooler to better model
4. Apply new thermal paste
5. Check for overclocking settings that may cause overheating

### Issue: Thermal throttling affecting performance
**Solution:**
1. Clean CPU heatsink thoroughly
2. Reapply thermal paste with proper amount
3. Ensure heatsink is properly mounted
4. Check case airflow and add additional fans
5. Consider liquid cooling for high-performance systems
        """,
        "category": "hardware",
        "tags": ["cpu", "overheating", "fan", "temperature", "thermal", "cooling", "hardware", "noise"],
        "author": "Hardware Support",
        "created_at": "2024-01-30T11:00:00Z",
        "updated_at": "2024-01-30T11:00:00Z",
        "relevance_score": 0.95
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
        category: Filter by category (optional - if None, searches all categories)
        max_results: Maximum number of results
        
    Returns:
        List of matching articles
    """
    query_lower = query.lower()
    query_words = query_lower.split()
    results = []
    
    # Define specific keyword groups to avoid false matches
    sound_audio_keywords = ['sound', 'audio', 'speaker', 'microphone', 'headphone', 'speakers', 'soundcard', 'hear', 'hearing']
    network_keywords = ['wifi', 'internet', 'vpn', 'network', 'router', 'modem', 'ethernet', 'wireless', 'connect']
    display_keywords = ['display', 'monitor', 'screen', 'signal', 'usb-c', 'hdmi', 'vga', 'video']
    hardware_keywords = ['printer', 'keyboard', 'mouse', 'laptop', 'computer', 'device', 'cable']
    
    # Check if query contains specific keywords
    query_has_sound = any(word in sound_audio_keywords for word in query_words)
    query_has_network = any(word in network_keywords for word in query_words)
    query_has_display = any(word in display_keywords for word in query_words)
    query_has_hardware = any(word in hardware_keywords for word in query_words)
    
    for article in KNOWLEDGE_ARTICLES:
        # Skip if category filter doesn't match (only if category is specified)
        if category and article["category"] != category:
            continue
        
        # STRICT CATEGORY MATCHING: If query is clearly about sound/audio, only return hardware articles
        if query_has_sound and article["category"] != "hardware":
            continue  # Skip non-hardware articles for sound queries
        
        # If query is clearly about network, only return network articles
        if query_has_network and article["category"] != "network":
            continue  # Skip non-network articles for network queries
        
        # Calculate relevance score based on multiple factors
        relevance_score = 0.0
        
        # Check exact phrase matches (highest priority)
        title_exact = query_lower in article["title"].lower()
        content_exact = query_lower in article["content"].lower()
        tag_exact = any(query_lower in tag.lower() for tag in article["tags"])
        
        if title_exact:
            relevance_score += 20.0  # Increased weight for exact matches
        if content_exact:
            relevance_score += 15.0
        if tag_exact:
            relevance_score += 12.0
        
        # Score based on keyword category matching
        if query_has_sound and article["category"] == "hardware":
            relevance_score += 15.0  # High score for sound + hardware
        elif query_has_network and article["category"] == "network":
            relevance_score += 15.0  # High score for network + network
        elif query_has_display and article["category"] == "hardware":
            relevance_score += 12.0
        elif query_has_hardware and article["category"] == "hardware":
            relevance_score += 8.0
        
        # Check word matches (lower priority, but more specific)
        title_words = article["title"].lower().split()
        content_words = article["content"].lower().split()
        
        # Only count meaningful word matches (3+ characters)
        meaningful_query_words = [word for word in query_words if len(word) >= 3]
        title_word_matches = sum(1 for word in meaningful_query_words if word in title_words)
        content_word_matches = sum(1 for word in meaningful_query_words if word in content_words)
        
        relevance_score += title_word_matches * 3.0  # Increased weight
        relevance_score += content_word_matches * 1.0
        
        # Add base relevance score from article (but with lower weight)
        relevance_score += article.get("relevance_score", 0.0) * 0.3
        
        # Only include articles with positive relevance scores
        if relevance_score > 0:
            # Create a copy of the article with updated relevance score
            article_copy = article.copy()
            article_copy["relevance_score"] = relevance_score
            results.append(article_copy)
            
            if len(results) >= max_results:
                break
    
    # Sort by calculated relevance score (highest first)
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