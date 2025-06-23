"""Monitoring scheduler for running escalation and SLA monitoring cycles."""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from ai_ticket_agent.tools.monitoring import run_monitoring_cycle
from ai_ticket_agent.tools.database import init_database


class MonitoringScheduler:
    """Scheduler for running monitoring cycles at regular intervals."""
    
    def __init__(self, interval_minutes: int = 5):
        """
        Initialize the monitoring scheduler.
        
        Args:
            interval_minutes: How often to run monitoring cycles (default: 5 minutes)
        """
        self.interval_minutes = interval_minutes
        self.running = False
        self.thread = None
        self.last_run = None
        self.run_count = 0
        self.errors = []
        
    def start(self):
        """Start the monitoring scheduler."""
        if self.running:
            print("⚠️ Monitoring scheduler is already running")
            return
        
        print(f"🚀 Starting monitoring scheduler (interval: {self.interval_minutes} minutes)")
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop the monitoring scheduler."""
        if not self.running:
            print("⚠️ Monitoring scheduler is not running")
            return
        
        print("🛑 Stopping monitoring scheduler...")
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)
        print("✅ Monitoring scheduler stopped")
    
    def _run_scheduler(self):
        """Internal method to run the scheduler loop."""
        while self.running:
            try:
                # Run monitoring cycle
                self._run_monitoring_cycle()
                
                # Wait for next cycle
                time.sleep(self.interval_minutes * 60)
                
            except Exception as e:
                error_msg = f"Error in monitoring cycle: {str(e)}"
                print(f"❌ {error_msg}")
                self.errors.append({
                    "timestamp": datetime.now().isoformat(),
                    "error": error_msg
                })
                
                # Wait a bit before retrying
                time.sleep(60)
    
    def _run_monitoring_cycle(self):
        """Run a single monitoring cycle."""
        print(f"🔄 Running monitoring cycle #{self.run_count + 1} at {datetime.now()}")
        
        # Initialize database
        init_database()
        
        # Run monitoring cycle
        results = run_monitoring_cycle()
        
        # Update stats
        self.last_run = datetime.now().isoformat()
        self.run_count += 1
        
        # Log results
        summary = results.get("monitoring_results", {}).get("summary", {})
        escalations = summary.get("escalations_needed", 0)
        sla_alerts = summary.get("sla_alerts", 0)
        
        if escalations > 0 or sla_alerts > 0:
            print(f"⚠️ Monitoring cycle found {escalations} escalations and {sla_alerts} SLA alerts")
        else:
            print(f"✅ Monitoring cycle complete - no issues found")
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the scheduler."""
        return {
            "running": self.running,
            "interval_minutes": self.interval_minutes,
            "last_run": self.last_run,
            "run_count": self.run_count,
            "error_count": len(self.errors),
            "recent_errors": self.errors[-5:] if self.errors else []
        }
    
    def run_once(self) -> Dict[str, Any]:
        """Run a single monitoring cycle immediately."""
        print("🔄 Running single monitoring cycle...")
        
        try:
            # Initialize database
            init_database()
            
            # Run monitoring cycle
            results = run_monitoring_cycle()
            
            print("✅ Single monitoring cycle complete")
            return results
            
        except Exception as e:
            error_msg = f"Error in single monitoring cycle: {str(e)}"
            print(f"❌ {error_msg}")
            self.errors.append({
                "timestamp": datetime.now().isoformat(),
                "error": error_msg
            })
            return {"error": error_msg}


# Global scheduler instance
_monitoring_scheduler: Optional[MonitoringScheduler] = None


def get_monitoring_scheduler() -> MonitoringScheduler:
    """Get the global monitoring scheduler instance."""
    global _monitoring_scheduler
    if _monitoring_scheduler is None:
        _monitoring_scheduler = MonitoringScheduler()
    return _monitoring_scheduler


def start_monitoring_scheduler(interval_minutes: int = 5):
    """Start the global monitoring scheduler."""
    scheduler = get_monitoring_scheduler()
    scheduler.interval_minutes = interval_minutes
    scheduler.start()


def stop_monitoring_scheduler():
    """Stop the global monitoring scheduler."""
    global _monitoring_scheduler
    if _monitoring_scheduler:
        _monitoring_scheduler.stop()


def run_monitoring_once() -> Dict[str, Any]:
    """Run a single monitoring cycle."""
    scheduler = get_monitoring_scheduler()
    return scheduler.run_once()


def get_scheduler_status() -> Dict[str, Any]:
    """Get the status of the monitoring scheduler."""
    scheduler = get_monitoring_scheduler()
    return scheduler.get_status() 