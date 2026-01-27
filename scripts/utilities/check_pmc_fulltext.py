import os
import sys
from pathlib import Path
import httpx
import xml.etree.ElementTree as ET

# Add project root to path
project_root = Path(__file__).parent.parent.absolute()
sys.path.append(str(project_root))

from src.modules.literature.pubmed import PubMedClient

def check_fulltext_access(pmid: str):
    client = PubMedClient()
    
    # 1. Try to find PMC ID from PMID using ELink
    print(f"Checking full-text access for PMID: {pmid}")
    
    # Simple ELink request to get PMC ID
    # https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&db=pmc&id=12790938&retmode=json
    params = {
        "dbfrom": "pubmed",
        "db": "pmc",
        "id": pmid,
        "retmode": "json",
    }
    
    try:
        response = httpx.get(f"{client.BASE_URL}/elink.fcgi", params=params)
        data = response.json()
        
        links = data.get("linksets", [{}])[0].get("linksetdb", [])
        pmcid = None
        for link in links:
            if link.get("dbto") == "pmc":
                pmcid = link.get("links", [None])[0]
                break
        
        if not pmcid:
            print(f"❌ No PMC ID found for PMID {pmid}. This paper might not be in Open Access PMC.")
            return
        
        print(f"✅ Found PMC ID: PMC{pmcid}")
        
        # 2. Try to fetch full text using EFetch with db=pmc
        # https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=PMC1234567&retmode=xml
        params = {
            "db": "pmc",
            "id": f"PMC{pmcid}",
            "retmode": "xml"
        }
        
        response = httpx.get(f"{client.BASE_URL}/efetch.fcgi", params=params)
        if response.status_code == 200:
            xml_text = response.text
            # Basic check if it contains body text
            if "<body>" in xml_text:
                print(f"✅ Successfully retrieved XML containing full-text body.")
                # Snippet of body
                start = xml_text.find("<body>")
                end = xml_text.find("</body>") + 7
                print(f"Body snippet: {xml_text[start:start+200]}...")
            else:
                print(f"⚠️ Retrieved XML but no <body> tag found. It might be abstract-only in PMC.")
        else:
            print(f"❌ Failed to fetch from PMC. Status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Test with PMID 12790938 (which we found earlier)
    check_fulltext_access("12790938")
