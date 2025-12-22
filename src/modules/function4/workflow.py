from typing import Dict, Any, TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.core.pennprs_client import PennPRSClient
from src.core.pgs_catalog_client import PGSCatalogClient
from src.modules.function4.models import Function4State, JobConfiguration, TraitColumn, Report
from src.modules.function4.report_generator import extract_features, generate_report_markdown
import os
import json
import datetime

# Define the state for the graph
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    next_node: str
    user_intent: str
    selected_trait: str # Track the trait
    selected_model_id: str # Track selected model
    pgs_results: list # Track catalog results
    job_config: Dict[str, Any]
    job_id: str
    job_status: str
    result_path: str # Path to downloaded results
    report_data: Report # Generated report
    structured_response: Dict[str, Any] # Structured data for frontend UI
    request_id: str # Tracking ID for progress polling

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Initialize Clients
client = PennPRSClient()
pgs_client = PGSCatalogClient()

# Node: Input Analysis
def input_analysis(state: AgentState):
    messages = state['messages']
    last_content = messages[-1].content.lower()
    
    # 0. Priority Detection: Deep Fetch / Deep Scan
    if "deep fetch" in last_content or "scan" in last_content:
         # Extract ID
         parts = last_content.split()
         model_id = None
         for p in parts:
            p_clean = p.strip(".,?!")
            if p_clean.startswith("gcst") or p_clean.startswith("pgs"):
                model_id = p_clean.upper()
                break
         if model_id:
             return {"selected_model_id": model_id, "user_intent": "deep_fetch", "next_node": "deep_fetch_metadata"}

    # 1. Detection: Train New (Highest Priority for 'train')
    if "train" in last_content or "new model" in last_content:
        trait = "Alzheimer's"
        if "for" in last_content:
             # simple extraction if needed, but collect_training_info does the real work
             pass
        return {"selected_trait": trait, "user_intent": "train_new", "next_node": "collect_training_info"}

    # 2. Detection: Use Existing Model / Download
    if "use" in last_content or "download" in last_content or "get" in last_content or "model" in last_content:
        # Simple extraction of potential ID (e.g., PGS000025 or GCST...)
        # Heuristic: verify against known patterns or just look for alphanumeric
        parts = last_content.split()
        model_id = None
        for p in parts:
            p_clean = p.strip(".,?!")
            if p_clean.startswith("pgs") or p_clean.startswith("gcst"):
                model_id = p_clean.upper()
                break
        
        if model_id:
            return {"selected_model_id": model_id, "user_intent": "use_existing", "next_node": "fetch_metadata"}
    
    # 3. Default: Search
    trait = "Alzheimer's"
    if "for" in last_content:
        trait = last_content.split("for")[-1].strip().strip("?.")
    elif len(last_content) < 50:
        trait = last_content
    
    if "alzheimer" in trait.lower():
        trait = "Alzheimer's disease"
        
    return {"selected_trait": trait, "user_intent": "search", "next_node": "pgs_search"}

# Helper: Fetch and Format Models
def _fetch_formatted_models(trait: str, request_id: str = None):
    import concurrent.futures
    import time
    from src.main import search_progress # Import shared state
    
    # 1. Search PGS Catalog
    if request_id and request_id in search_progress:
        search_progress[request_id]["current_action"] = "Searching PGS Catalog..."
    
    t_start = time.time()
    pgs_results = pgs_client.search_scores(trait)
    print(f"[Timing] PGS Search (IDs): {time.time() - t_start:.4f}s")
    
    # 2. Search PennPRS Public Results
    t_penn = time.time()
    penn_results = client.search_public_results(trait)
    print(f"[Timing] PennPRS Search: {time.time() - t_penn:.4f}s")

    # Update total count (PGS + PennPRS)
    if request_id and request_id in search_progress:
        search_progress[request_id]["total"] = len(pgs_results) + len(penn_results)
        search_progress[request_id]["status"] = "running"
        search_progress[request_id]["current_action"] = "Fetching metadata..."
    
    model_cards = []
    
    # Parallel Fetch details and performance for PGS Catalog (Unlimited)
    t_details = time.time()
    pgs_details_map = {}
    pgs_performance_map = {}
    
    fetched_count = 0 
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Create a dictionary to map future to ID and type (details or performance)
        future_to_req = {}
        for res in pgs_results:
             pid = res.get('id')
             future_to_req[executor.submit(pgs_client.get_score_details, pid)] = (pid, 'details')
             future_to_req[executor.submit(pgs_client.get_score_performance, pid)] = (pid, 'performance')
        
        for future in concurrent.futures.as_completed(future_to_req):
            pid, req_type = future_to_req[future]
            try:
                data = future.result()
                if req_type == 'details':
                    pgs_details_map[pid] = data
                    # Only increment count on details completion to avoid double counting
                    fetched_count += 1
                    if request_id and request_id in search_progress:
                        search_progress[request_id]["fetched"] = fetched_count
                        search_progress[request_id]["current_action"] = f"Fetching {pid}..."

                else:
                    pgs_performance_map[pid] = data
            except Exception as exc:
                print(f'{pid} {req_type} generated an exception: {exc}')

    print(f"[Timing] Parallel Fetch Details & Perf ({len(pgs_results)} models): {time.time() - t_details:.4f}s")

    # Add PGS Catalog Models (Unlimited)

    for res in pgs_results:
        pid = res.get('id')
        details = pgs_details_map.get(pid, {})
        perf_data = pgs_performance_map.get(pid, [])
        metrics = details.get("metrics", {})
        

        # Format Performance Detailed
        performance_detailed = []
        for p in perf_data:
            # Extract Metrics from complex structure
            p_metrics = p.get("performance_metrics", {})
            
            # 1. AUC (from class_acc or othermetrics)
            auc_val = None
            auc_lower = None
            auc_upper = None
            
            # Check class_acc first (common for AUC)
            for acc in p_metrics.get("class_acc", []):
                name = acc.get("name_short", "") + acc.get("name_long", "")
                if "AUC" in name or "AUROC" in name:
                    auc_val = acc.get("estimate")
                    auc_lower = acc.get("ci_lower")
                    auc_upper = acc.get("ci_upper")
                    break
            
            # Check othermetrics if not found
            if auc_val is None:
                for om in p_metrics.get("othermetrics", []):
                    name = om.get("name_short", "") + om.get("name_long", "")
                    if "AUC" in name or "AUROC" in name or "C-index" in name or "Area under curve" in name:
                        auc_val = om.get("estimate")
                        auc_lower = om.get("ci_lower")
                        auc_upper = om.get("ci_upper")
                        break

            # 2. R2 (from othermetrics)
            r2_val = None
            for om in p_metrics.get("othermetrics", []):
                name = om.get("name_short", "") + om.get("name_long", "")
                name_lower = name.lower()
                if "r2" in name_lower or "r^2" in name_lower or "variance" in name_lower:
                    r2_val = om.get("estimate")
                    break

            # 3. Effect Sizes (HR/OR/Beta) - usually one main one
            eff_val = None
            eff_type = None
            if p_metrics.get("effect_sizes"):
                eff = p_metrics.get("effect_sizes")[0]
                eff_val = eff.get("estimate")
                eff_type = eff.get("name_short")
            
            # Populate if we have at least some data
            if auc_val or r2_val or eff_val:
                performance_detailed.append({
                    "ppm_id": p.get("id"),
                    "ancestry": p.get("sampleset", {}).get("samples", [{}])[0].get("ancestry_broad"),
                    "cohorts": ", ".join([c.get("name_short") for c in p.get("sampleset", {}).get("samples", [{}])[0].get("cohorts", []) if c.get("name_short")]),
                    "sample_size": p.get("sampleset", {}).get("samples", [{}])[0].get("sample_number"),
                    "auc": auc_val,
                    "auc_ci_lower": auc_lower,
                    "auc_ci_upper": auc_upper,
                    "r2": r2_val,
                    "covariates": p.get("covariates"),
                    "comments": p.get("performance_comments")
                })
                
                # Update top-level metrics if empty (using first available)
                if not metrics.get("AUC") and auc_val: metrics["AUC"] = auc_val
                if not metrics.get("R2") and r2_val: metrics["R2"] = r2_val
                if not metrics.get("HR") and eff_type == 'HR': metrics["HR"] = eff_val
                if not metrics.get("OR") and eff_type == 'OR': metrics["OR"] = eff_val
                if not metrics.get("Beta") and eff_type == 'Beta': metrics["Beta"] = eff_val

        # Refine Ancestry for root model card
        ancestry_root = details.get("ancestry") 
        if not ancestry_root:
             # Try to parse from ancestry_distribution.dist (e.g. key names)
             # "ancestry_distribution": {"gwas": {"dist": {"EUR": 93.66, ...}}}
             anc_dist = details.get("ancestry_distribution", {})
             if anc_dist:
                 # Check available stages: gwas > dev > eval
                 stage_dist = anc_dist.get("gwas", {}).get("dist") or anc_dist.get("dev", {}).get("dist") or anc_dist.get("eval", {}).get("dist")
                 if stage_dist:
                     ancestry_root = ", ".join(stage_dist.keys())
        
        if not ancestry_root:
             ancestry_root = ",".join(res.get('ancestry', []))

        
        # Parse Ancestry Distribution for Frontend (List Format)
        # Frontend expects: { dist: [{ancestry, percent, number}, ...] }
        # API returns: { "dev": { "dist": {"EUR": 100}, "count": N }, ... }
        ancestry_dist_frontend = {"dist": []}
        anc_dist_api = details.get("ancestry_distribution", {})
        
        # Priority: gwas > dev > eval
        target_stage_key = "gwas" if "gwas" in anc_dist_api else "dev" if "dev" in anc_dist_api else "eval"
        if target_stage_key in anc_dist_api:
            stage_data = anc_dist_api[target_stage_key]
            dists = stage_data.get("dist", {})
            total_count = stage_data.get("count", 0)
            
            for anc_code, pct in dists.items():
                # Calculate approximate number if total count exists
                num = int((pct / 100.0) * total_count) if total_count else 0
                ancestry_dist_frontend["dist"].append({
                    "ancestry": anc_code,
                    "percent": pct,
                    "number": num
                })

        # Map trait_efo to mapped_traits
        mapped_traits_list = []
        if details.get("trait_efo"):
            for t in details.get("trait_efo"):
                mapped_traits_list.append({
                    "id": t.get("id"),
                    "label": t.get("label"),
                    "url": t.get("url")
                })

        
        # Helper to extract total sample size safely
        def get_sample_size_safe(d):
            # Try top level
            if isinstance(d.get("sample_size"), int): return d.get("sample_size")
            
            # Try summing samples_variants or samples_training
            # These are usually lists of objects with 'sample_number'
            total = 0
            for key in ["samples_variants", "samples_training"]:
                val = d.get(key)
                if isinstance(val, list):
                    for item in val:
                         if isinstance(item, dict):
                             total += item.get("sample_number", 0) or 0
                elif isinstance(val, dict):
                    # Handle case where it might be a single dict (rare but possible in some API versions?)
                    total += val.get("sample_number", 0) or 0
            
            return total if total > 0 else 0

        model_cards.append({
            "id": pid,
            "name": details.get('name') or res.get('name', 'Unnamed Model'),
            "trait": res.get('trait_reported', trait),
            # Use details ancestry (computed from distribution) as primary, fallback to search res
            "ancestry": ancestry_root,
            "method": details.get("method_name", res.get('method_name', 'Unknown')),
            "metrics": metrics, 
            "num_variants": details.get("variants_number", 0), # Correct key: variants_number
            "publication": details.get("publication"), # Pass full publication dict
            "sample_size": get_sample_size_safe(details), # Safe extraction
            "source": "PGS Catalog",

            "download_url": res.get('ftp_scoring_file'),
            # New Fields
            "trait_detailed": details.get("trait_reported"),
            "trait_efo": [t.get("id") for t in details.get("trait_efo", [])], # Keep simple list for compatibility if needed
            "license": details.get("license"),
            "genome_build": details.get("variants_genomebuild"),
            "covariates": details.get("covariates"), # Often null at top level, found in performance
            "performance_comments": details.get("performance_comments"),
            "ancestry_distribution": ancestry_dist_frontend,
            # Newly Recovered Technical Fields
            "pgs_name": details.get("name"), # Name is top level
            "mapped_traits": mapped_traits_list,
            "performance_detailed": performance_detailed,
            "weight_type": details.get("weight_type"),
            "params": details.get("method_params"),
            "variants_genomebuild": details.get("variants_genomebuild"),
            "trait_reported": details.get("trait_reported")
        })


        
    # Add PennPRS Models (Unlimited)
    for res in penn_results:
        # PennPRS usually has metrics in the search result
        metrics = res.get('metrics', {})
        # Strictly NO MOCKS for PennPRS either as requested
        
        model_cards.append({
            "id": res.get('id'),
            "name": res.get('name', 'Unnamed Model'),
            "trait": trait, 
            "ancestry": res.get('ancestry', 'Unknown'),
            "method": res.get('method', 'PennPRS'),
            "metrics": metrics,
            "sample_size": res.get('sample_size', 0), # Mapped from PennPRS Client
            "publication": res.get('publication'), # Mapped from PennPRS Client
            "source": "PennPRS",
            "download_url": res.get('download_link'),
            # New Fields
            "study_id": res.get("study_id"),
            "trait_type": res.get("trait_type"),
            "trait_detailed": res.get("trait_detailed"),
            "submission_date": res.get("submission_date")
        })
        
    # Sort model_cards by AUC descending
    # Prioritize detailed AUC, then metrics AUC
    # Sort model_cards by AUC descending
    # Prioritize detailed AUC, then metrics AUC
    def get_sort_auc(card):
        # Ancestry Mapping (Code -> Full Name prefix)
        ancestry_map = {
            'EUR': 'European',
            'AFR': 'African',
            'EAS': 'East Asian',
            'SAS': 'South Asian',
            'AMR': 'Hispanic', 
            'MIX': 'Multi-ancestry'
        }

        # Check detailed performance first
        perf = card.get("performance_detailed", [])
        if perf:
            # 1. Try to find match for Model's training ancestry
            model_ancestries = [s.strip() for s in (card.get("ancestry") or "").split(",")]
            target_ancestry_names = [ancestry_map.get(code, code) for code in model_ancestries]
            
            matched_record = None
            for p in perf:
                p_anc = (p.get("ancestry") or "").lower()
                # Check if any target ancestry is in this record's ancestry
                if any(target.lower() in p_anc for target in target_ancestry_names):
                    matched_record = p
                    break
            
            if matched_record and matched_record.get("auc"):
                 return matched_record.get("auc")

            # 2. Fallback: Find max AUC in detailed records
            max_p = max((p.get("auc") or 0 for p in perf), default=0)
            if max_p > 0: return max_p
            
        # Fallback to metrics object
        metrics = card.get("metrics", {})
        return metrics.get("AUC") or 0

    model_cards.sort(key=get_sort_auc, reverse=True)

    return model_cards, pgs_results, penn_results

# Node: Combined Model Search
def pgs_search(state: AgentState):
    trait = state.get("selected_trait")
    if not trait:
        return {"messages": [AIMessage(content="I couldn't identify the trait.")], "next_node": END}
        
    model_cards, pgs_results, penn_results = _fetch_formatted_models(trait, request_id=state.get("request_id"))
    
    msg = f"I found **{len(model_cards)}** models for '{trait}' (combining PGS Catalog and PennPRS public results).\n\n"
    
    best_model_data = None
    options = []
    
    if model_cards:
        best_model_data = model_cards[0]
        
        msg += f"The model with the highest AUC is **{best_model_data.get('name')}** (ID: {best_model_data.get('id')}).\n"
        msg += "I've displayed the best model card below. You can view detailed information for this result and others in the **Canvas** panel.\n\n"
        msg += "How would you like to proceed?"

        options = [
            "Evaluate on Cohort",
            "Build Ensemble Model",
            "Download Model",
            "Train Custom Model"
        ]
    else:
        msg += "No models found. Would you like to **Train Custom Model**?"
        options = ["Train Custom Model"]

    structured_data = {
        "type": "model_grid",
        "models": model_cards,
        "best_model": best_model_data,
        "actions": options
    }

    return {
        "pgs_results": pgs_results, 
        "messages": [AIMessage(content=msg)], 
        "structured_response": structured_data,
        "next_node": END
    }

# Node: Collect Training Info
def collect_training_info(state: AgentState):
    messages = state['messages']
    last_content = messages[-1].content
    
    # Defaults
    trait = state.get("selected_trait", "Alzheimer's")
    job_name = f"Train_{trait.split()[0]}"
    ancestry = "EUR"
    methods = ['C+T-pseudo']
    ensemble = False
    data_source_type = "public"
    data_source_value = "GCST007429"
    trait_type = "Continuous"
    sample_size = 100000
    hyperparams = {}

    import re

    # 1. Parse Job Name
    # "named 'JobName'"
    m_name = re.search(r"named '([^']+)'", last_content)
    if m_name:
        job_name = m_name.group(1)

    # 2. Parse Ancestry
    # "(Ancestry: EUR)"
    m_anc = re.search(r"Ancestry: (\w+)", last_content)
    if m_anc:
        ancestry = m_anc.group(1)

    # 3. Parse Methods
    # "Methods: C+T-pseudo, Lassosum2"
    m_meth = re.search(r"Methods: (.+?)(?:\n|$)", last_content)
    if m_meth:
        methods = [m.strip() for m in m_meth.group(1).split(',')]

    # 4. Parse Ensemble
    if "Ensemble: Enabled" in last_content:
        ensemble = True

    # 5. Parse Data Source
    # "Data Source: Public GWAS (ID: GCST007429)" or "Data Source: User Upload (filename.txt)"
    m_source = re.search(r"Data Source: (Public GWAS|User Upload) \((?:ID: |)(.+?)\)", last_content)
    if m_source:
        source_type_str = m_source.group(1)
        data_source_value = m_source.group(2)
        if "Upload" in source_type_str:
            data_source_type = "upload"
        else:
            data_source_type = "public"

    # 6. Parse Trait Type & Sample Size
    # "Trait Type: Continuous, Sample Size: 10000"
    m_type = re.search(r"Trait Type: (\S+)", last_content)
    if m_type:
        trait_type = m_type.group(1)
    
    m_n = re.search(r"Sample Size: (\d+)", last_content)
    if m_n:
        sample_size = int(m_n.group(1))

    # 7. Parse Hyperparams
    # "Hyperparams: kb=500, r2=0.1, pval_thr=..."
    m_hyper = re.search(r"Hyperparams: (.+?)(?:\n|$)", last_content)
    if m_hyper:
        # naive parse "k=v, k2=v2"
        pairs = m_hyper.group(1).split(',')
        for p in pairs:
            if '=' in p:
                k, v = p.split('=')
                hyperparams[k.strip()] = v.strip()


    # Map to API Structure
    # If Public: traits_col uses ID
    # If Upload: traits_col uses ??? (For now, assume we pass filename as ID or special field, 
    # but since we are MOCKING the upload for now, we'll just pass it as 'id' for tracking or a new field if client supports)
    
    traits_col_entry = {}
    if data_source_type == 'public':
        traits_col_entry = {"id": data_source_value}
    else:
        # Mocking upload: We don't have the file technically on backend yet unless we POSTed it.
        # But for the Agent Simulation, we will treat 'id' as the filename to indicate source.
        traits_col_entry = {"id": f"FILE:{data_source_value}"} 


    job_config = {
        "job_name": job_name, 
        "traits_name": [trait],
        "traits_col": [traits_col_entry],
        "job_methods": methods,
        "job_ensemble": ensemble,
        "traits_type": [trait_type],
        "traits_population": [ancestry],
        "traits_source": ["User Upload" if data_source_type == "upload" else "Query Data"],
        "traits_detail": ["User Data" if data_source_type == "upload" else "GWAS Catalog"],
        "para_dict": hyperparams
    }
    
    return {"job_config": job_config, "next_node": "submit_training"}

# Node: Submit Training (Keep as is)
def submit_training(state: AgentState):
    config = state.get("job_config")
    if not config:
        return {"messages": [AIMessage(content="Failed to configure job.")], "next_node": END}
        
    res = client.add_single_job(
        job_name=config.get("job_name"),
        job_type="single",
        job_methods=config.get("job_methods", ['C+T-pseudo']),
        job_ensemble=config.get("job_ensemble", False),
        traits_source=config.get("traits_source", ["Query Data"]),
        traits_detail=config.get("traits_detail", ["GWAS Catalog"]),
        traits_type=config.get("traits_type", ["Continuous"]),
        traits_name=config.get("traits_name"),
        traits_population=config.get("traits_population", ["EUR"]),
        traits_col=config.get("traits_col"),
        para_dict=config.get("para_dict")
    )
    
    if res and "job_id" in res:
        return {"job_id": res["job_id"], "job_status": "submitted", "messages": [AIMessage(content=f"Job submitted! ID: {res['job_id']}")], "next_node": "poll_status"}
    else:
        return {"messages": [AIMessage(content="Job submission failed.")], "next_node": END}

# Node: Poll Status (Keep as is)
def poll_status(state: AgentState):
    job_id = state.get("job_id")
    status = client.get_job_status(job_id)
    return {"job_status": status, "messages": [AIMessage(content=f"Current status: {status}")]}

# Node: Fetch Metadata
def fetch_metadata(state: AgentState):
    mid = state.get("selected_model_id")
    # In a real app, we'd fetch details from PGS Catalog or PennPRS API here.
    # For now, we pass through to download.
    msg = f"Fetching metadata for model {mid}..."
    return {"messages": [AIMessage(content=msg)], "next_node": "download_results"}

# Node: Download Results
def download_results(state: AgentState):
    mid = state.get("selected_model_id") or state.get("job_id") or "UNKNOWN"
    
    # Mock download path
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    result_path = f"{output_dir}/{mid}_result.zip"
    
    # Create a dummy file if not exists
    if not os.path.exists(result_path):
        with open(result_path, "w") as f:
            f.write("Mock result content")
            
    msg = f"Results downloaded to {result_path}."
    return {"result_path": result_path, "messages": [AIMessage(content=msg)], "next_node": "generate_report"}

# Node: Generate Report
def generate_report(state: AgentState):
    result_path = state.get("result_path")
    mid = state.get("selected_model_id") or state.get("job_id") or "UNKNOWN"
    trait = state.get("selected_trait", "Alzheimer's disease")
    
    # Extract
    report = extract_features(result_path, mid, trait)
    
    # Generate Markdown
    md_content = generate_report_markdown(report)
    
    user_intent = state.get("user_intent")
    structured_data = None
    
    if user_intent == "train_new":
        # Return a Model Grid with the new model added
        config = state.get("job_config", {})
        
        # Determine source label
        src_label = "PennPRS (Custom)"
        if "Upload" in config.get("traits_source", [])[0]:
            src_label = "User Upload"
            
        new_model_card = {
            "id": state.get("job_id", "NEW_JOB"),
            "name": config.get("job_name", f"Custom Model ({trait})"),
            "trait": trait,
            "ancestry": config.get("traits_population", ["EUR"])[0], 
            "method": ", ".join(config.get("job_methods", ["Unknown"])), 
            "metrics": {"R2": 0.15, "AUC": 0.65}, # Still mock result values until real download parsed
            "source": src_label,
            "download_url": "#"
        }
        
        # Fetch existing models to merge
        existing_models, _, _ = _fetch_formatted_models(trait)
        
        # Prepend new model
        model_cards = [new_model_card] + existing_models
        
        structured_data = {
            "type": "model_grid",
            "models": model_cards
        }
        
        # Append prompt to text
        md_content += "\n\n**Training Complete!** I've added your new model to the list below (first item). You can **Select** it to proceed to benchmarking."

    else:
        # Return Downstream Options (Step 2)
        structured_data = {
            "type": "downstream_options",
            "model_id": mid,
            "trait": trait,
            "options": ["benchmark", "proteomics", "ensemble"]
        }
        
        md_content += "\n\n[INFO] Model selected. Please choose a downstream analysis option below."

    return {"report_data": report, "messages": [AIMessage(content=md_content)], "structured_response": structured_data, "next_node": END}

# Node: Deep Fetch Metadata (New)
def deep_fetch_metadata(state: AgentState):
    mid = state.get("selected_model_id")
    msg = f"Deep scanning model **{mid}**... This involves downloading and parsing the model file. Please wait."
    
    # Perform Deep Fetch
    result = client.get_deep_metadata(mid)
    
    status_msg = ""
    if result.get("deep_fetch_status") == "success":
        h2 = result.get("h2", "N/A")
        vars_count = result.get("num_variants", "N/A")
        
        # User Feedback: Don't show results in dialog, just update details.
        status_msg = f"**Deep Scan Complete.** Model details have been updated."
        
        # Return a structured update event (frontend can consume this to update state)
        structured_data = {
            "type": "model_update",
            "model_id": mid,
            "updates": {
                "metrics": {"H2": h2}, # Merge into metrics
                "num_variants": vars_count,
                "deep_scan_done": True
            }
        }
        return {"messages": [AIMessage(content=status_msg)], "structured_response": structured_data, "next_node": END}
    else:
        status_msg = f"Deep scan failed for {mid}. The file might not be accessible or has an unexpected format."
        return {"messages": [AIMessage(content=status_msg)], "next_node": END}

# Graph Construction
workflow = StateGraph(AgentState)

workflow.add_node("input_analysis", input_analysis)
workflow.add_node("pgs_search", pgs_search)
workflow.add_node("collect_training_info", collect_training_info)
workflow.add_node("submit_training", submit_training)
workflow.add_node("poll_status", poll_status)
workflow.add_node("fetch_metadata", fetch_metadata)
workflow.add_node("download_results", download_results)
workflow.add_node("generate_report", generate_report)
workflow.add_node("deep_fetch_metadata", deep_fetch_metadata)

workflow.set_entry_point("input_analysis")

# Conditional Routing
def route_input(state):
    return state["next_node"]

workflow.add_conditional_edges(
    "input_analysis",
    route_input,
    {
        "pgs_search": "pgs_search",
        "collect_training_info": "collect_training_info",
        "fetch_metadata": "fetch_metadata",
        "deep_fetch_metadata": "deep_fetch_metadata"
    }
)

# Route poll_status: if completed -> download, else -> poll (loop not fully impl here for simplicity)
def route_poll(state):
    status = state.get("job_status")
    if status == "completed" or True: # Force complete for demo/mock
        return "download_results"
    return "poll_status" # Creating a loop

workflow.add_conditional_edges(
    "poll_status",
    route_poll,
    {
        "download_results": "download_results",
        "poll_status": "poll_status"
    }
)

workflow.add_edge("pgs_search", END)
workflow.add_edge("collect_training_info", "submit_training")
workflow.add_edge("submit_training", "poll_status")
workflow.add_edge("fetch_metadata", "download_results")
workflow.add_edge("download_results", "generate_report")
workflow.add_edge("generate_report", END)
workflow.add_edge("deep_fetch_metadata", END)

app = workflow.compile()
