"""
Stock Data Updater Service
Service that runs once at startup and then daily at 3:30 PM IST
"""

import threading
import schedule
import time
from datetime import datetime
import pytz
from stock_data_updater import StockDataUpdater
from logger_config import app_logger

# Use main application logger
logger = app_logger

class StockUpdaterService:
    """Service to manage stock data updates"""
    
    def __init__(self):
        self.updater = StockDataUpdater()
        self.is_running = False
        self.scheduler_thread = None
        
    def start(self):
        """Start the service - run once immediately and schedule daily updates"""
        if self.is_running:
            logger.warning("Stock updater service is already running")
            return
            
        logger.info("Starting Stock Data Updater Service...")
        
        # Run initial update
        try:
            logger.info("Running initial stock data update...")
            self.updater.update_all_data()
            logger.info("Initial stock data update completed")
        except Exception as e:
            logger.error(f"Initial stock data update failed: {e}")
        
        # Schedule daily updates at 3:30 PM IST
        # Converting IST to UTC: 3:30 PM IST = 10:00 AM UTC (IST is UTC+5:30)
        schedule.every().day.at("10:00").do(self._scheduled_update)
        
        # Start scheduler in background thread
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("Stock updater service started. Daily updates scheduled at 3:30 PM IST (10:00 AM UTC)")
    
    def _scheduled_update(self):
        """Run scheduled update"""
        try:
            ist = pytz.timezone('Asia/Kolkata')
            current_time = datetime.now(ist)
            logger.info(f"Running scheduled stock data update at {current_time.strftime('%Y-%m-%d %H:%M:%S IST')}")
            
            self.updater.update_all_data()
            logger.info("Scheduled stock data update completed successfully")
            
        except Exception as e:
            logger.error(f"Scheduled stock data update failed: {e}")
    
    def _run_scheduler(self):
        """Run the scheduler in background"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def stop(self):
        """Stop the service"""
        if not self.is_running:
            return
            
        logger.info("Stopping Stock Data Updater Service...")
        self.is_running = False
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        schedule.clear()
        logger.info("Stock updater service stopped")
    
    def manual_update(self):
        """Trigger a manual update"""
        try:
            logger.info("Running manual stock data update...")
            self.updater.update_all_data()
            logger.info("Manual stock data update completed")
            return True
        except Exception as e:
            logger.error(f"Manual stock data update failed: {e}")
            return False

# Global service instance
stock_service = StockUpdaterService()

def start_stock_updater_service():
    """Start the stock updater service"""
    stock_service.start()

def stop_stock_updater_service():
    """Stop the stock updater service"""
    stock_service.stop()

def manual_update_stocks():
    """Trigger manual update"""
    return stock_service.manual_update()
