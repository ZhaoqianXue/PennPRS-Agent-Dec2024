import sys
import os
from unittest.mock import MagicMock

# Mock OpenAI before import
sys.modules["langchain_openai"] = MagicMock()
sys.modules["langchain_openai.chat_models"] = MagicMock()
sys.modules["langchain_openai.chat_models.base"] = MagicMock()

# Also set dummy env var just in case
os.environ["OPENAI_API_KEY"] = "dummy"

sys.path.append(os.getcwd())

from src.modules.function3.workflow import _fetch_formatted_protein_scores

def test_multi_protein_search():
    print("Testing multi-protein search...")
    query = "APOE, IL6"
    request_id = "test_req_1"
    
    # We expect this to print "[Multi-Search] Searching for 2 terms: ['APOE', 'IL6']"
    # and then execute searches.
    
    try:
        model_cards, raw_results = _fetch_formatted_protein_scores(query, request_id=request_id)
        
        print(f"Successfully fetched {len(model_cards)} model cards.")
        print(f"First model: {model_cards[0]['name'] if model_cards else 'None'}")
        
        # Check if we have results for both
        has_apoe = any("APOE" in str(c) for c in model_cards)
        has_il6 = any("IL6" in str(c) for c in model_cards)
        
        print(f"Has APOE: {has_apoe}")
        print(f"Has IL6: {has_il6}")
        
    except Exception as e:
        print(f"Error during search: {e}")

if __name__ == "__main__":
    test_multi_protein_search()
