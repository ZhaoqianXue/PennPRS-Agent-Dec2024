"""
Protein Module: PennPRS-Protein Workflow
Handles searching and displaying protein genetic scores from OmicsPred.
"""

from typing import Dict, Any, TypedDict, Annotated, List
import operator
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from src.server.core.llm_config import get_llm  # Centralized LLM config
from src.server.core.omicspred_client import OmicsPredClient
import concurrent.futures
import time

# Define the state for the protein workflow
class ProteinAgentState(TypedDict):
    messages: Annotated[list, operator.add]
    next_node: str
    user_intent: str
    selected_protein: str  # Track the target protein/gene
    selected_platform: str  # Track platform filter (Olink, Somalogic, etc.)
    selected_model_id: str  # Track selected score
    protein_results: list  # Track OmicsPred results
    structured_response: Dict[str, Any]  # Structured data for frontend UI
    request_id: str  # Tracking ID for progress polling


# Initialize LLM from centralized config
llm = get_llm("protein_workflow")

# Initialize Client
omicspred_client = OmicsPredClient()


# Node: Input Analysis
def input_analysis(state: ProteinAgentState):
    """
    Analyze user input to determine intent:
    - Search for protein scores
    - Get details for a specific score
    - Filter by platform
    """
    messages = state['messages']
    last_content = messages[-1].content.lower()
    
    # Check for platform passed from frontend
    incoming_platform = state.get("selected_platform", "")
    
    # 1. Detection: Get specific score details
    if "details" in last_content or "info" in last_content:
        # Try to extract OPGS ID
        import re
        match = re.search(r'opgs\d+', last_content, re.IGNORECASE)
        if match:
            score_id = match.group(0).upper()
            return {
                "selected_model_id": score_id,
                "user_intent": "get_details",
                "next_node": "fetch_score_details"
            }
    
    # 2. Detection: Platform-specific browsing (no protein query needed)
    platform = incoming_platform  # Use platform from state first
    is_browse_only = "browse" in last_content or (platform and not any(kw in last_content for kw in ["search", "find", "for"]))
    
    if not platform:
        if "olink" in last_content:
            platform = "Olink"
        elif "somalogic" in last_content or "soma" in last_content:
            platform = "Somalogic"
    
    # If browsing platform without search terms, don't extract protein query
    if is_browse_only and platform:
        return {
            "selected_protein": "",  # Empty - browsing only
            "selected_platform": platform,
            "user_intent": "browse_platform",
            "next_node": "protein_search"
        }
    
    # 3. Default: Protein search
    # Extract protein/gene name from query
    protein_query = ""
    
    # Try to extract after common keywords
    for keyword in ["for", "of", "search", "find", "protein", "gene", "scores"]:
        if keyword in last_content:
            parts = last_content.split(keyword)
            if len(parts) > 1:
                candidate = parts[-1].strip().strip("?.!").strip()
                # Filter out platform names and common words
                if candidate and candidate not in ["olink", "somalogic", "platform", ""]:
                    protein_query = candidate
                    break
    
    # If no keyword, use the whole input as query (if short)
    if not protein_query and len(last_content) < 50:
        # But exclude platform-related messages
        if platform and any(kw in last_content for kw in ["browse", "platform", "all"]):
            protein_query = ""  # Don't use the message as a query
        else:
            protein_query = last_content.strip()
    
    return {
        "selected_protein": protein_query,
        "selected_platform": platform or "",
        "user_intent": "search",
        "next_node": "protein_search"
    }


# Helper: Fetch and fully hydrate protein scores with detailed performance data
def _fetch_formatted_protein_scores(
    protein_query: str, 
    platform: str = None,
    request_id: str = None
) -> tuple[List[Dict], List[Dict]]:
    """
    Fetch protein scores from OmicsPred and fully hydrate them with details (R2, Rho, etc.).
    Matches the user experience of Disease Search (Search -> Count -> Progress Bar -> Details).
    
    Returns:
        Tuple of (formatted_model_cards, raw_detailed_results)
    """
    from src.server.core.state import search_progress  # Import shared progress state
    
    # 1. Update progress: Initial Search
    if request_id and request_id in search_progress:
        search_progress[request_id]["current_action"] = "Searching OmicsPred..."
        search_progress[request_id]["status"] = "running"
    
    t_start = time.time()
    
    search_results = []
    seen_ids = set()
    
    # --- PHASE 1: Initial Discovery (Get IDs) ---
    
    if protein_query:
        # Check for multiple terms (comma-separated)
        terms = [t.strip() for t in protein_query.split(',') if t.strip()]
        
        if len(terms) > 1:
            print(f"[Multi-Search] Searching for {len(terms)} terms: {terms}")
            if request_id and request_id in search_progress:
                search_progress[request_id]["current_action"] = f"Searching for {len(terms)} genes/proteins..."
            
            # Parallel search for each term
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                future_to_term = {executor.submit(omicspred_client.search_scores_general, term): term for term in terms}
                
                for future in concurrent.futures.as_completed(future_to_term):
                    try:
                        results = future.result()
                        for res in results:
                            sid = res.get("id") or res.get("opgs_id")
                            if sid and sid not in seen_ids:
                                seen_ids.add(sid)
                                search_results.append(res)
                    except Exception as exc:
                        print(f"Term search generated exception: {exc}")
        else:
            # Single term search
            single_term = terms[0] if terms else protein_query
            search_results = omicspred_client.search_scores_general(single_term)
            
    elif platform:
        search_results = omicspred_client.get_scores_by_platform(platform)
    else:
        search_results = []

    total_models = len(search_results)
    print(f"[Timing] Initial Search: {time.time() - t_start:.4f}s (Found: {total_models})")
    
    if total_models == 0:
        return [], []

    # --- PHASE 2: Fetch Detailed Info (Parallel) ---
    
    # Init Progress Bar for Retrieval
    if request_id and request_id in search_progress:
        search_progress[request_id]["total"] = total_models
        search_progress[request_id]["fetched"] = 0
        search_progress[request_id]["current_action"] = "Retrieving model details (Ancestry, R2, Rho)..."

    detailed_models = []
    
    # Helper for parallel execution
    def fetch_single_detail(item):
        try:
            sid = item.get("id") or item.get("opgs_id")
            if not sid: return None
            # Fetch FULL details (calls public + private API)
            details = omicspred_client.get_score_details(sid)
            # Format immediately
            formatted = omicspred_client.format_score_for_ui(details)
            return formatted
        except Exception as e:
            print(f"Error fetching details for {item.get('id')}: {e}")
            return None

    t_details = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all tasks
        futures = [executor.submit(fetch_single_detail, item) for item in search_results]
        
        # Process as they complete to update progress
        completed_count = 0
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                detailed_models.append(result)
            
            completed_count += 1
            if request_id and request_id in search_progress:
                search_progress[request_id]["fetched"] = completed_count
                # Optional: Update action text periodically
                if completed_count % 5 == 0:
                     search_progress[request_id]["current_action"] = f"Retrieving details {completed_count}/{total_models}..."

    print(f"[Timing] Detail Fetch & Format: {time.time() - t_details:.4f}s")
    
    # Sort by R2 or sample size (descending)
    def get_sort_key(card):
        metrics = card.get("metrics", {})
        r2 = metrics.get("R2") or 0
        sample = card.get("sample_size") or 0
        return (r2, sample)
    
    detailed_models.sort(key=get_sort_key, reverse=True)
    
    return detailed_models, search_results  # Return formatted detailed models


# Node: Protein Search
def protein_search(state: ProteinAgentState):
    """
    Search for protein genetic scores in OmicsPred.
    """
    protein_query = state.get("selected_protein", "")
    platform = state.get("selected_platform", "")
    request_id = state.get("request_id")
    
    if not protein_query and not platform:
        return {
            "messages": [AIMessage(content="Please specify a protein, gene, or platform to search for.")],
            "next_node": END
        }
    
    model_cards, raw_results = _fetch_formatted_protein_scores(
        protein_query, platform, request_id
    )
    
    # Build response message
    search_term = protein_query or platform
    msg = f"I found **{len(model_cards)}** proteomics genetic scores"
    
    if protein_query:
        msg += f" related to **'{protein_query}'**"
    if platform:
        msg += f" from **{platform}** platform"
    msg += " in OmicsPred.\n\n"
    
    best_model_data = None
    options = []
    
    if model_cards:
        best_model_data = model_cards[0]
        
        msg += f"The top scoring model is **{best_model_data.get('name')}** (ID: {best_model_data.get('id')}).\n"
        msg += "You can view detailed information for this result and others in the **Canvas** panel."
        
        options = [
            "View Score Details",
            "Download this Score",
            "Browse All Platforms"
        ]
    else:
        msg += "No scores found matching your criteria. Try a different protein name or browse by platform."
        options = ["Browse Olink Scores", "Browse Somalogic Scores"]
    
    structured_data = {
        "type": "protein_grid",
        "models": model_cards,
        "best_model": best_model_data,
        "actions": options,
        "search_query": protein_query,
        "platform": platform
    }
    
    return {
        "protein_results": raw_results,
        "messages": [AIMessage(content=msg)],
        "structured_response": structured_data,
        "next_node": END
    }


# Node: Fetch Score Details
def fetch_score_details(state: ProteinAgentState):
    """
    Get detailed information for a specific OmicsPred score.
    """
    score_id = state.get("selected_model_id")
    
    if not score_id:
        return {
            "messages": [AIMessage(content="I couldn't identify the score ID.")],
            "next_node": END
        }
    
    details = omicspred_client.get_score_details(score_id)
    
    if not details:
        return {
            "messages": [AIMessage(content=f"Could not fetch details for score {score_id}.")],
            "next_node": END
        }
    
    # Format for display
    formatted = omicspred_client.format_score_for_ui(details)
    
    msg = f"**Score Details: {score_id}**\n\n"
    msg += f"- **Protein**: {formatted.get('protein_name') or 'N/A'}\n"
    msg += f"- **Gene**: {formatted.get('gene_name') or 'N/A'}\n"
    msg += f"- **Platform**: {formatted.get('platform') or 'N/A'}\n"
    msg += f"- **Variants**: {formatted.get('num_variants') or 'N/A'}\n"
    msg += f"- **Sample Size**: {formatted.get('sample_size') or 'N/A'}\n"
    
    metrics = formatted.get("metrics", {})
    if metrics.get("R2"):
        msg += f"- **R²**: {metrics.get('R2')}\n"
    if metrics.get("H2"):
        msg += f"- **Heritability (h²)**: {metrics.get('H2')}\n"
    
    structured_data = {
        "type": "protein_detail",
        "model": formatted,
        "actions": ["Download this Score", "Back to Search"]
    }
    
    return {
        "messages": [AIMessage(content=msg)],
        "structured_response": structured_data,
        "next_node": END
    }


# Graph Construction
workflow = StateGraph(ProteinAgentState)

workflow.add_node("input_analysis", input_analysis)
workflow.add_node("protein_search", protein_search)
workflow.add_node("fetch_score_details", fetch_score_details)

workflow.set_entry_point("input_analysis")


# Conditional Routing
def route_input(state):
    return state.get("next_node", END)


workflow.add_conditional_edges(
    "input_analysis",
    route_input,
    {
        "protein_search": "protein_search",
        "fetch_score_details": "fetch_score_details"
    }
)

workflow.add_edge("protein_search", END)
workflow.add_edge("fetch_score_details", END)

app = workflow.compile()
