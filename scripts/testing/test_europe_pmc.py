import httpx
import sys

def test_europe_pmc(id_value: str):
    print(f"\n--- Testing Europe PMC for ID: {id_value} ---")
    search_url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=ext_id:{id_value}&format=json"
    
    try:
        response = httpx.get(search_url)
        data = response.json()
        results = data.get("resultList", {}).get("result", [])
        
        if not results:
            print(f"❌ Europe PMC search found nothing for {id_value}")
            return
            
        paper = results[0]
        pmcid = paper.get('pmcid')
        print(f"✅ Found paper: {paper.get('title')}")
        print(f"   Journal: {paper.get('journalTitle')}")
        print(f"   Open Access: {paper.get('isOpenAccess')}")
        print(f"   PMCID: {pmcid}")
        print(f"   hasFullTextXML: {paper.get('hasFullTextXML')}")
        print(f"   hasTDM: {paper.get('hasTDM')}") # Text Data Mining eligibility
        print(f"   hasTextMinedTerms: {paper.get('hasTextMinedTerms')}")
        
        target_id = pmcid if pmcid else id_value

        # Try Full Text XML
        fulltext_url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{target_id}/fullTextXML"
        print(f"Fetching full-text from: {fulltext_url}")
        
        ft_response = httpx.get(fulltext_url)
        if ft_response.status_code == 200:
            xml_text = ft_response.text
            if "<body>" in xml_text or "<body" in xml_text:
                print(f"✅ Successfully retrieved Full-Text XML.")
                start = xml_text.find("<body")
                print(f"Body snippet: {xml_text[start:start+300]}...")
            else:
                print(f"⚠️ XML retrieved but NO <body>. Length: {len(xml_text)}")
        else:
            print(f"❌ Full-text fetch failed (Status {ft_response.status_code})")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    pmids = [
        "34301930", # OA - Nature Communications (2021)
        "32709849", # OA - Nature Communications (2020)
        "30617256", # Non-OA - Nature Genetics (2019)
        "24162737", # Non-OA - Nature Genetics (2013)
        "30820047", # Non-OA - Nature Genetics (2019)
        "26117565", # Non-OA - Epidemiology (2015)
    ]
    for pmid in pmids:
        test_europe_pmc(pmid)
