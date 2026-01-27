#!/usr/bin/env python3
"""
Test PMC Full-Text Heritability Extraction

This script:
1. Searches Europe PMC for Open Access papers on heritability + Alzheimer's
2. Downloads their full text via Europe PMC API
3. Tests the HeritabilityExtractor on each paper
4. Reports extraction results

Usage:
    python scripts/test_pmc_heritability_extraction.py
"""

import os
import sys
import json
import time
import logging
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add project root to path
# Add project root to path
# Script is in scripts/testing/, so root is ../../..
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(project_root / ".env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Europe PMC API Client
# ============================================================================

class EuropePMCClient:
    """Client for Europe PMC API to fetch Open Access full-text articles."""
    
    BASE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "PennPRS-Agent/1.0 (Research; mailto:your-email@upenn.edu)"
        })
    
    def search_oa_papers(
        self, 
        query: str, 
        max_results: int = 10,
        has_fulltext: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search for Open Access papers with full text available.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            has_fulltext: Only return papers with full text available
            
        Returns:
            List of paper metadata dicts
        """
        # Add Open Access filter
        full_query = f"({query}) AND (OPEN_ACCESS:y)"
        if has_fulltext:
            full_query += " AND (HAS_FT:y)"
        
        params = {
            "query": full_query,
            "resultType": "core",
            "pageSize": max_results,
            "format": "json"
        }
        
        url = f"{self.BASE_URL}/search"
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            results = data.get("resultList", {}).get("result", [])
            logger.info(f"Found {len(results)} Open Access papers for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def get_full_text_xml(self, pmcid: str) -> Optional[str]:
        """
        Fetch full-text XML for a PMC article.
        
        Args:
            pmcid: PMC ID (e.g., "PMC1234567")
            
        Returns:
            Full-text XML string or None if not available
        """
        # Ensure PMC prefix
        if not pmcid.startswith("PMC"):
            pmcid = f"PMC{pmcid}"
        
        url = f"{self.BASE_URL}/{pmcid}/fullTextXML"
        
        try:
            response = self.session.get(url, timeout=60)
            
            if response.status_code == 200:
                return response.text
            else:
                logger.warning(f"Full text not available for {pmcid}: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching full text for {pmcid}: {e}")
            return None
    
    def extract_text_from_xml(self, xml_content: str) -> str:
        """
        Extract plain text content from PMC XML.
        
        Args:
            xml_content: Full PMC XML string
            
        Returns:
            Plain text extracted from the article
        """
        import re
        from xml.etree import ElementTree as ET
        
        try:
            # Parse XML
            root = ET.fromstring(xml_content)
            
            # Extract text from body sections
            text_parts = []
            
            # Get article title
            title_elem = root.find(".//article-title")
            if title_elem is not None:
                title_text = "".join(title_elem.itertext())
                text_parts.append(f"TITLE: {title_text}\n")
            
            # Get abstract
            abstract = root.find(".//abstract")
            if abstract is not None:
                abstract_text = " ".join(abstract.itertext())
                text_parts.append(f"ABSTRACT: {abstract_text}\n")
            
            # Get body text
            body = root.find(".//body")
            if body is not None:
                for section in body.findall(".//sec"):
                    # Get section title
                    sec_title = section.find("title")
                    if sec_title is not None:
                        text_parts.append(f"\n## {sec_title.text}\n")
                    
                    # Get paragraphs
                    for p in section.findall(".//p"):
                        p_text = " ".join(p.itertext())
                        text_parts.append(p_text + "\n")
            
            # Join and clean
            full_text = "\n".join(text_parts)
            full_text = re.sub(r'\s+', ' ', full_text)  # Normalize whitespace
            full_text = re.sub(r'\n\s*\n', '\n\n', full_text)  # Normalize paragraphs
            
            return full_text.strip()
            
        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
            # Fallback: extract text via regex
            text = re.sub(r'<[^>]+>', ' ', xml_content)
            text = re.sub(r'\s+', ' ', text)
            return text[:50000]  # Limit length


def fetch_alzheimer_heritability_papers(n_papers: int = 5) -> List[Dict]:
    """
    Fetch Open Access papers about Alzheimer's and heritability from Europe PMC.
    """
    client = EuropePMCClient()
    
    # Search query for heritability + Alzheimer's
    query = '(heritability OR "SNP heritability" OR "h2" OR "LDSC") AND (Alzheimer OR "Alzheimer\'s disease" OR AD)'
    
    papers = client.search_oa_papers(query, max_results=n_papers * 2)  # Get extra in case some fail
    
    result = []
    for paper in papers:
        if len(result) >= n_papers:
            break
            
        pmcid = paper.get("pmcid")
        if not pmcid:
            continue
        
        logger.info(f"Fetching full text for {pmcid}...")
        xml_content = client.get_full_text_xml(pmcid)
        
        if xml_content:
            full_text = client.extract_text_from_xml(xml_content)
            
            # Filter out short papers (e.g. posters/abstracts only)
            if len(full_text) > 5000:
                result.append({
                    "pmid": paper.get("pmid", ""),
                    "pmcid": pmcid,
                    "title": paper.get("title", ""),
                    "journal": paper.get("journalTitle", ""),
                    "year": paper.get("pubYear", ""),
                    "authors": paper.get("authorString", ""),
                    "abstract": paper.get("abstractText", ""),
                    "full_text": full_text,
                    "full_text_length": len(full_text)
                })
                logger.info(f"  ✓ Got {len(full_text):,} chars of full text")
            else:
                logger.warning(f"  ✗ Full text too short ({len(full_text)} chars) - Skipping")
        
        time.sleep(0.5)  # Rate limiting
    
    return result


def test_heritability_extraction(papers: List[Dict]) -> Dict:
    """
    Run HeritabilityExtractor on the fetched papers.
    """
    from src.modules.literature.entities import PaperMetadata
    from src.modules.literature.information_extractor import HeritabilityExtractor
    
    extractor = HeritabilityExtractor()
    
    results = {
        "total_papers": len(papers),
        "successful_extractions": 0,
        "failed_extractions": 0,
        "total_estimates": 0,
        "extractions": []
    }
    
    for i, paper in enumerate(papers, 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"Paper {i}/{len(papers)}: {paper['title'][:80]}...")
        logger.info(f"PMID: {paper['pmid']}, PMCID: {paper['pmcid']}")
        logger.info(f"Full text length: {paper['full_text_length']:,} chars")
        
        # Create PaperMetadata with full_text
        paper_metadata = PaperMetadata(
            pmid=paper['pmid'] or paper['pmcid'],
            title=paper['title'],
            abstract=paper.get('abstract', ''),
            full_text=paper['full_text'],
            journal=paper.get('journal', ''),
            publication_date=None
        )
        
        try:
            extractions = extractor.extract(paper_metadata)
            
            if extractions:
                results["successful_extractions"] += 1
                results["total_estimates"] += len(extractions)
                
                paper_result = {
                    "pmid": paper['pmid'],
                    "pmcid": paper['pmcid'],
                    "title": paper['title'],
                    "num_extractions": len(extractions),
                    "extractions": []
                }
                
                for ext in extractions:
                    ext_dict = {
                        "id": ext.id,
                        "trait": ext.trait,
                        "trait_efo": ext.trait_efo,
                        "h2": ext.h2,
                        "se": ext.se,
                        "scale": ext.scale,
                        "p_value": ext.p_value,
                        "z_score": ext.z_score,
                        "method": ext.method.value if ext.method else None,
                        "method_detail": ext.method_detail,
                        "intercept": ext.intercept,
                        "lambda_gc": ext.lambda_gc,
                        "sample_size": ext.sample_size,
                        "ancestry": ext.ancestry,
                        "prevalence": ext.prevalence,
                        "publication": ext.publication,
                        "publication_year": ext.publication_year,
                        "confidence": ext.extraction_confidence,
                        "source_text": ext.raw_text_snippet[:200] if ext.raw_text_snippet else "",
                        "evidence_html": ext.evidence_html  # Check if this is populated
                    }
                    paper_result["extractions"].append(ext_dict)
                    
                    logger.info(f"  ✓ Extracted: {ext.trait}")
                    logger.info(f"    - h²: {ext.h2} (SE: {ext.se}, p: {ext.p_value})")
                    logger.info(f"    - Method: {ext.method}, Scale: {ext.scale}")
                    logger.info(f"    - Pop: N={ext.sample_size}, Ancestry={ext.ancestry}")
                    logger.info(f"    - QC: Intercept={ext.intercept}, LambdaGC={ext.lambda_gc}")
                    logger.info(f"    - Evidence HTML present: {bool(ext.evidence_html)}")
                
                results["extractions"].append(paper_result)
            else:
                results["failed_extractions"] += 1
                logger.warning(f"  ✗ No heritability estimates extracted")
                
        except Exception as e:
            results["failed_extractions"] += 1
            logger.error(f"  ✗ Extraction error: {e}")
        
        # Small delay between papers
        time.sleep(1)
    
    return results


def main():
    """Main function to run the PMC heritability extraction test."""
    
    print("\n" + "="*70)
    print("PMC Full-Text Heritability Extraction Test")
    print("="*70 + "\n")
    
    # Step 1: Fetch papers
    print("Step 1: Fetching Open Access papers from Europe PMC...")
    print("Query: heritability + Alzheimer's disease")
    print("-"*50)
    
    papers = fetch_alzheimer_heritability_papers(n_papers=5)
    
    if not papers:
        print("ERROR: No papers found. Check your internet connection.")
        return
    
    print(f"\n✓ Successfully fetched {len(papers)} papers with full text\n")
    
    # List papers
    for i, p in enumerate(papers, 1):
        print(f"{i}. [{p['pmcid']}] {p['title'][:70]}...")
        print(f"   {p['journal']}, {p['year']} | Full text: {p['full_text_length']:,} chars")
    
    # Step 2: Run extraction
    print("\n" + "-"*50)
    print("Step 2: Running HeritabilityExtractor on papers...")
    print("-"*50)
    
    results = test_heritability_extraction(papers)
    
    # Step 3: Summary
    print("\n" + "="*70)
    print("EXTRACTION RESULTS SUMMARY")
    print("="*70)
    
    print(f"\nTotal Papers Processed: {results['total_papers']}")
    print(f"Papers with Extractions: {results['successful_extractions']}")
    print(f"Papers without Extractions: {results['failed_extractions']}")
    print(f"Total h² Estimates Extracted: {results['total_estimates']}")
    
    if results['total_estimates'] > 0:
        print(f"\nSuccess Rate: {results['successful_extractions']/results['total_papers']*100:.1f}%")
        print(f"Avg Estimates per Paper: {results['total_estimates']/max(results['successful_extractions'],1):.1f}")
    
    # Detailed results
    if results['extractions']:
        print("\n" + "-"*50)
        print("DETAILED EXTRACTIONS:")
        print("-"*50)
        
        for paper in results['extractions']:
            print(f"\n{paper['pmcid']}: {paper['title'][:60]}...")
            for ext in paper['extractions']:
                print(f"  • [ID: {ext.get('id')}] Trait: {ext['trait']}")
                print(f"    h² = {ext['h2']} (SE={ext['se']}, p={ext['p_value']}, z={ext['z_score']})")
                print(f"    Method: {ext['method']} ({ext['method_detail']}), Scale: {ext['scale']}")
                print(f"    QC: Intercept={ext['intercept']}, LambdaGC={ext['lambda_gc']}")
                print(f"    Pop: N={ext['sample_size']}, Ancestry={ext['ancestry']}, Prev={ext['prevalence']}")
                print(f"    Pub: {ext['publication']} ({ext['publication_year']})")
                print(f"    Confidence: {ext['confidence']}")
                print(f"    Evidence HTML: {'✓ Present' if ext['evidence_html'] else '✗ Missing'}")
                if ext['evidence_html']:
                    print(f"    (HTML snippet length: {len(ext['evidence_html'])})")
    
    # Save results
    output_dir = project_root / "data" / "test_results"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"pmc_heritability_extraction_test_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n✓ Results saved to: {output_file}")


if __name__ == "__main__":
    main()
