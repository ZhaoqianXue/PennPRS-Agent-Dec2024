
import requests
import json

def dump_gene_json():
    gene_id = "ENSG00000108821"
    url = f"https://rest.omicspred.org/api/gene/{gene_id}"
    print(f"Fetching {url}...")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2)[:2000]) # Print first 2000 chars
            
            # Check keys
            print(f"\nKeys: {list(data.keys())}")
            if "scores" in data:
                print(f"Scores count: {len(data['scores'])}")
            if "associated_scores" in data:
                print(f"Associated Scores count: {len(data['associated_scores'])}")
        else:
            print(f"Status: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    dump_gene_json()
