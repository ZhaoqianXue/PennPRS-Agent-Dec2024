from __future__ import annotations

from fastapi import APIRouter

from .models import PennPRSAgentRequest, PennPRSAgentResponse
from .service import get_examples, recommend


router = APIRouter(prefix="/pennprs-agent", tags=["PennPRS Agent"])


@router.get("/examples")
async def pennprs_agent_examples():
    return get_examples()


@router.post("/recommend", response_model=PennPRSAgentResponse)
async def pennprs_agent_recommend(req: PennPRSAgentRequest):
    return recommend(req.target_trait, mode=req.mode)
