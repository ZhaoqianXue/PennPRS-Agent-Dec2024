import requests
import threading
import time
import uuid

BASE_URL = "http://localhost:8000"

def poll_progress(request_id):
    print(f"Starting poller for {request_id}...")
    for _ in range(20): # Poll for 10 seconds
        try:
            resp = requests.get(f"{BASE_URL}/agent/search_progress/{request_id}")
            data = resp.json()
            print(f"[Poller] Status: {data.get('status')} | Fetched: {data.get('fetched')}/{data.get('total')}")
            if data.get('status') == 'completed':
                print("[Poller] Completed!")
                return
        except Exception as e:
            print(f"[Poller] Error: {e}")
        time.sleep(0.5)

def trigger_search(request_id):
    print(f"Triggering search for {request_id}...")
    try:
        resp = requests.post(f"{BASE_URL}/agent/invoke", json={
            "message": "Type 2 diabetes",
            "request_id": request_id
        })
        print(f"[Trigger] Search finished with status: {resp.status_code}")
    except Exception as e:
        print(f"[Trigger] Error: {e}")

def main():
    request_id = str(uuid.uuid4())
    
    # Start poller in background
    poller = threading.Thread(target=poll_progress, args=(request_id,))
    poller.start()
    
    # Trigger search in main thread
    trigger_search(request_id)
    
    poller.join()

if __name__ == "__main__":
    main()
