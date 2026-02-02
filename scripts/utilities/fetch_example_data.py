
import sys
import os
import json

# Add the src directory to the path so we can import the client
sys.path.append(os.path.abspath("/Users/zhaoqianxue/Desktop/UPenn/PennPRS_Agent/src/server"))

from core.pgs_catalog_client import PGSCatalogClient

def main():
    client = PGSCatalogClient()
    
    def get_data(pgs_id):
        details = client.get_score_details(pgs_id)
        performance = client.get_score_performance(pgs_id)
        perf_example = performance[0] if performance else {}
        return {
            "id": details.get("id"),
            "name": details.get("name"),
            "trait_reported": details.get("trait_reported"),
            "trait_additional": details.get("trait_additional"),
            "trait_efo": ", ".join([t.get("label") for t in details.get("trait_efo", [])]),
            "method_name": details.get("method_name"),
            "method_params": details.get("method_params"),
            "variants_number": details.get("variants_number"),
            "variants_interactions": details.get("variants_interactions"),
            "variants_genomebuild": details.get("variants_genomebuild"),
            "weight_type": details.get("weight_type"),
            "ancestry_distribution": f"GWAS: {next(iter(details.get('ancestry_distribution', {}).get('gwas', {}).get('dist', {})), 'N/A')} (100%)",
            "publication": details.get("publication", {}).get("title"),
            "date_release": details.get("date_release"),
            "license": details.get("license")[:20] + "...",
            "ftp_scoring_file": details.get("ftp_scoring_file")[:30] + "...",
            "ftp_hm_scoring_files": "GRCh37, GRCh38 URLs",
            "matches_publication": str(details.get("matches_publication")),
            "samples_variants": f"n={sum(s.get('sample_number', 0) for s in details.get('samples_variants', []))}",
            "samples_training": f"n={sum(s.get('sample_number', 0) for s in details.get('samples_training', []))}",
            "performance_metrics": f"R²: {next((m.get('estimate') for m in perf_example.get('performance_metrics', {}).get('othermetrics', []) if 'R²' in m.get('name_short', '')), 'N/A')}",
            "phenotyping_reported": perf_example.get("phenotyping_reported"),
            "covariates": perf_example.get("covariates")[:30] + "..." if perf_example.get("covariates") else "null",
            "sampleset": perf_example.get("sampleset", {}).get("name") if perf_example.get("sampleset") else "null",
            "performance_comments": perf_example.get("comments"),
            "associated_pgs_id": perf_example.get("associated_pgs_id")
        }

    ex1 = get_data("PGS000831")
    ex2 = get_data("PGS000018")
    
    print(json.dumps({"ex1": ex1, "ex2": ex2}, indent=2))

if __name__ == "__main__":
    main()
