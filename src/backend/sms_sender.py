import os
import vonage
from vonage_sms import requests as sms_requests
import logging
from dotenv import load_dotenv

# Load .env file explicitly
load_dotenv()

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Vonage Credentials (Environment Variables)
VONAGE_API_KEY = os.getenv("VONAGE_API_KEY", "")
VONAGE_API_SECRET = os.getenv("VONAGE_API_SECRET", "")
VONAGE_BRAND_NAME = os.getenv("VONAGE_BRAND_NAME", "NetPulse")

def send_sms(phone_number: str, message: str) -> tuple[bool, str]:
    """
    Gerçek SMS gönder (Vonage ile)
    
    Returns:
        tuple: (Başarılı mı?, Hata Mesajı/Success Durumu)
    """
    try:
        if not VONAGE_API_KEY or not VONAGE_API_SECRET:
             return False, "Vonage CREDENTIALS MISSING IN .ENV"

        # Clean phone number (remove spaces)
        formatted_phone = phone_number.replace(" ", "").replace("+", "") 
        
        # Initialize Vonage Client
        client = vonage.Vonage(vonage.Auth(api_key=VONAGE_API_KEY, api_secret=VONAGE_API_SECRET))
        
        # Send SMS
        message_payload = sms_requests.SmsMessage(
            to=formatted_phone,
            from_=VONAGE_BRAND_NAME,
            text=message
        )
        responseData = client.sms.send(message_payload)

        # Access attributes with dot notation if it is an object
        if responseData.messages[0].status == "0":
            msg_id = responseData.messages[0].message_id
            logger.info(f"SMS Gonderildi! ID: {msg_id}, To: {formatted_phone}")
            return True, f"Gonderildi: {formatted_phone} (ID: {msg_id})"
        else:
            # error_text might be error_text or error-text depending on object mapping
            # usually python SDKs map kebab-case to snake_case
            error_text = responseData.messages[0].error_text
            logger.error(f"SMS Gonderme Hatasi: {error_text}")
            return False, f"Vonage Error: {error_text}"
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"SMS Gonderme Hatasi (Exception): {error_msg}")
        return False, error_msg