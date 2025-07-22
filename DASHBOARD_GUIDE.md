# 🎫 Dashboard User Guide

## **Quick Start**

### **1. Start the Dashboard**
```bash
python run.py dashboard
```
The dashboard will open at: `http://localhost:8501`

### **2. View Your Ticket**

#### **Method 1: Search by Ticket ID**
1. Go to **"Ticket Management"** in the sidebar
2. In the search box, enter: `TICKET-20250720-012AC57C`
3. Click on the ticket to see details

#### **Method 2: Search by Keywords**
1. Go to **"Ticket Management"** in the sidebar
2. Search for: `printer` or `test.user@company.com`
3. Find your ticket in the results

#### **Method 3: Filter by Status**
1. Go to **"Ticket Management"** in the sidebar
2. Set Status filter to: `open`
3. Look for the printer ticket

### **3. Dashboard Features**

#### **📊 Main Dashboard**
- **Real-time Metrics**: Total, open, resolved tickets
- **Interactive Charts**: Status, priority, category distributions
- **Last Updated**: Shows when data was last refreshed

#### **🎫 Ticket Management**
- **Search**: Find tickets by ID, subject, or user email
- **Filters**: Filter by status, priority, team
- **Details**: Click on any ticket to see full history

#### **📈 Analytics**
- **Time Trends**: Daily ticket volume
- **Performance**: Team resolution rates
- **Resolution Times**: How long tickets take to resolve

### **4. Refresh Data**

#### **Manual Refresh**
- Click **"🔄 Refresh Data"** button in the sidebar
- This will reload all data from the database

#### **Auto Refresh**
- The dashboard shows **"Last updated"** timestamp
- Refresh manually when you want to see new tickets

### **5. Your Test Ticket Details**

**Ticket ID**: `TICKET-20250720-012AC57C`
- **Subject**: Printer showing offline - need help
- **Status**: Open (escalated)
- **Priority**: High
- **Category**: Hardware
- **User**: test.user@company.com
- **Resolution Attempts**: 1 (failed, escalated to human team)

### **6. Troubleshooting**

#### **Dashboard Not Loading**
```bash
# Check if dashboard is running
ps aux | grep streamlit

# Restart dashboard
python run.py dashboard
```

#### **No Tickets Showing**
```bash
# Create a test ticket
python create_test_ticket.py

# Check database
python run.py init-db
```

#### **Search Not Working**
- Make sure you're in the **"Ticket Management"** section
- Try searching with partial terms (e.g., "printer" instead of full subject)
- Check the ticket ID format: `TICKET-YYYYMMDD-XXXXXXXX`

### **7. Next Steps**

1. **View your ticket** in the dashboard
2. **Explore the analytics** to see system performance
3. **Create more test tickets** to see the system in action
4. **Try different search terms** to test the filtering

The dashboard provides a complete view of your AI Ticket Agent system with real-time data and interactive features! 🎉 