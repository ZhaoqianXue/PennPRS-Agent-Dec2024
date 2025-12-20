
import requests
import json
import logging

# Suppress warnings for verify=False
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def debug_pennprs():
    url = "https://pennprs.org/results_meta_data.json"
    print(f"Fetching {url}...")
    try:
        resp = requests.get(url, verify=False, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            print(f"Found {len(data)} items.")
            if data:
                print("--- First Item Keys ---")
                first = data[0]
                print(json.dumps(first, indent=2))
                
                # Check for metrics
                print("\nScan for metrics keywords in keys:")
                keys = first.keys()
                for k in keys:
                    if any(x in k.lower() for x in ['r2', 'auc', 'beta', 'pvalue', 'variant', 'snp']):
                        print(f"  - {k}: {first[k]}")
        else:
            print(f"Failed: {resp.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_pennprs()
