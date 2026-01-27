import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.pgs_catalog_client import PGSCatalogClient

def debug_api():
    base_url = "https://www.pgscatalog.org/rest"
    endpoints = [
        f"{base_url}/score/all?search=Alzheimer",
        f"{base_url}/score/all?trait=Alzheimer",
        f"{base_url}/score/all?q=Alzheimer"
    ]
    
    for url in endpoints:
        print(f"\nQuerying {url}...")
        try:
            r = requests.get(url, timeout=10)
            print(f"Status: {r.status_code}")
            print(f"Content-Type: {r.headers.get('Content-Type')}")
            # Print first 500 chars
            print(f"Body: {r.text[:500]}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    debug_api()
