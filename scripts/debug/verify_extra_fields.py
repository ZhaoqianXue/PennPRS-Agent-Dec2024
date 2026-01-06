
import sys
import os
import json
sys.path.append(os.getcwd())

from src.core.pennprs_client import PennPRSClient
from src.core.pgs_catalog_client import PGSCatalogClient

# Disable SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def verify_extra_fields():
    print("=== Verifying PGS Catalog Extra Fields ===")
    pgs_client = PGSCatalogClient()
    # Using a known detailed model
    details = pgs_client.get_score_details("PGS000004") 
    print(f"ID: {details.get('id')}")
    print(f"License: {details.get('license')}")
    print(f"Trait Detailed: {details.get('trait_detailed')}")
    print(f"EFO: {details.get('trait_efo')}")
    print(f"Covariates: {details.get('covariates')}")
    print(f"Performance Comments: {details.get('performance_comments')}")
    
    print("\n=== Verifying PennPRS Extra Fields ===")
    penn_client = PennPRSClient()
    results = penn_client.search_public_results("alzheimer")
    if results:
        first = results[0]
        print(f"ID: {first.get('id')}")
        print(f"Study ID: {first.get('study_id')}")
        print(f"Trait Type: {first.get('trait_type')}")
        print(f"Submission Date: {first.get('submission_date')}")
        print(f"Source: {first.get('source')}")
    else:
        print("No PennPRS results found.")

if __name__ == "__main__":
    verify_extra_fields()
