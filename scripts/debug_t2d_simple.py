#!/usr/bin/env python3
"""
Simplified debug script to investigate T2D NO_MATCH_FOUND issue.
"""

import sys
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
project_root = Path(__file__).parent.parent
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"Loaded environment variables from {env_file}")
else:
    print(f"Warning: .env file not found at {env_file}")

# Add project root to path
sys.path.insert(0, str(project_root))

from src.server.modules.disease.recommendation_agent import recommend_models

def main():
    target_trait = "t2d"
    print(f"Testing T2D recommendation for: '{target_trait}'")
    print("=" * 80)
    
    try:
        report = recommend_models(target_trait, request_id="debug_t2d_simple")
        
        print(f"\nFinal Report:")
        print(f"  Recommendation type: {report.recommendation_type}")
        print(f"  Primary recommendation: {report.primary_recommendation}")
        print(f"  Genetic graph ran: {report.genetic_graph_ran}")
        print(f"  Caveats: {report.caveats_and_limitations}")
        
        # Save report
        output_file = Path(__file__).parent.parent / "results" / "debug_t2d_simple_report.json"
        output_file.parent.mkdir(exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(report.model_dump(), f, indent=2, default=str)
        print(f"\nReport saved to: {output_file}")
        
    except Exception as exc:
        print(f"\nERROR: {type(exc).__name__}: {str(exc)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
