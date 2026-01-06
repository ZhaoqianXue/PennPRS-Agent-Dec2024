import requests
import uuid
import json

BASE_URL = "http://localhost:8000"

def test_search_response():
    request_id = str(uuid.uuid4())
    print(f"Triggering search for {request_id}...")
    
    try:
        # Short timeout might not be enough for real search, but we just want to see structure
        # actually, for T2D it takes ~30s. We need to wait.
        resp = requests.post(f"{BASE_URL}/agent/invoke", json={
            "message": "Type 2 diabetes",
            "request_id": request_id
        }, timeout=60)
        
        if resp.status_code == 200:
            data = resp.json()
            print("Response Keys:", data.keys())
            
            full_state = data.get("full_state", {})
            print("Full State Keys:", full_state.keys())
            
            sr = full_state.get("structured_response")
            if sr:
                print("Structured Response Type:", sr.get("type"))
                print("Models Found:", len(sr.get("models", [])))
            else:
                print("EROR: structured_response is MISSING in full_state")
                
        else:
            print(f"Error: HTTP {resp.status_code}")
            print(resp.text)

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_search_response()
