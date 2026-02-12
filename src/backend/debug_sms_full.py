import vonage
from vonage_sms import requests as sms_requests
import os
from dotenv import load_dotenv
import logging

# Load .env file explicitly
load_dotenv()

# Configure Logging to print EVERYTHING
logging.basicConfig(level=logging.DEBUG)

def debug_sms():
    print("--- STARTING VERBOSE SMS DEBUG ---")
    
    key = os.getenv("VONAGE_API_KEY")
    secret = os.getenv("VONAGE_API_SECRET")
    brand = os.getenv("VONAGE_BRAND_NAME", "NetPulse")
    
    print(f"API Key: {key[:4]}****")
    print(f"Brand: {brand}")
    
    client = vonage.Vonage(vonage.Auth(api_key=key, api_secret=secret))
    
    # Target Number (hardcoded to verify)
    target = "905366251652" 
    print(f"Target: {target}")
    
    try:
        print("Sending request...")
        message_payload = sms_requests.SmsMessage(
            to=target,
            from_=brand,
            text="NetPulse Debug: Lutfen bu mesaji onaylayin."
        )
        response = client.sms.send(message_payload)
        
        print("\n--- RAW RESPONSE OBJECT ---")
        print(response)
        
        print("\n--- MESSAGES ARRAY ---")
        for i, msg in enumerate(response.messages):
            print(f"Message {i}:")
            print(f"  Status: {msg.status}")
            print(f"  Message ID: {msg.message_id}")
            print(f"  To: {msg.to}")
            print(f"  Remaining Balance: {msg.remaining_balance}")
            print(f"  Message Price: {msg.message_price}")
            print(f"  Network: {msg.network}")
            
            if msg.status != "0":
                print(f"  ERROR TEXT: {msg.error_text}")
                
    except Exception as e:
        print(f"CRASH: {e}")

if __name__ == "__main__":
    debug_sms()
