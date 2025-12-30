import requests
import json

opgs_id = "OPGS000890"
perf_url = f"https://rest-private-dot-sl925-phpc-1.nw.r.appspot.com/api/performance/search?opgs_id={opgs_id}"
resp = requests.get(perf_url)
if resp.status_code == 200:
    data = resp.json()
    results = data.get('results', [])
    if results:
        print(json.dumps(results[0], indent=2))
    else:
        print("No results found in API")
else:
    print(f"API Error: {resp.status_code}")
