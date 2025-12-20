import os
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv

# Load env before importing modules that might need it
load_dotenv()

from src.modules.function4.workflow import app as workflow_app

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

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
