"""
PubMed E-utilities Client

Provides access to PubMed/NCBI databases via the E-utilities API.
Used by the Supervisor agent to:
1. Search for relevant papers by disease/trait
2. Retrieve paper metadata (title, abstract, authors, etc.)
3. Fetch full-text links where available

API Documentation: https://www.ncbi.nlm.nih.gov/books/NBK25500/
"""

import os
import time
import logging
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from .entities import PaperMetadata

logger = logging.getLogger(__name__)


@dataclass
class PubMedSearchResult:
    """Result from a PubMed search."""
    query: str
    total_count: int
    pmids: List[str]
    search_time: float


class PubMedClient:
    """
    Client for PubMed E-utilities API.
    
    Implements:
    - ESearch: Search for papers matching a query
    - EFetch: Retrieve detailed metadata for papers
    - ELink: Get related papers and full-text links
    
    Rate limiting: NCBI allows up to 3 requests/second without API key,
    or 10 requests/second with an API key.
    """
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        email: Optional[str] = None,
        tool_name: str = "PennPRS_Agent"
    ):
        """
        Initialize PubMed client.
        
        Args:
            api_key: NCBI API key (optional but recommended)
            email: Contact email (required by NCBI for tracking)
            tool_name: Application name for NCBI tracking
        """
        self.api_key = api_key or os.getenv("NCBI_API_KEY")
        self.email = email or os.getenv("NCBI_EMAIL", "pennprs@example.com")
        self.tool_name = tool_name
        
        # Rate limiting
        self._last_request_time = 0.0
        self._min_request_interval = 0.1 if self.api_key else 0.34  # seconds
        
        # HTTP client with timeouts
        self.client = httpx.Client(
            timeout=httpx.Timeout(30.0, connect=10.0),
            follow_redirects=True
        )
    
    def _rate_limit(self):
        """Ensure we don't exceed NCBI rate limits."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            time.sleep(self._min_request_interval - elapsed)
        self._last_request_time = time.time()
    
    def _build_params(self, **kwargs) -> Dict[str, str]:
        """Build request parameters with common fields."""
        params = {
            "tool": self.tool_name,
            "email": self.email,
            "retmode": "json",
        }
        if self.api_key:
            params["api_key"] = self.api_key
        params.update({k: v for k, v in kwargs.items() if v is not None})
        return params
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _request(self, endpoint: str, params: Dict[str, str]) -> Dict[str, Any]:
        """Make a rate-limited request to PubMed API."""
        self._rate_limit()
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from PubMed: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"Error fetching from PubMed: {e}")
            raise
    
    def _request_xml(self, endpoint: str, params: Dict[str, str]) -> str:
        """Make a request expecting XML response."""
        self._rate_limit()
        url = f"{self.BASE_URL}/{endpoint}"
        params["retmode"] = "xml"
        
        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error fetching XML from PubMed: {e}")
            raise
    
    # =========================================================================
    # Search Methods
    # =========================================================================
    
    def search(
        self,
        query: str,
        max_results: int = 100,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        sort: str = "relevance"
    ) -> PubMedSearchResult:
        """
        Search PubMed for papers matching a query.
        
        Args:
            query: Search query (supports PubMed advanced syntax)
            max_results: Maximum number of results to return
            date_from: Start date filter (YYYY/MM/DD format)
            date_to: End date filter (YYYY/MM/DD format)
            sort: Sort order ("relevance" or "date")
        
        Returns:
            PubMedSearchResult with list of PMIDs
        """
        start_time = time.time()
        
        params = self._build_params(
            db="pubmed",
            term=query,
            retmax=str(max_results),
            sort=sort,
            usehistory="n"
        )
        
        if date_from:
            params["mindate"] = date_from
        if date_to:
            params["maxdate"] = date_to
        if date_from or date_to:
            params["datetype"] = "pdat"  # Publication date
        
        data = self._request("esearch.fcgi", params)
        
        result = data.get("esearchresult", {})
        pmids = result.get("idlist", [])
        total_count = int(result.get("count", 0))
        
        search_time = time.time() - start_time
        
        logger.info(f"PubMed search '{query[:50]}...' found {total_count} papers, returning {len(pmids)}")
        
        return PubMedSearchResult(
            query=query,
            total_count=total_count,
            pmids=pmids,
            search_time=search_time
        )
    
    def search_prs_papers(
        self,
        disease: str,
        max_results: int = 100,
        years_back: int = 5
    ) -> PubMedSearchResult:
        """
        Search for PRS-related papers for a specific disease.
        
        Uses an optimized query combining disease terms with PRS-related terms.
        
        Args:
            disease: Disease/trait name (e.g., "Alzheimer's Disease")
            max_results: Maximum papers to return
            years_back: How many years back to search
        """
        # Build comprehensive PRS search query
        prs_terms = [
            "polygenic risk score",
            "polygenic score", 
            "genetic risk score",
            "PRS",
            "PGS",
            "genome-wide risk"
        ]
        prs_query = " OR ".join(f'"{term}"' for term in prs_terms)
        
        query = f'("{disease}"[Title/Abstract]) AND ({prs_query})'
        
        # Calculate date range
        from datetime import datetime, timedelta
        date_to = datetime.now().strftime("%Y/%m/%d")
        date_from = (datetime.now() - timedelta(days=365*years_back)).strftime("%Y/%m/%d")
        
        return self.search(
            query=query,
            max_results=max_results,
            date_from=date_from,
            date_to=date_to,
            sort="relevance"
        )
    
    def search_heritability_papers(
        self,
        disease: str,
        max_results: int = 100,
        years_back: int = 5
    ) -> PubMedSearchResult:
        """Search for heritability papers for a specific disease."""
        h2_terms = [
            "heritability",
            "h2",
            "SNP-heritability",
            "genetic variance",
            "LDSC",
            "LD score regression"
        ]
        h2_query = " OR ".join(f'"{term}"' for term in h2_terms)
        
        query = f'("{disease}"[Title/Abstract]) AND ({h2_query})'
        
        from datetime import datetime, timedelta
        date_to = datetime.now().strftime("%Y/%m/%d")
        date_from = (datetime.now() - timedelta(days=365*years_back)).strftime("%Y/%m/%d")
        
        return self.search(
            query=query,
            max_results=max_results,
            date_from=date_from,
            date_to=date_to
        )
    
    def search_genetic_correlation_papers(
        self,
        disease: str,
        max_results: int = 100,
        years_back: int = 5
    ) -> PubMedSearchResult:
        """Search for genetic correlation papers involving a specific disease."""
        rg_terms = [
            "genetic correlation",
            "rg",
            "LDSC",
            "cross-trait",
            "shared genetic",
            "pleiotropy"
        ]
        rg_query = " OR ".join(f'"{term}"' for term in rg_terms)
        
        query = f'("{disease}"[Title/Abstract]) AND ({rg_query})'
        
        from datetime import datetime, timedelta
        date_to = datetime.now().strftime("%Y/%m/%d")
        date_from = (datetime.now() - timedelta(days=365*years_back)).strftime("%Y/%m/%d")
        
        return self.search(
            query=query,
            max_results=max_results,
            date_from=date_from,
            date_to=date_to
        )
    
    # =========================================================================
    # Fetch Methods
    # =========================================================================
    
    def fetch_papers(self, pmids: List[str]) -> List[PaperMetadata]:
        """
        Fetch detailed metadata for a list of PMIDs.
        
        Args:
            pmids: List of PubMed IDs to fetch
        
        Returns:
            List of PaperMetadata objects
        """
        if not pmids:
            return []
        
        papers = []
        
        # EFetch has a limit, process in batches
        batch_size = 100
        for i in range(0, len(pmids), batch_size):
            batch = pmids[i:i+batch_size]
            batch_papers = self._fetch_batch(batch)
            papers.extend(batch_papers)
        
        return papers
    
    def _fetch_batch(self, pmids: List[str]) -> List[PaperMetadata]:
        """Fetch a batch of papers."""
        params = self._build_params(
            db="pubmed",
            id=",".join(pmids),
            rettype="abstract"
        )
        params["retmode"] = "xml"  # EFetch returns better data in XML
        
        xml_data = self._request_xml("efetch.fcgi", params)
        return self._parse_efetch_xml(xml_data)
    
    def _parse_efetch_xml(self, xml_data: str) -> List[PaperMetadata]:
        """Parse EFetch XML response into PaperMetadata objects."""
        import xml.etree.ElementTree as ET
        
        papers = []
        
        try:
            root = ET.fromstring(xml_data)
            
            for article in root.findall(".//PubmedArticle"):
                try:
                    paper = self._parse_article(article)
                    if paper:
                        papers.append(paper)
                except Exception as e:
                    logger.warning(f"Error parsing article: {e}")
                    continue
                    
        except ET.ParseError as e:
            logger.error(f"Error parsing PubMed XML: {e}")
        
        return papers
    
    def _parse_article(self, article) -> Optional[PaperMetadata]:
        """Parse a single PubmedArticle element."""
        medline = article.find(".//MedlineCitation")
        if medline is None:
            return None
        
        # PMID
        pmid_elem = medline.find(".//PMID")
        if pmid_elem is None:
            return None
        pmid = pmid_elem.text
        
        # Article info
        article_elem = medline.find(".//Article")
        if article_elem is None:
            return None
        
        # Title
        title_elem = article_elem.find(".//ArticleTitle")
        title = title_elem.text if title_elem is not None else ""
        
        # Abstract
        abstract_parts = []
        for abstract_text in article_elem.findall(".//AbstractText"):
            if abstract_text.text:
                label = abstract_text.get("Label", "")
                if label:
                    abstract_parts.append(f"{label}: {abstract_text.text}")
                else:
                    abstract_parts.append(abstract_text.text)
        abstract = " ".join(abstract_parts)
        
        # Authors
        authors = []
        for author in article_elem.findall(".//Author"):
            last_name = author.find("LastName")
            fore_name = author.find("ForeName")
            if last_name is not None:
                name = last_name.text
                if fore_name is not None:
                    name = f"{fore_name.text} {name}"
                authors.append(name)
        
        # Journal
        journal_elem = article_elem.find(".//Journal/Title")
        journal = journal_elem.text if journal_elem is not None else ""
        
        # Publication date
        pub_date = None
        date_elem = article_elem.find(".//PubDate")
        if date_elem is not None:
            year = date_elem.find("Year")
            month = date_elem.find("Month")
            day = date_elem.find("Day")
            
            if year is not None:
                try:
                    y = int(year.text)
                    m = self._parse_month(month.text) if month is not None else 1
                    d = int(day.text) if day is not None else 1
                    pub_date = date(y, m, d)
                except (ValueError, TypeError):
                    pass
        
        # DOI
        doi = None
        for eid in article_elem.findall(".//ELocationID"):
            if eid.get("EIdType") == "doi":
                doi = eid.text
                break
        
        # Keywords (MeSH terms)
        keywords = []
        for mesh in medline.findall(".//MeshHeading/DescriptorName"):
            if mesh.text:
                keywords.append(mesh.text)
        
        return PaperMetadata(
            pmid=pmid,
            title=title,
            abstract=abstract,
            authors=authors,
            journal=journal,
            publication_date=pub_date,
            doi=doi,
            keywords=keywords
        )
    
    def _parse_month(self, month_str: str) -> int:
        """Parse month string to integer (handles both numeric and text)."""
        if month_str.isdigit():
            return int(month_str)
        
        months = {
            "jan": 1, "feb": 2, "mar": 3, "apr": 4,
            "may": 5, "jun": 6, "jul": 7, "aug": 8,
            "sep": 9, "oct": 10, "nov": 11, "dec": 12
        }
        return months.get(month_str.lower()[:3], 1)
    
    # =========================================================================
    # Convenience Methods
    # =========================================================================
    
    def get_paper(self, pmid: str) -> Optional[PaperMetadata]:
        """Fetch a single paper by PMID."""
        papers = self.fetch_papers([pmid])
        return papers[0] if papers else None
    
    def search_and_fetch(
        self,
        query: str,
        max_results: int = 50
    ) -> List[PaperMetadata]:
        """
        Search for papers and immediately fetch their metadata.
        
        Convenience method combining search() and fetch_papers().
        """
        result = self.search(query, max_results=max_results)
        if not result.pmids:
            return []
        return self.fetch_papers(result.pmids)
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ============================================================================
# Query Builders
# ============================================================================

class PubMedQueryBuilder:
    """
    Helper class to build complex PubMed queries.
    
    Supports:
    - Boolean operators (AND, OR, NOT)
    - Field tags ([Title], [Abstract], [MeSH Terms], etc.)
    - Date ranges
    - Publication type filters
    """
    
    def __init__(self):
        self.parts = []
    
    def add_disease(self, disease: str) -> "PubMedQueryBuilder":
        """Add disease/trait term."""
        self.parts.append(f'("{disease}"[Title/Abstract])')
        return self
    
    def add_prs_terms(self) -> "PubMedQueryBuilder":
        """Add common PRS-related search terms."""
        terms = [
            '"polygenic risk score"',
            '"polygenic score"',
            '"genetic risk score"',
            'PRS[Title/Abstract]',
            'PGS[Title/Abstract]'
        ]
        self.parts.append(f"({' OR '.join(terms)})")
        return self
    
    def add_heritability_terms(self) -> "PubMedQueryBuilder":
        """Add heritability-related search terms."""
        terms = [
            '"heritability"',
            '"h2"[Title/Abstract]',
            '"SNP-heritability"',
            '"LDSC"[Title/Abstract]'
        ]
        self.parts.append(f"({' OR '.join(terms)})")
        return self
    
    def add_genetic_correlation_terms(self) -> "PubMedQueryBuilder":
        """Add genetic correlation-related search terms."""
        terms = [
            '"genetic correlation"',
            '"rg"[Title/Abstract]',
            '"cross-trait"',
            '"pleiotropy"'
        ]
        self.parts.append(f"({' OR '.join(terms)})")
        return self
    
    def add_custom(self, term: str) -> "PubMedQueryBuilder":
        """Add a custom search term."""
        self.parts.append(term)
        return self
    
    def build(self, operator: str = "AND") -> str:
        """Build the final query string."""
        return f" {operator} ".join(self.parts)
