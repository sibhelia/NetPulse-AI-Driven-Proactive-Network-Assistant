try:
    import vonage_sms
    from vonage_sms import responses
    print("vonage_sms.responses dir:", dir(responses))
    
    if hasattr(responses, 'SmsResponse'):
        print("responses.SmsResponse FOUND")
        import inspect
        print("SmsResponse sig:", inspect.signature(responses.SmsResponse.__init__))
        # properties?
        # print("SmsResponse members:", dir(responses.SmsResponse))
        
except ImportError as e:
    print(f"Import failed: {e}")
except Exception as e:
    print(f"Error: {e}")
