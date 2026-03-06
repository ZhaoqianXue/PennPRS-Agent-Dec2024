#!/usr/bin/env python3
"""
Debug script to investigate why T2D search returns 184 models but results in NO_MATCH_FOUND.
"""

import sys
import json
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.server.modules.disease.recommendation_agent import recommend_models
from src.server.core.pgs_catalog_client import PGSCatalogClient
from src.server.core.tools.prs_model_tools import (
    prs_model_pgscatalog_search,
    prs_model_performance_landscape,
    prs_model_domain_knowledge
)
from src.server.core.agent_artifacts import stable_json_dumps

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def debug_t2d_search():
    """Debug T2D search and Step 1 decision."""
    target_trait = "t2d"
    
    print(f"\n{'='*80}")
    print(f"Debugging T2D Search: '{target_trait}'")
    print(f"{'='*80}\n")
    
    # Step 1: Search PGS Catalog
    print("Step 1: Searching PGS Catalog...")
    pgs_client = PGSCatalogClient()
    pgs_result = prs_model_pgscatalog_search(pgs_client, target_trait)
    
    print(f"\nPGS Search Results:")
    print(f"  - Query trait: {pgs_result.query_trait}")
    print(f"  - Total found: {pgs_result.total_found}")
    print(f"  - After filter: {pgs_result.after_filter}")
    print(f"  - Models returned: {len(pgs_result.models)}")
    
    if pgs_result.models:
        print(f"\nFirst 3 models:")
        for i, model in enumerate(pgs_result.models[:3], 1):
            print(f"  {i}. {model.id}: {model.trait_reported}")
            if hasattr(model, 'performance_metrics') and model.performance_metrics:
                print(f"     Performance: {model.performance_metrics}")
    
    # Step 2: Get performance landscape
    print(f"\n{'='*80}")
    print("Step 2: Getting performance landscape...")
    landscape = prs_model_performance_landscape(pgs_client, pgs_result.models)
    print(f"Performance Landscape:")
    landscape_dict = landscape.model_dump()
    print(f"  - Models with AUC: {landscape_dict.get('models_with_auc', 'N/A')}")
    print(f"  - Models with R2: {landscape_dict.get('models_with_r2', 'N/A')}")
    if 'auc_stats' in landscape_dict and landscape_dict['auc_stats']:
        print(f"  - AUC stats: {landscape_dict['auc_stats']}")
    if 'r2_stats' in landscape_dict and landscape_dict['r2_stats']:
        print(f"  - R2 stats: {landscape_dict['r2_stats']}")
    
    # Step 3: Get domain knowledge
    print(f"\n{'='*80}")
    print("Step 3: Getting domain knowledge...")
    knowledge = prs_model_domain_knowledge(f"{target_trait} PRS clinical thresholds AUC R2")
    print(f"Domain Knowledge:")
    print(f"  - Knowledge items: {len(knowledge.knowledge_items)}")
    if knowledge.knowledge_items:
        print(f"  - First item: {knowledge.knowledge_items[0][:200]}...")
    
    # Step 4: Build Step 1 context
    print(f"\n{'='*80}")
    print("Step 4: Building Step 1 context...")
    
    from src.server.modules.disease.recommendation_agent import (
        _summarize_search_result_for_llm,
        _slugify,
        TOP_MODELS_INLINE
    )
    from src.server.core.agent_artifacts import maybe_externalize_json, MAX_INLINE_CONTEXT_BYTES
    
    direct_models_dump = pgs_result.model_dump()
    direct_models_inline, direct_models_artifact = maybe_externalize_json(
        payload=direct_models_dump,
        artifact_prefix=f"direct_models_{_slugify(target_trait)}",
        max_inline_bytes=MAX_INLINE_CONTEXT_BYTES,
        max_inline_tokens=2_000,
        summary_builder=lambda _: _summarize_search_result_for_llm(pgs_result, top_n=TOP_MODELS_INLINE)
    )
    
    step1_context = {
        "target_trait": target_trait,
        "direct_models": direct_models_inline,
        "direct_models_artifact": direct_models_artifact.model_dump() if direct_models_artifact else None,
        "performance_landscape": landscape.model_dump(),
        "domain_knowledge": knowledge.model_dump(),
    }
    
    print(f"Step 1 Context Summary:")
    print(f"  - Target trait: {step1_context['target_trait']}")
    print(f"  - Direct models type: {type(step1_context['direct_models'])}")
    if isinstance(step1_context['direct_models'], dict):
        print(f"  - Direct models keys: {list(step1_context['direct_models'].keys())}")
        if 'total_found' in step1_context['direct_models']:
            print(f"  - Total found in context: {step1_context['direct_models']['total_found']}")
        if 'after_filter' in step1_context['direct_models']:
            print(f"  - After filter in context: {step1_context['direct_models']['after_filter']}")
        if 'top_models' in step1_context['direct_models']:
            print(f"  - Top models count: {len(step1_context['direct_models']['top_models'])}")
    
    # Step 5: Call Step 1 chain
    print(f"\n{'='*80}")
    print("Step 5: Calling Step 1 decision chain...")
    
    from src.server.modules.disease.recommendation_agent import _build_step1_chain
    
    try:
        chain = _build_step1_chain()
        step1_decision = chain.invoke(
            {"context_json": stable_json_dumps(step1_context)}
        )
        
        print(f"\nStep 1 Decision:")
        print(f"  - Outcome: {step1_decision.outcome}")
        print(f"  - Best model ID: {step1_decision.best_model_id}")
        print(f"  - Confidence: {step1_decision.confidence}")
        print(f"  - Rationale: {step1_decision.rationale}")
        
        # Save full context for inspection
        output_file = Path(__file__).parent.parent / "results" / "debug_t2d_step1_context.json"
        output_file.parent.mkdir(exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump({
                "step1_context": step1_context,
                "step1_decision": step1_decision.model_dump(),
                "pgs_result_summary": {
                    "query_trait": pgs_result.query_trait,
                    "total_found": pgs_result.total_found,
                    "after_filter": pgs_result.after_filter,
                    "models_count": len(pgs_result.models)
                }
            }, f, indent=2, default=str)
        print(f"\nFull context saved to: {output_file}")
        
    except Exception as exc:
        print(f"\nERROR in Step 1 chain:")
        print(f"  - Exception type: {type(exc).__name__}")
        print(f"  - Exception message: {str(exc)}")
        import traceback
        traceback.print_exc()
    
    # Step 6: Full recommendation
    print(f"\n{'='*80}")
    print("Step 6: Running full recommendation workflow...")
    
    try:
        report = recommend_models(target_trait, request_id="debug_t2d")
        
        print(f"\nFinal Report:")
        print(f"  - Recommendation type: {report.recommendation_type}")
        print(f"  - Primary recommendation: {report.primary_recommendation}")
        print(f"  - Genetic graph ran: {report.genetic_graph_ran}")
        print(f"  - Genetic graph neighbors: {report.genetic_graph_neighbors}")
        print(f"  - Caveats: {report.caveats_and_limitations}")
        
        # Save full report
        output_file = Path(__file__).parent.parent / "results" / "debug_t2d_full_report.json"
        with open(output_file, 'w') as f:
            json.dump(report.model_dump(), f, indent=2, default=str)
        print(f"\nFull report saved to: {output_file}")
        
    except Exception as exc:
        print(f"\nERROR in full recommendation:")
        print(f"  - Exception type: {type(exc).__name__}")
        print(f"  - Exception message: {str(exc)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_t2d_search()
