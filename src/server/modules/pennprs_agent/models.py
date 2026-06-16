from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


AgentMode = Literal["cached", "live"]


class PennPRSAgentRequest(BaseModel):
    target_trait: str = Field(..., min_length=1)
    mode: AgentMode = "cached"


class AgentTraceStep(BaseModel):
    id: str
    title: str
    status: Literal["queued", "running", "completed", "skipped", "failed"]
    detail: str
    provenance: list[str] = Field(default_factory=list)


class SameTraitQualityAssessment(BaseModel):
    accept_direct_baseline: bool
    rationale: str


class FinalRecommendation(BaseModel):
    recommendation_source: Literal["same_trait", "cross_trait_transfer", "none"]
    recommended_pgs_id: Optional[str] = None
    recommended_trait: Optional[str] = None
    confidence: Optional[str] = None
    summary: str


class PennPRSAgentResponse(BaseModel):
    target_trait: str
    mode: AgentMode
    same_trait_result: dict[str, Any]
    same_trait_quality_assessment: SameTraitQualityAssessment
    transfer_result: Optional[dict[str, Any]] = None
    final_recommendation: FinalRecommendation
    agent_trace_steps: list[AgentTraceStep]
    artifacts_used: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    timing: dict[str, Any] = Field(default_factory=dict)
