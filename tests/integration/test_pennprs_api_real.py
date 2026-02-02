import sys
import os
import time
import logging
import pytest

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.core.pennprs_client import PennPRSClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if os.getenv("RUN_REAL_API_TESTS") != "1":
    pytest.skip("Skipping real PennPRS API tests (set RUN_REAL_API_TESTS=1 to enable).", allow_module_level=True)

def test_real_api_submission():
    """
    Test submitting a real job to PennPRS API.
    """
    print("Initializing PennPRS Client...")
    # Using the email from reference implementation if valid, or a test email.
    # ideally this should be the user's email.
    # Using the valid email for testing
    TEST_EMAIL = "zhaoqian.xue@pennmedicine.upenn.edu"
    client = PennPRSClient(email=TEST_EMAIL) 
    
    print("Preparing job configuration...")
    # Configuration copied from pennprs-agent/pennprs_tool_octotools.py
    job_config = {
        "job_name": "Agent_Integration_Test_001",
        "job_type": "single",
        "job_methods": ['C+T-pseudo'], # Reduced methods for faster/lighter test
        "job_ensemble": True,
        "traits_source": ["Query Data"],
        "traits_detail": ["GWAS Catalog"],
        "traits_type": ["Continuous"],
        "traits_name": ["Alzheimer's Test"], # Descriptive name
        "traits_population": ["EUR"],
        "traits_col": [{
            "id": "GCST007429", # Valid ID from reference
            "SNP": "", "CHR": "", "BETA": "", "SE": "", "P": "",
            "A1": "", "A2": "", "MAF": "", "N": "321047",
            "NEFF": "", "NCASE": "", "NCONTROL": ""
        }],
        "para_dict": {
            'delta': '0.001,0.01', # reduced
            'nlambda': '30',
            'lambda_min_ratio': '0.01',
            'alpha': '1.0',
            'p_seq': '0.001,0.01,0.1,1.0',
            'sparse': 'FALSE',
            'kb': '500',
            'pval_thr': '5e-08,5e-05',
            'r2': '0.1',
            'Ll': '5', 'Lc': '5', 'ndelta': '5', 'phi': '1e-2'
        }
    }

    print(f"Submitting job: {job_config['job_name']}...")
    try:
        response = client.add_single_job(
            job_name=job_config["job_name"],
            job_type=job_config["job_type"],
            job_methods=job_config["job_methods"],
            job_ensemble=job_config["job_ensemble"],
            traits_source=job_config["traits_source"],
            traits_detail=job_config["traits_detail"],
            traits_type=job_config["traits_type"],
            traits_name=job_config["traits_name"],
            traits_population=job_config["traits_population"],
            traits_col=job_config["traits_col"],
            para_dict=job_config["para_dict"]
        )
        
        if response and "job_id" in response:
            job_id = response["job_id"]
            print(f"✅ Job submitted successfully! Job ID: {job_id}")
            
            # Check Status immediately
            print(f"Checking status for Job ID: {job_id}...")
            status = client.get_job_status(job_id)
            print(f"Current Status: {status}")
            
            return True
        else:
            print("❌ Job submission failed. No Job ID returned.")
            print(f"Response: {response}")
            return False

    except Exception as e:
        print(f"❌ Exception during API test: {e}")
        return False

if __name__ == "__main__":
    success = test_real_api_submission()
    if not success:
        sys.exit(1)
