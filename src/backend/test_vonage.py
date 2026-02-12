from sms_sender import send_sms
import os
from dotenv import load_dotenv

def test_manual_sms():
    load_dotenv()
    print("Starting Vonage SMS test...")
    
    # Use the number verified in previous steps
    target_number = "905366251652" # Vonage format often prefers no +
    message = "NetPulse Test SMS: Vonage entegrasyonu basarili."
    
    print(f"Target: {target_number}")
    print(f"Message: {message}")
    
    try:
        success, response = send_sms(target_number, message)
        
        if success:
            print(f"SUCCESS: {response}")
        else:
            print(f"FAILED: {response}")
            
    except Exception as e:
        print(f"CRASH: {e}")

if __name__ == "__main__":
    test_manual_sms()
