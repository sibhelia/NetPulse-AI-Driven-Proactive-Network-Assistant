import os
from twilio.rest import Client
import logging

logger = logging.getLogger(__name__)

# Twilio Credentials (Environment Variables)
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "demo_mode")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "demo_mode")
TWILIO_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "+1234567890")

def send_sms(phone_number: str, message: str) -> bool:
    """
    Gerçek SMS gönder (Twilio ile) veya demo mode'da logla
    
    Args:
        phone_number: Alıcı telefon numarası (+90 5XX XXX XX XX formatında)
        message: SMS mesajı
    
    Returns:
        bool: Başarılı ise True
    """
    try:
        if ACCOUNT_SID == "demo_mode":
            # Demo Mode - Console'a yaz
            logger.warning("=" * 60)
            logger.warning("📱 [DEMO MODE] SMS SİMÜLASYONU")
            logger.warning("=" * 60)
            logger.warning(f"📞 Alıcı: {phone_number}")
            logger.warning(f"📝 Mesaj:\n{message}")
            logger.warning("=" * 60)
            logger.warning("ℹ️  Gerçek SMS göndermek için TWILIO_ACCOUNT_SID ayarlayın")
            logger.warning("=" * 60)
            return True
        
        # Gerçek SMS Gönderimi
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        msg = client.messages.create(
            body=message,
            from_=TWILIO_NUMBER,
            to=phone_number
        )
        logger.info(f"✅ SMS Gönderildi! SID: {msg.sid}, To: {phone_number}")
        return True
        
    except Exception as e:
        logger.error(f"❌ SMS Gönderme Hatası: {e}")
        return False