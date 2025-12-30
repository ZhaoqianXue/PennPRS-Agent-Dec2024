print("Starting simple test...")
import requests
print("requests imported")
import time
print("time imported")

print("Testing API call...")
try:
    response = requests.get("https://rest.omicspred.org/api/score/all/?limit=1", timeout=10)
    print(f"API call successful: {response.status_code}")
except Exception as e:
    print(f"API call failed: {e}")

print("Test completed!")
