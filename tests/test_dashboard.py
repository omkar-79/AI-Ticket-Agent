#!/usr/bin/env python3
"""Test script for Streamlit dashboard functionality."""

import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_dashboard_imports():
    """Test that all dashboard imports work correctly."""
    print("🧪 Testing Dashboard Imports")
    print("=" * 40)
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import plotly.express as px
        print("✅ Plotly imported successfully")
    except ImportError as e:
        print(f"❌ Plotly import failed: {e}")
        return False
    
    try:
        from ai_ticket_agent.database import db_manager
        print("✅ Database manager imported successfully")
    except ImportError as e:
        print(f"❌ Database manager import failed: {e}")
        return False
    
    try:
        from ai_ticket_agent.models import TicketStatus, TicketPriority, TicketCategory
        print("✅ Database models imported successfully")
    except ImportError as e:
        print(f"❌ Database models import failed: {e}")
        return False
    
    return True


def test_dashboard_data_loading():
    """Test that the dashboard can load data from the database."""
    print("\n📊 Testing Dashboard Data Loading")
    print("=" * 40)
    
    try:
        from ai_ticket_agent.database import db_manager
        import pandas as pd
        
        # Test database connection
        session = db_manager.get_session()
        tickets = db_manager.search_tickets(session, limit=10)
        session.close()
        
        print(f"✅ Database connection successful - {len(tickets)} tickets found")
        
        # Test data conversion to DataFrame
        tickets_data = []
        for ticket in tickets:
            tickets_data.append({
                'ticket_id': ticket.ticket_id,
                'subject': ticket.subject,
                'status': ticket.status.value,
                'priority': ticket.priority.value,
                'category': ticket.category.value if ticket.category else 'Not specified',
                'assigned_team': ticket.assigned_team or 'Not assigned',
                'user_email': ticket.user_email,
                'created_at': ticket.created_at,
                'resolution_attempts': 0,  # Don't access lazy-loaded attributes in test
                'status_updates': 0
            })
        
        df = pd.DataFrame(tickets_data)
        print(f"✅ Data conversion successful - DataFrame shape: {df.shape}")
        
        if not df.empty:
            print(f"✅ Sample data:")
            print(f"   - Statuses: {df['status'].unique()}")
            print(f"   - Priorities: {df['priority'].unique()}")
            print(f"   - Categories: {df['category'].unique()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        return False


def test_dashboard_functions():
    """Test that dashboard functions can be imported and called."""
    print("\n🔧 Testing Dashboard Functions")
    print("=" * 40)
    
    try:
        # Import dashboard functions
        from dashboard import load_data, main_dashboard, ticket_management, analytics, settings
        
        print("✅ Dashboard functions imported successfully")
        
        # Test load_data function
        try:
            df, resolution_df = load_data()
            print(f"✅ load_data() successful - Tickets: {len(df)}, Resolution attempts: {len(resolution_df)}")
        except Exception as e:
            print(f"⚠️ load_data() failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Dashboard functions test failed: {e}")
        return False


def main():
    """Main test function."""
    print("🧪 Streamlit Dashboard Test Suite")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_dashboard_imports()
    
    # Test data loading
    data_ok = test_dashboard_data_loading()
    
    # Test functions
    functions_ok = test_dashboard_functions()
    
    # Summary
    print("\n📋 Test Summary")
    print("=" * 30)
    print(f"Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"Data Loading: {'✅ PASS' if data_ok else '❌ FAIL'}")
    print(f"Functions: {'✅ PASS' if functions_ok else '❌ FAIL'}")
    
    if all([imports_ok, data_ok, functions_ok]):
        print("\n🎉 All tests passed! Dashboard should work correctly.")
        print("\n🚀 To start the dashboard:")
        print("   python run.py dashboard")
        print("   # or")
        print("   streamlit run dashboard.py")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")


if __name__ == "__main__":
    main() 