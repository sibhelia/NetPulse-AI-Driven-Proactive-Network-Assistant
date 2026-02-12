import vonage
import inspect
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("VONAGE_API_KEY", "dummy")
secret = os.getenv("VONAGE_API_SECRET", "dummy")

try:
    auth = vonage.Auth(api_key=key, api_secret=secret)
    client = vonage.Vonage(auth)
    
    if hasattr(client.sms, 'send'):
        print("Inspecting client.sms.send:")
        try:
            sig = inspect.signature(client.sms.send)
            print(sig)
        except ValueError:
            print("Could not get signature (maybe built-in?)")
        
        print("\nDocstring:")
        print(client.sms.send.__doc__)
    else:
        print("client.sms.send not found")

except Exception as e:
    print(f"Error: {e}")
