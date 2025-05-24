import logging
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Notifier:
    def __init__(self, email_config=None, telegram_config=None):
        # If email_config is provided, use it for email notifications
        self.email_config = email_config
        # If telegram_config is provided, use it for telegram notifications
        self.telegram_config = telegram_config
    
    def send_email(self, subject, message, to_email):
        if not self.email_config:
            logging.warning("Email configuration not provided")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            
            logging.info(f"Email notification sent to {to_email}")
            return True
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
            return False
    
    def send_telegram(self, message):
        if not self.telegram_config:
            logging.warning("Telegram configuration not provided")
            return False
        
        try:
            bot_token = self.telegram_config['bot_token']
            chat_id = self.telegram_config['chat_id']
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=payload)
            
            if response.status_code == 200:
                logging.info(f"Telegram notification sent to chat ID {chat_id}")
                return True
            else:
                logging.error(f"Failed to send Telegram message: {response.text}")
                return False
        except Exception as e:
            logging.error(f"Failed to send Telegram message: {e}")
            return False
    
    def notify_price_drops(self, price_drops, to_email=None):
        if not price_drops:
            logging.info("No price drops to notify")
            return
        
        # Log notifications
        for product in price_drops:
            logging.info(f"Price Drop Alert: {product['name']} is now ₹{product['current_price']} (below threshold of ₹{product['threshold_price']})")
        
        # Prepare message content
        message = "The following products have dropped below your price threshold:\n\n"
        for product in price_drops:
            message += f"- {product['name']}: ₹{product['current_price']} (below ₹{product['threshold_price']})\n"
            message += f"  Link: {product['url']}\n\n"
        
        # Send email if configured
        if self.email_config and to_email:
            subject = f"Price Drop Alert: {len(price_drops)} products on sale!"
            self.send_email(subject, message, to_email)
        
        # Send telegram if configured
        if self.telegram_config:
            telegram_message = f"<b>Price Drop Alert: {len(price_drops)} products on sale!</b>\n\n"
            for product in price_drops:
                telegram_message += f"<b>{product['name']}</b>\n"
                telegram_message += f"Price: ₹{product['current_price']} (below ₹{product['threshold_price']})\n"
                telegram_message += f"<a href='{product['url']}'>View on Flipkart</a>\n\n"
            
            self.send_telegram(telegram_message)