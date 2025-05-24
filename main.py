import logging
import json
import os
import time
import schedule
from price_tracker import PriceTracker
from notifier import Notifier

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("price_tracker.log"),
        logging.StreamHandler()
    ]
)

def load_config():
    config_path = 'config.json'
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {
        "check_interval_hours": 6,
        "notification": {
            "email": None,
            "telegram": None
        }
    }

def check_prices():
    logging.info("Running price check...")
    tracker = PriceTracker()
    notifier = Notifier(
        email_config=config.get('notification', {}).get('email'),
        telegram_config=config.get('notification', {}).get('telegram')
    )
    
    price_drops = tracker.check_prices()
    if price_drops:
        recipient = config.get('notification', {}).get('recipient_email')
        notifier.notify_price_drops(price_drops, recipient)
    
    logging.info("Price check completed")

if __name__ == "__main__":
    config = load_config()
    
    # Run once immediately
    check_prices()
    
    # Schedule regular checks
    interval_hours = config.get('check_interval_hours', 6)
    logging.info(f"Scheduling price checks every {interval_hours} hours")
    
    schedule.every(interval_hours).hours.do(check_prices)
    
    # Keep the script running
    logging.info("Price tracker is running. Press Ctrl+C to stop.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute if there are scheduled tasks to run
    except KeyboardInterrupt:
        logging.info("Price tracker stopped by user")
