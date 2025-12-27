import os
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv

# Load env before importing modules that might need it
load_dotenv()

from src.modules.function4.workflow import app as workflow_app
from src.modules.function3.workflow import app as protein_workflow_app

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

app = FastAPI(title="PennPRS Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev, ideally ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Progress Store (InMemory)
# {request_id: {"status": "running"|"completed", "total": 0, "fetched": 0, "current_action": ""}}
search_progress = {}

class AgentRequest(BaseModel):
    message: str
    request_id: str = None # Optional for backward compatibility

@app.get("/")
async def root():
    return {"message": "PennPRS Agent is running"}

@app.get("/agent/search_progress/{request_id}")
async def get_search_progress(request_id: str):
    """
    Get the progress of a search request.
    """
    return search_progress.get(request_id, {"status": "unknown"})

@app.post("/agent/invoke")
def invoke_agent(req: AgentRequest):
    """
    Invoke the agent with a message.
    """
    # Initialize progress if ID provided
    if req.request_id:
        search_progress[req.request_id] = {
            "status": "starting",
            "total": 0,
            "fetched": 0,
            "current_action": "Initializing..."
        }

    initial_state = {
        "messages": [HumanMessage(content=req.message)],
        "request_id": req.request_id # Pass ID to graph
    }
    
    # Run the workflow
    result = workflow_app.invoke(initial_state)
    
    # Mark complete
    if req.request_id:
        search_progress[req.request_id]["status"] = "completed"
        search_progress[req.request_id]["current_action"] = "Done"
    
    # Extract the last message content from the agent for the response
    # Result['messages'] is a list of BaseMessages
    last_msg = result['messages'][-1]
    response_text = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
    
    return {"response": response_text, "full_state": result}


class TraitClassifyRequest(BaseModel):
    trait_name: str
    sample_info: str = None  # Optional extra context


@app.post("/agent/classify_trait")
async def classify_trait_endpoint(req: TraitClassifyRequest):
    """
    Use LLM to classify whether a trait is Binary (disease/case-control) or Continuous (quantitative measurement).
    Also extracts ancestry information from sample_info.
    Returns: {"trait_type": "Binary" | "Continuous", "ancestry": "EUR" | "AFR" | ..., "confidence": "high" | "medium" | "low"}
    """
    from src.modules.function4.trait_classifier import classify_trait
    
    return classify_trait(req.trait_name, req.sample_info)


class ProteinAgentRequest(BaseModel):
    message: str
    request_id: str = None  # Optional for progress tracking
    platform: str = None  # Optional platform filter (Olink, Somalogic)


@app.post("/protein/invoke")
def invoke_protein_agent(req: ProteinAgentRequest):
    """
    Invoke the protein agent for proteomics PRS model search.
    Uses OmicsPred as the data source.
    """
    # Initialize progress if ID provided
    if req.request_id:
        search_progress[req.request_id] = {
            "status": "starting",
            "total": 0,
            "fetched": 0,
            "current_action": "Initializing protein search..."
        }

    initial_state = {
        "messages": [HumanMessage(content=req.message)],
        "request_id": req.request_id,
        "selected_platform": req.platform or ""
    }
    
    # Run the protein workflow
    result = protein_workflow_app.invoke(initial_state)
    
    # Mark complete
    if req.request_id:
        search_progress[req.request_id]["status"] = "completed"
        search_progress[req.request_id]["current_action"] = "Done"
    
    # Extract the last message content
    last_msg = result['messages'][-1]
    response_text = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
    
    return {"response": response_text, "full_state": result}


@app.get("/protein/platforms")
async def list_protein_platforms():
    """
    List available proteomics platforms from OmicsPred.
    """
    from src.core.omicspred_client import OmicsPredClient
    
    client = OmicsPredClient()
    platforms = client.list_platforms()
    
    return {"platforms": platforms}


@app.get("/protein/score/{score_id}")
async def get_protein_score_details(score_id: str):
    """
    Get detailed information for a specific OmicsPred score.
    """
    from src.core.omicspred_client import OmicsPredClient
    
    client = OmicsPredClient()
    details = client.get_score_details(score_id)
    formatted = client.format_score_for_ui(details)
    
    return formatted


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)

