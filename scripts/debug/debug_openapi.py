import requests
import sys

BASE_URL = "http://localhost:8000"

print("Fetching OpenAPI schema...")
try:
    r = requests.get(f"{BASE_URL}/openapi.json")
    r.raise_for_status()
    schema = r.json()
    paths = list(schema.get("paths", {}).keys())
    print(f"Found {len(paths)} paths.")
    
    deep_paths = [p for p in paths if "deep-research" in p]
    print("\nDeep Research Paths found in schema:")
    for p in deep_paths:
        print(f"  - {p}")
        
    if not deep_paths:
        print("\n❌ CRITICAL: Deep Research paths NOT found in OpenAPI schema!")
    else:
        print("\n✅ Paths exist in schema. 404 is likely due to inner error or method mismatch.")
        
except Exception as e:
    print(f"Failed to fetch schema: {e}")
