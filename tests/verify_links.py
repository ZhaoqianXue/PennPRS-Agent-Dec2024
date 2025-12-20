
import sys
import os
import requests
import concurrent.futures

# Add src to path
sys.path.append(os.getcwd())

from src.core.pgs_catalog_client import PGSCatalogClient
from src.core.pennprs_client import PennPRSClient

def check_url(url, description):
    if not url:
        print(f"[-] {description}: MISSING URL")
        return False
    
    if url.startswith("ftp://"):
        print(f"[?] {description}: FTP Link (Cannot verify with requests, assume browser handles): {url}")
        return True

    try:
        # Use simple get with stream=True to avoid downloading large files
        # Increased timeout for PennPRS
        resp = requests.get(url, stream=True, timeout=60, verify=False)
        if resp.status_code < 400:
            print(f"[+] {description}: OK ({resp.status_code}) - {url}")
            return True
        else:
            print(f"[!] {description}: BROKEN ({resp.status_code}) - {url}")
            return False
    except Exception as e:
        print(f"[!] {description}: ERROR ({str(e)}) - {url}")
        return False

def main():
    print("Initializing Clients...")
    pgs_client = PGSCatalogClient()
    penn_client = PennPRSClient()
    
    trait = "Alzheimer's"
    print(f"Searching for '{trait}'...")
    
    # 1. PGS Catalog
    pgs_results = pgs_client.search_scores(trait)
    print(f"Found {len(pgs_results)} PGS models.")
    
    # Check first 5 PGS models
    for res in pgs_results[:5]:
        pid = res.get('id')
        name = res.get('name')
        dl_url = res.get('ftp_scoring_file')
        
        print(f"\nChecking PGS Model {pid} ({name}):")
        check_url(dl_url, f"Download URL")
        
        # Check details for publication link
        try:
            details = pgs_client.get_score_details(pid)
            pub = details.get("publication", {})
            doi = pub.get("doi")
            if doi:
                # DOI is often just "10.1038/..." not a full URL.
                # Check if it needs https://doi.org/ prefix
                if not doi.startswith("http"):
                    doi_url = f"https://doi.org/{doi}"
                else:
                    doi_url = doi
                check_url(doi_url, "Publication DOI")
        except Exception as e:
            print(f"Error fetching details for {pid}: {e}")

    # 2. PennPRS Public
    penn_results = penn_client.search_public_results(trait)
    print(f"\nFound {len(penn_results)} PennPRS models.")
    
    for res in penn_results[:5]:
        sid = res.get('study_id')
        name = res.get('name')
        dl_url = res.get("download_link")
        
        print(f"\nChecking PennPRS Model {sid} ({name}):")
        check_url(dl_url, "Download Link")
        
        # Check Deep Fetch URL (Functional check)
        # We won't download the zip, just check HEAD
        deep_url = f"https://pennprs.org/api/download_result?filename={sid}"
        check_url(deep_url, "Deep Fetch API")

if __name__ == "__main__":
    main()
