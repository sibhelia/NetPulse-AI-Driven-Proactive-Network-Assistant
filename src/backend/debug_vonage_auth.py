import vonage
import inspect

try:
    print("vonage.Auth:", vonage.Auth)
    sig = inspect.signature(vonage.Auth.__init__)
    print("vonage.Auth sig:", sig)
except AttributeError:
    print("vonage.Auth not found")
    # Try searching in dir
    for item in dir(vonage):
        if 'Auth' in item:
            print(f"Found {item} in vonage")
except Exception as e:
    print(f"Error: {e}")
