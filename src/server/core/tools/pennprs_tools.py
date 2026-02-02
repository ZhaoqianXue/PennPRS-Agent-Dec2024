# src/server/core/tools/pennprs_tools.py
"""
PennPRS Training Tools for Module 3.
Implements sop.md L564-594 tool specifications.
"""
from typing import Union, Optional, List, Dict, Any
import uuid
from datetime import datetime
from src.server.core.tool_schemas import (
    TrainingConfig, JobSubmissionResult, ToolError
)


# Method selection criteria based on domain knowledge
METHOD_CONFIGS = {
    "LDpred2": {
        "description": "Bayesian shrinkage with LD structure",
        "best_for": "Polygenic traits with moderate-to-high heritability",
        "min_sample_size": 50000,
        "para_key": "ldpred2_mode",
        "default_para": {"ldpred2_mode": "auto"}
    },
    "PRS-CS": {
        "description": "Continuous shrinkage prior for polygenicity",
        "best_for": "Highly polygenic traits with very large GWAS",
        "min_sample_size": 100000,
        "para_key": "prscs_phi_mode",
        "default_para": {"prscs_phi_mode": "fullyBayesian"}
    },
    "Lassosum2": {
        "description": "L1 regularization for sparsity",
        "best_for": "Traits with expected sparse genetic architecture",
        "min_sample_size": 30000,
        "para_key": "lassosum_s",
        "default_para": {}
    },
    "CT-pseudo": {
        "description": "Clumping + Thresholding baseline",
        "best_for": "Quick baseline or sparse traits",
        "min_sample_size": 10000,
        "para_key": "ct_pvalue",
        "default_para": {"ct_pvalue_threshold": 5e-8}
    }
}


def generate_training_config(
    target_trait: str,
    gwas_id: str,
    ancestry: str,
    trait_type: str,
    sample_size: Optional[int] = None,
    custom_methods: Optional[List[str]] = None,
    para_dict: Optional[Dict[str, Any]] = None
) -> TrainingConfig:
    """
    Generate a training configuration for PennPRS.
    
    Implements sop.md L572-594 specification.
    This function acts as the Agent's method recommendation engine.
    
    Args:
        target_trait: Disease/trait name
        gwas_id: GCST ID or file reference
        ancestry: Target population (EUR, EAS, AFR, etc.)
        trait_type: 'binary' or 'continuous'
        sample_size: Optional GWAS sample size for method selection
        custom_methods: Override recommended methods
        para_dict: Optional method-specific parameters
        
    Returns:
        TrainingConfig ready for submission or UI display
    """
    # Determine recommended methods based on sample size
    if custom_methods:
        methods = custom_methods
        recommended = methods[0]
        rationale = "User-specified methods"
    else:
        methods, recommended, rationale = _recommend_methods(sample_size, trait_type)
    
    # Generate unique job name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_trait = target_trait.replace(" ", "_")[:20]
    job_name = f"{safe_trait}_{timestamp}_{uuid.uuid4().hex[:6]}"
    
    # Determine LD reference based on ancestry
    ld_ref = _get_ld_reference(ancestry)
    
    # Determine source type
    if gwas_id.startswith("GCST"):
        traits_source = "public"
        traits_detail = gwas_id
    elif gwas_id.startswith("FILE:"):
        traits_source = "user"
        traits_detail = gwas_id
    else:
        traits_source = "public"
        traits_detail = gwas_id
    
    # Build parameter dict
    final_para = para_dict or {}
    if not final_para:
        # Use default params for recommended method
        if recommended in METHOD_CONFIGS:
            final_para = METHOD_CONFIGS[recommended].get("default_para", {})
    
    # Determine confidence based on sample size
    if sample_size and sample_size >= 100000:
        confidence = "High"
    elif sample_size and sample_size >= 50000:
        confidence = "Moderate"
    else:
        confidence = "Low"
    
    return TrainingConfig(
        target_trait=target_trait,
        recommended_method=recommended,
        method_rationale=rationale,
        job_name=job_name,
        job_type="single",
        job_methods=methods,
        job_ensemble=len(methods) > 1,
        traits_source=traits_source,
        traits_detail=traits_detail,
        traits_type=trait_type,
        traits_population=ancestry,
        gwas_summary_stats=gwas_id,
        ld_reference=ld_ref,
        ancestry=ancestry,
        para_dict=final_para,
        agent_confidence=confidence,
        estimated_runtime=_estimate_runtime(methods, sample_size)
    )


def pennprs_train_model(
    pennprs_client,  # PennPRSClient
    config: TrainingConfig
) -> Union[JobSubmissionResult, ToolError]:
    """
    Submit a PRS training job to PennPRS.
    
    Implements sop.md L576-594 specification.
    Human-in-the-Loop: User reviews config before this is called.
    
    Args:
        pennprs_client: Configured PennPRSClient instance
        config: Training configuration (reviewed by user)
        
    Returns:
        JobSubmissionResult on success, ToolError on failure
    """
    try:
        # Build traits_col as required by API
        traits_col = [{"gwas_id": config.gwas_summary_stats}]
        
        # Submit job
        response = pennprs_client.add_single_job(
            job_name=config.job_name,
            job_type=config.job_type,
            job_methods=config.job_methods,
            job_ensemble=config.job_ensemble,
            traits_source=[config.traits_source],
            traits_detail=[config.traits_detail],
            traits_type=[config.traits_type],
            traits_name=[config.target_trait],
            traits_population=[config.traits_population],
            traits_col=traits_col,
            para_dict=config.para_dict
        )
        
        if response is None:
            return ToolError(
                tool_name="pennprs_train_model",
                error_type="SubmissionFailed",
                error_message="PennPRS API returned None - submission may have failed",
                context={"job_name": config.job_name}
            )
        
        return JobSubmissionResult(
            success=True,
            job_id=response.get("jobId"),
            job_name=config.job_name,
            status=response.get("status", "submitted"),
            message=response.get("message", "Job submitted successfully"),
            config=config
        )
        
    except Exception as e:
        return ToolError(
            tool_name="pennprs_train_model",
            error_type=type(e).__name__,
            error_message=str(e),
            context={"job_name": config.job_name}
        )


def _recommend_methods(
    sample_size: Optional[int],
    trait_type: str
) -> tuple:
    """
    Recommend PRS methods based on GWAS characteristics.
    
    Returns:
        Tuple of (methods_list, primary_recommendation, rationale)
    """
    # Default to comprehensive set if sample size unknown
    if sample_size is None:
        return (
            ["LDpred2", "PRS-CS", "CT-pseudo"],
            "LDpred2",
            "LDpred2 recommended as robust default; PRS-CS included for comparison"
        )
    
    if sample_size >= 200000:
        return (
            ["PRS-CS", "LDpred2"],
            "PRS-CS",
            f"PRS-CS recommended for very large GWAS (N={sample_size:,}); handles polygenicity well"
        )
    elif sample_size >= 100000:
        return (
            ["LDpred2", "PRS-CS"],
            "LDpred2",
            f"LDpred2 recommended for large GWAS (N={sample_size:,}); auto mode provides good default"
        )
    elif sample_size >= 50000:
        return (
            ["LDpred2", "Lassosum2"],
            "LDpred2",
            f"LDpred2 recommended for moderate GWAS (N={sample_size:,})"
        )
    else:
        return (
            ["CT-pseudo", "Lassosum2"],
            "CT-pseudo",
            f"C+T recommended for smaller GWAS (N={sample_size:,}); simple and robust"
        )


def _get_ld_reference(ancestry: str) -> str:
    """Get appropriate LD reference panel for ancestry."""
    ref_map = {
        "EUR": "1000G EUR",
        "EAS": "1000G EAS",
        "AFR": "1000G AFR",
        "SAS": "1000G SAS",
        "AMR": "1000G AMR",
    }
    return ref_map.get(ancestry.upper(), f"1000G {ancestry.upper()}")


def _estimate_runtime(methods: List[str], sample_size: Optional[int]) -> str:
    """Estimate job runtime based on methods and sample size."""
    base_hours = len(methods) * 0.5
    
    if sample_size:
        if sample_size > 200000:
            base_hours *= 2
        elif sample_size > 100000:
            base_hours *= 1.5
    
    if base_hours < 1:
        return "~30 minutes"
    elif base_hours < 2:
        return "~1-2 hours"
    elif base_hours < 4:
        return "~2-4 hours"
    else:
        return "~4+ hours"
