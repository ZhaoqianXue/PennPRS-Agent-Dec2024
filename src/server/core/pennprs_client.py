import os
import requests
import time
from typing import Optional, Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PennPRSClient:
    """
    Client for interacting with the PennPRS API.
    """
    BASE_URL = "https://pennprs.org/api"

    def __init__(self, email: Optional[str] = None):
        self.email = email or os.getenv("PENNPRS_EMAIL") or "zhaoqian.xue@pennmedicine.upenn.edu" # Updated default
        
    def add_single_job(
        self, 
        job_name: str, 
        job_type: str, 
        job_methods: List[str], 
        job_ensemble: bool, 
        traits_source: List[str], 
        traits_detail: List[str], 
        traits_type: List[str], 
        traits_name: List[str], 
        traits_population: List[str], 
        traits_col: List[Dict[str, Any]], 
        para_dict: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Submit a single job to PennPRS.
        """
        job_data = {
            "userEmail": self.email,
            "jobEmailOpt": True,
            "jobName": job_name,
            "jobType": job_type,
            "jobMethods": job_methods,
            "jobEnsemble": job_ensemble,
            "traitsSource": traits_source,
            "traitsDetail": traits_detail,
            "traitsType": traits_type,
            "traitsName": traits_name,
            "traitsPopulation": traits_population,
            "traitsCol": traits_col,
            "paraDict": para_dict or {}
        }
        
        url = f"{self.BASE_URL}/add_job"
        try:
            logger.info(f"Submitting job to {url}")
            # Note: verify=False is used in reference implementation, likely due to self-signed certs or similar.
            # We will keep it but it's a security risk in production.
            response = requests.post(url, json=job_data, verify=False)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error submitting job: {e}")
            return None

    def get_job_status(self, job_id: str) -> Optional[str]:
        """
        Get the status of a specific job.
        """
        url = f"{self.BASE_URL}/get_jobs"
        try:
            response = requests.get(url, params={"email": self.email}, verify=False, timeout=30)
            response.raise_for_status()
            jobs = response.json()
            
            for job in jobs:
                if job.get("id") == job_id:
                    return job.get("status")
            return None
        except Exception as e:
            logger.error(f"Error checking job status: {e}")
            return None

    def download_results(self, job_id: str, output_dir: str = "output") -> Optional[str]:
        """
        Download job results.
        """
        download_url = f"{self.BASE_URL}/download"
        filename_param = f"{self.email}={job_id}"
        
        try:
            logger.info(f"Downloading results for job {job_id}...")
            response = requests.get(download_url, params={"filename": filename_param}, verify=False, timeout=60)
            
            if response.status_code == 200:
                os.makedirs(output_dir, exist_ok=True)
                output_filename = os.path.join(output_dir, f"{job_id}.zip")
                with open(output_filename, 'wb') as f:
                    f.write(response.content)
                logger.info(f"Results saved to {output_filename}")
                return output_filename
            else:
                logger.error(f"Download failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error downloading results: {e}")
            return None
    def search_jobs(self, trait_query: str) -> List[Dict]:
        """
        Search for jobs associated with the user's email that match the trait query.
        """
        if not self.email:
            return []
            
        try:
            # Note: This searches user history, not public results.
            # verify=False due to PennPRS certificate issues
            url = f"{self.BASE_URL}/get_jobs?email={self.email}" # Changed self.base_url to self.BASE_URL
            response = requests.get(url, verify=False, timeout=10)
            
            if response.status_code == 200:
                jobs = response.json()
                # Filter by trait/name matching query
                matches = []
                query_lower = trait_query.lower()
                
                for job in jobs:
                    # Check job name or trait name if available
                    j_name = job.get('job_name', '').lower()
                    # Some jobs might store trait info in other fields, checking common ones
                    traits = job.get('traits_name', [])
                    if isinstance(traits, list):
                         traits_str = " ".join(traits).lower()
                    else:
                         traits_str = str(traits).lower()
                         
                    if query_lower in j_name or query_lower in traits_str:
                        matches.append({
                            "id": job.get("_id", {}).get("$oid", "unknown") if isinstance(job.get("_id"), dict) else job.get("_id", "unknown"),
                            "name": job.get("job_name"),
                            "status": job.get("status", "unknown"),
                             # Add more fields if needed
                        })
                return matches
            return []
        except Exception as e:
            logger.error(f"Error searching jobs: {e}") # Changed print to logger.error
            return []

    def search_public_results(self, trait_query: str) -> List[Dict]:
        """
        Search for public models in PennPRS (from pennprs.org/result).
        Fetches results_meta_data.json and filters by diseaseTrait.
        """
        try:
            # Verify=False due to PennPRS certificate
            url = "https://pennprs.org/results_meta_data.json"
            response = requests.get(url, verify=False, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                matches = []
                query_lower = trait_query.lower()
                
                for item in data:
                    trait = item.get("diseaseTrait", "").lower()
                    if query_lower in trait:
                        # Parse Sample Size
                        ss_str = item.get("sampleSize", "")
                        sample_size = 0
                        if ss_str:
                            # Extract first number "5,959 Finnish..." -> 5959
                            try:
                                import re
                                match = re.search(r'([\d,]+)', ss_str)
                                if match:
                                    sample_size = int(match.group(1).replace(",", ""))
                            except:
                                pass

                        # Parse Publication
                        pmid = item.get("pubmedId")
                        publication = None
                        if pmid:
                             publication = {
                                 "date": "Unknown",
                                 "citation": f"PubMed ID: {pmid}",
                                 "id": pmid,
                                 "doi": "" # DOI not provided
                             }

                        matches.append({
                            "id": item.get("studyId"),
                            "name": item.get("diseaseTrait"),
                            "pubmed_id": item.get("pubmedId"),
                            "ancestry": item.get("ancestry"),
                            "sample_size": sample_size,
                            "publication": publication,
                            "download_link": item.get("downloadLink"),
                            "source": "PennPRS Public",
                            "study_id": item.get("studyId"), # Explicitly add study_id
                            "trait_type": item.get("traitType", "Unknown"), # e.g. Binary/Continuous
                            "trait_detailed": item.get("diseaseTrait"), # Map to common field name
                            "submission_date": item.get("submissionDate", "Unknown") # Add date
                        })
                return matches
            return []
        except Exception as e:
            logger.error(f"Error searching public results: {e}") # Changed print to logger.error
            return []

    def get_deep_metadata(self, model_id: str) -> Dict[str, Any]:
        """
        Deep fetch: Downloads the model ZIP, parses training info for H2, and counts variants.
        This is resource intensive and should be called on-demand only.
        """
        import zipfile
        import io
        import re

        url = f"https://pennprs.org/api/download_result?filename={model_id}"
        result = {"h2": None, "num_variants": None, "deep_fetch_status": "failed"}

        try:
            logger.info(f"Deep fetching for {model_id} from {url}...")
            resp = requests.get(url, verify=False, timeout=60)
            
            if resp.status_code == 200:
                with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
                    file_list = z.namelist()
                    
                    # 1. Parse H2 from Training Info
                    info_file = next((n for n in file_list if "PRS_model_training_info" in n), None)
                    if info_file:
                        with z.open(info_file) as f:
                            content = f.read().decode('utf-8')
                            # Look for H2 = 0.05323
                            match = re.search(r'H2\s*=\s*([\d\.]+)', content)
                            if match:
                                result["h2"] = float(match.group(1))

                    # 2. Count Variants from Model File
                    # Look for file ending in .PRS.txt but NOT readme or info
                    model_file = next((n for n in file_list if ".PRS.txt" in n and "training_info" not in n), None)
                    if model_file:
                        with z.open(model_file) as f:
                            # Count lines, skipping header (usually 1 line)
                            # Using sum(1...) is efficient enough for standard PRS files
                            count = sum(1 for _ in f) - 1
                            if count > 0:
                                result["num_variants"] = count
                    
                    result["deep_fetch_status"] = "success"
                    return result
            else:
                logger.error(f"Deep fetch failed: {resp.status_code}")
                return result
                
        except Exception as e:
            logger.error(f"Error deep fetching {model_id}: {e}")
            return result
