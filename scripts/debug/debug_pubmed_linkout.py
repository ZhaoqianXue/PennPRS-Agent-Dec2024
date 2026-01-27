import httpx
import json
import os
from pathlib import Path

def get_pubmed_linkout(pmid: str):
    print(f"--- Investigating LinkOut for PMID: {pmid} ---")
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    params = {
        "dbfrom": "pubmed",
        "id": pmid,
        "cmd": "llinks",
        "retmode": "xml",
    }
    
    try:
        response = httpx.get(f"{base_url}/elink.fcgi", params=params)
        xml_text = response.text
        
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml_text)
        
        obj_urls = root.findall(".//ObjUrl")
        print(f"✅ Found {len(obj_urls)} ObjUrl elements in XML.")
        
        full_text_urls = []
        for obj in obj_urls:
            url_elem = obj.find("Url")
            url = url_elem.text if url_elem is not None else ""
            
            provider = obj.find(".//Provider/Name")
            provider_name = provider.text if provider is not None else "Unknown"
            
            categories = [cat.text for cat in obj.findall(".//Category")]
            
            print(f"   - Provider: {provider_name}")
            print(f"     URL: {url}")
            print(f"     Categories: {categories}")
            
            if any("Full Text" in cat for cat in categories):
                full_text_urls.append({
                    "name": provider_name,
                    "url": url
                })
        
        return full_text_urls

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def construct_upenn_proxy_url(original_url: str):
    proxy_prefix = "https://proxy.library.upenn.edu/login?url="
    return f"{proxy_prefix}{original_url}"

if __name__ == "__main__":
    # Test with Jansen 2019 (Nature Genetics) - Non-OA
    pmid = "30617256"
    links = get_pubmed_linkout(pmid)
    
    if links:
        print("\n--- Proposed UPenn Proxy URLs ---")
        for link in links:
            proxied = construct_upenn_proxy_url(link['url'])
            print(f"Target: {link['name']}")
            print(f"Proxied URL: {proxied}")
            print("-" * 30)
