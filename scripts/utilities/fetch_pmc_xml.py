import os
import sys
from pathlib import Path
import httpx

def fetch_pmc_fulltext(pmcid: str):
    print(f"Fetching full-text for PMC ID: {pmcid}")
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    params = {
        "db": "pmc",
        "id": pmcid,
        "retmode": "xml"
    }
    
    try:
        response = httpx.get(f"{base_url}/efetch.fcgi", params=params)
        if response.status_code == 200:
            xml_text = response.text
            if "<body>" in xml_text:
                print(f"✅ Successfully retrieved XML containing full-text body.")
                start = xml_text.find("<body>")
                print(f"Body snippet (first 500 chars): {xml_text[start:start+500]}...")
            else:
                print(f"⚠️ Retrieved XML but no <body> tag found. Full XML length: {len(xml_text)}")
                # Print first 200 chars to see what it is
                print(f"Start of XML: {xml_text[:200]}...")
        else:
            print(f"❌ Failed to fetch. Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Test with the PMCID we just found: 12790938
    fetch_pmc_fulltext("12790938")
