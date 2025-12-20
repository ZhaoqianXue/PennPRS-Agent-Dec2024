
import requests
import json

BASE_URL = "https://www.pgscatalog.org/rest"

def test_pagination():
    print("--- Testing Pagination ---")
    url = f"{BASE_URL}/score/all"
    params = {"limit": 5}
    resp = requests.get(url, params=params)
    data = resp.json()
    print(f"Count: {data.get('count')}")
    print(f"Next: {data.get('next')}")
    print(f"Results in page: {len(data.get('results'))}")

def test_parameter_filtering():
    print("\n--- Testing Direct Parameter Filtering ---")
    # Try common Django-style filters often used in such APIs
    candidates = [
        {"trait_reported": "Alzheimer"},
        {"trait_reported__icontains": "Alzheimer"},
        {"search": "Alzheimer"},
        {"q": "Alzheimer"}
    ]
    
    url = f"{BASE_URL}/score/all"
    
    for params in candidates:
        print(f"Testing params: {params}")
        resp = requests.get(url, params=params)
        data = resp.json()
        count = data.get('count') # Total count matching query?
        results = data.get('results', [])
        
        # Check if list is filtered
        if count and count < 4000: # Assuming total DB is large, filtered should be small
            print(f"-> SUCCESS? Count: {count}")
            for r in results[:3]:
                print(f"   - {r.get('id')}: {r.get('trait_reported')}")
        else:
            print(f"-> Failed (Count: {count})")

if __name__ == "__main__":
    test_pagination()
    test_parameter_filtering()
