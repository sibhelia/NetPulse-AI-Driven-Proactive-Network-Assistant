import requests
import os
import logging
from dotenv import load_dotenv

# Load .env explicitly
load_dotenv()

# Configure Logging
logger = logging.getLogger(__name__)

# Telegram Credentials
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message: str) -> tuple[bool, str]:
    """
    Send a message to a Telegram Chat via Bot API
    """
    # Reload env to catch updates
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        return False, "TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing in .env"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        if response.status_code == 200 and data.get("ok"):
            logger.info(f"Telegram Message Sent to {chat_id}")
            return True, "Message sent successfully"
        else:
            error_desc = data.get("description", "Unknown error")
            logger.error(f"Telegram API Error: {error_desc}")
            return False, f"Telegram Error: {error_desc}"
            
    except Exception as e:
        logger.error(f"Telegram Connection Error: {e}")
        return False, str(e)
