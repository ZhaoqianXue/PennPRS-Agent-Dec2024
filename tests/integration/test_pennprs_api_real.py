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
    # Use a user-provided email to ensure notifications go to the correct inbox.
    # This is intentionally required for real API submission tests.
    test_email = os.getenv("PENNPRS_TEST_EMAIL") or os.getenv("PENNPRS_EMAIL")
    if not test_email:
        pytest.skip(
            "Set PENNPRS_TEST_EMAIL (or PENNPRS_EMAIL) to run real PennPRS submission tests.",
            allow_module_level=False,
        )

    client = PennPRSClient(email=test_email)

    # Configuration copied from pennprs-agent/pennprs_tool_octotools.py
    job_config = {
        "job_name": f"Agent_Integration_Test_{int(time.time())}",
        "job_type": "single",
        "job_methods": ['C+T-pseudo'], # Reduced methods for faster/lighter test
        "job_ensemble": True,
        "traits_source": ["Query Data"],
        "traits_detail": ["GWAS Catalog"],
        "traits_type": ["Continuous"],
        "traits_name": ["Alzheimer's Test"], # Descriptive name
        "traits_population": ["EUR"],
        # Keep the payload minimal to match the backend's `/api/submit-training-job`
        # behavior and avoid PennPRS-side schema validation errors.
        "traits_col": [{"id": "GCST007429"}],
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

        assert response, "PennPRS submission returned empty response."
        assert isinstance(response, dict), f"Expected dict response, got {type(response)}"
        assert "job_id" in response, f"Job submission did not return job_id. Response: {response}"

        job_id = response["job_id"]

        # Check status immediately (best-effort).
        status = client.get_job_status(job_id)
        assert status is not None

    except Exception as e:
        pytest.fail(f"Exception during real PennPRS API test: {e}")

if __name__ == "__main__":
    # Allow running as a script for quick manual verification.
    test_real_api_submission()
