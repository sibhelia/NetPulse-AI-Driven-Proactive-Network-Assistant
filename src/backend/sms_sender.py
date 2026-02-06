from twilio.rest import Client

# Twilio Paneli'nden alacağın bilgileri buraya yaz:
ACCOUNT_SID = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" # Burayı kendi SID'inle değiştir
AUTH_TOKEN = "your_auth_token_here"           # Burayı kendi Token'ınla değiştir
TWILIO_NUMBER = "+1234567890"                 # Twilio'nun sana verdiği numara
MY_PHONE_NUMBER = "+90536xxxxxxx"             # Kendi telefon numaran (Sibel)

def send_real_sms(message_body):
    try:
        # Eğer bilgiler girilmediyse hata vermesin, loglayıp geçsin (Demo modu)
        if "your_auth" in AUTH_TOKEN:
            print("⚠️ Twilio bilgileri eksik. SMS simülasyon modunda.")
            return False

        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_NUMBER,
            to=MY_PHONE_NUMBER
        )
        print(f"✅ SMS Gönderildi! ID: {message.sid}")
        return True
    except Exception as e:
        print(f"❌ SMS Hatası: {e}")
        return False