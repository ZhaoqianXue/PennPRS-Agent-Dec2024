"""
JSON Schemas for Literature Mining LLM Outputs

Defines strict JSON schemas for structured output from:
- Paper Classifier
- PRS Extractor
- Heritability Extractor
- Genetic Correlation Extractor

These schemas follow the OpenAI Structured Outputs format:
https://platform.openai.com/docs/guides/structured-outputs

Schema Design Principles:
1. All fields have explicit descriptions
2. Enums for categorical values
3. Required fields specified
4. additionalProperties: False for strict validation
"""

from typing import Dict, Any

# ============================================================================
# Paper Classification Schema
# ============================================================================

PAPER_CLASSIFICATION_SCHEMA: Dict[str, Any] = {
    "type": "json_schema",
    "json_schema": {
        "name": "paper_classification",
        "strict": True,
        "schema": {
        "type": "object",
        "properties": {
            "classifications": {
                "type": "array",
                "description": "List of applicable categories for this paper. A paper may belong to multiple categories.",
                "items": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Category classification for the paper.",
                            "enum": [
                                "PRS_PERFORMANCE",
                                "HERITABILITY",
                                "GENETIC_CORRELATION",
                                "NOT_RELEVANT"
                            ]
                        },
                        "confidence": {
                            "type": "number",
                            "description": "Confidence score from 0.0 to 1.0 for this classification."
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "Brief explanation for why this category applies or does not apply."
                        },
                        "key_evidence": {
                            "type": "array",
                            "description": "Key phrases or terms from the abstract that support this classification.",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["category", "confidence", "reasoning", "key_evidence"],
                    "additionalProperties": False
                }
            },
            "primary_category": {
                "type": "string",
                "description": "The most relevant/dominant category for this paper.",
                "enum": [
                    "PRS_PERFORMANCE",
                    "HERITABILITY",
                    "GENETIC_CORRELATION",
                    "NOT_RELEVANT"
                ]
            },
            "data_availability": {
                "type": "object",
                "description": "Assessment of what quantitative data is extractable from this paper.",
                "properties": {
                    "has_prs_metrics": {
                        "type": "boolean",
                        "description": "True if paper reports AUC, R², C-index, or OR per SD for PRS."
                    },
                    "has_heritability": {
                        "type": "boolean",
                        "description": "True if paper reports SNP-heritability (h²) estimates."
                    },
                    "has_genetic_correlation": {
                        "type": "boolean",
                        "description": "True if paper reports genetic correlation (rg) values."
                    },
                    "has_sample_size": {
                        "type": "boolean",
                        "description": "True if paper reports sample size."
                    },
                    "has_ancestry_info": {
                        "type": "boolean",
                        "description": "True if paper specifies population ancestry."
                    }
                },
                "required": [
                    "has_prs_metrics",
                    "has_heritability",
                    "has_genetic_correlation",
                    "has_sample_size",
                    "has_ancestry_info"
                ],
                "additionalProperties": False
            },
            "overall_reasoning": {
                "type": "string",
                "description": "Summary explanation of the classification decision and extractable content."
            }
        },
        "required": [
            "classifications",
            "primary_category",
            "data_availability",
            "overall_reasoning"
        ],
        "additionalProperties": False
        }
    }
}


# ============================================================================
# PRS Model Extraction Schema
# ============================================================================

PRS_EXTRACTION_SCHEMA: Dict[str, Any] = {
    "type": "json_schema",
    "json_schema": {
        "name": "prs_extraction",
        "strict": True,
        "schema": {
        "type": "object",
        "properties": {
            "extractions": {
                "type": "array",
                "description": "List of PRS models extracted from this paper. A paper may report multiple models.",
                "items": {
                    "type": "object",
                    "properties": {
                        "trait": {
                            "type": "string",
                            "description": "Disease or trait name that the PRS predicts."
                        },
                        "performance_metrics": {
                            "type": "object",
                            "description": "Performance metrics for this PRS model. At least one metric is required.",
                            "properties": {
                                "auc": {
                                    "type": ["number", "null"],
                                    "description": "Area Under ROC Curve (0.5-1.0). Null if not reported."
                                },
                                "auc_ci_lower": {
                                    "type": ["number", "null"],
                                    "description": "Lower bound of AUC 95% confidence interval."
                                },
                                "auc_ci_upper": {
                                    "type": ["number", "null"],
                                    "description": "Upper bound of AUC 95% confidence interval."
                                },
                                "r2": {
                                    "type": ["number", "null"],
                                    "description": "Variance explained R² (0.0-1.0). Null if not reported."
                                },
                                "r2_liability": {
                                    "type": ["number", "null"],
                                    "description": "R² on liability scale for binary traits."
                                },
                                "c_index": {
                                    "type": ["number", "null"],
                                    "description": "Concordance statistic (0.5-1.0). Null if not reported."
                                },
                                "or_per_sd": {
                                    "type": ["number", "null"],
                                    "description": "Odds ratio per standard deviation of PRS."
                                },
                                "hr_per_sd": {
                                    "type": ["number", "null"],
                                    "description": "Hazard ratio per standard deviation of PRS."
                                }
                            },
                            "required": [
                                "auc", 
                                "auc_ci_lower", 
                                "auc_ci_upper", 
                                "r2", 
                                "r2_liability", 
                                "c_index", 
                                "or_per_sd", 
                                "hr_per_sd"
                            ],
                            "additionalProperties": False
                        },
                        "model_characteristics": {
                            "type": "object",
                            "properties": {
                                "variants_number": {
                                    "type": ["integer", "null"],
                                    "description": "Number of SNPs/variants in the PRS model."
                                },
                                "method": {
                                    "type": ["string", "null"],
                                    "description": "PRS construction method used.",
                                    "enum": [
                                        "PRS-CS",
                                        "LDpred2",
                                        "C+T",
                                        "P+T",
                                        "lassosum",
                                        "PRSice",
                                        "SBayesR",
                                        "DBSLMM",
                                        "MegaPRS",
                                        "other",
                                        None
                                    ]
                                },
                                "method_detail": {
                                    "type": ["string", "null"],
                                    "description": "Additional method details or parameters."
                                }
                            },
                            "required": ["variants_number", "method", "method_detail"],
                            "additionalProperties": False
                        },
                        "population": {
                            "type": "object",
                            "properties": {
                                "sample_size": {
                                    "type": ["integer", "null"],
                                    "description": "Total sample size (cases + controls or total N)."
                                },
                                "n_cases": {
                                    "type": ["integer", "null"],
                                    "description": "Number of cases (for case-control studies)."
                                },
                                "n_controls": {
                                    "type": ["integer", "null"],
                                    "description": "Number of controls (for case-control studies)."
                                },
                                "ancestry": {
                                    "type": ["string", "null"],
                                    "description": "Population ancestry (European, East Asian, African, etc.)."
                                },
                                "cohort": {
                                    "type": ["string", "null"],
                                    "description": "Cohort or biobank name (UK Biobank, FinnGen, etc.)."
                                }
                            },
                            "required": ["sample_size", "n_cases", "n_controls", "ancestry", "cohort"],
                            "additionalProperties": False
                        },
                        "gwas_source": {
                            "type": "object",
                            "properties": {
                                "gwas_id": {
                                    "type": ["string", "null"],
                                    "description": "GCST ID or other GWAS identifier."
                                },
                                "gwas_source": {
                                    "type": ["string", "null"],
                                    "description": "Source of GWAS summary statistics."
                                }
                            },
                            "required": ["gwas_id", "gwas_source"],
                            "additionalProperties": False
                        },
                        "extraction_metadata": {
                            "type": "object",
                            "properties": {
                                "confidence": {
                                    "type": "number",
                                    "description": "Confidence in this extraction (0.0-1.0)."
                                },
                                "source_text": {
                                    "type": "string",
                                    "description": "Verbatim quote from abstract containing this data."
                                }
                            },
                            "required": ["confidence", "source_text"],
                            "additionalProperties": False
                        }
                    },
                    "required": [
                        "trait",
                        "performance_metrics",
                        "model_characteristics",
                        "population",
                        "gwas_source",
                        "extraction_metadata"
                    ],
                    "additionalProperties": False
                }
            },
            "extraction_notes": {
                "type": "string",
                "description": "Notes about the extraction process, ambiguities, or limitations."
            }
        },
        "required": ["extractions", "extraction_notes"],
        "additionalProperties": False
        }
    }
}


# ============================================================================
# Heritability Extraction Schema
# ============================================================================

HERITABILITY_EXTRACTION_SCHEMA: Dict[str, Any] = {
    "type": "json_schema",
    "json_schema": {
        "name": "heritability_extraction",
        "strict": True,
        "schema": {
        "type": "object",
        "properties": {
            "extractions": {
                "type": "array",
                "description": "List of heritability estimates extracted from this paper.",
                "items": {
                    "type": "object",
                    "properties": {
                        "trait": {
                            "type": "string",
                            "description": "Disease or trait for which heritability is estimated."
                        },
                        "heritability_estimate": {
                            "type": "object",
                            "properties": {
                                "h2": {
                                    "type": "number",
                                    "description": "SNP-heritability estimate (0.0-1.0)."
                                },
                                "se": {
                                    "type": ["number", "null"],
                                    "description": "Standard error of the estimate."
                                },
                                "ci_lower": {
                                    "type": ["number", "null"],
                                    "description": "Lower bound of 95% confidence interval."
                                },
                                "ci_upper": {
                                    "type": ["number", "null"],
                                    "description": "Upper bound of 95% confidence interval."
                                },
                                "scale": {
                                    "type": "string",
                                    "description": "Scale of heritability estimate.",
                                    "enum": ["liability", "observed", "not_specified"]
                                }
                            },
                            "required": ["h2", "se", "ci_lower", "ci_upper", "scale"],
                            "additionalProperties": False
                        },
                        "method": {
                            "type": "object",
                            "properties": {
                                "estimation_method": {
                                    "type": ["string", "null"],
                                    "description": "Method used for heritability estimation.",
                                    "enum": [
                                        "LDSC",
                                        "GCTA",
                                        "GREML",
                                        "BOLT-REML",
                                        "SumHer",
                                        "HESS",
                                        "other",
                                        None
                                    ]
                                },
                                "method_detail": {
                                    "type": ["string", "null"],
                                    "description": "Additional method details."
                                }
                            },
                            "required": ["estimation_method", "method_detail"],
                            "additionalProperties": False
                        },
                        "population": {
                            "type": "object",
                            "properties": {
                                "sample_size": {
                                    "type": ["integer", "null"],
                                    "description": "Sample size for the analysis."
                                },
                                "ancestry": {
                                    "type": ["string", "null"],
                                    "description": "Population ancestry."
                                },
                                "prevalence": {
                                    "type": ["number", "null"],
                                    "description": "Population prevalence (for liability scale conversion)."
                                }
                            },
                            "required": ["sample_size", "ancestry", "prevalence"],
                            "additionalProperties": False
                        },
                        "extraction_metadata": {
                            "type": "object",
                            "properties": {
                                "confidence": {
                                    "type": "number",
                                    "description": "Confidence in this extraction (0.0-1.0)."
                                },
                                "source_text": {
                                    "type": "string",
                                    "description": "Verbatim quote from abstract."
                                }
                            },
                            "required": ["confidence", "source_text"],
                            "additionalProperties": False
                        }
                    },
                    "required": [
                        "trait",
                        "heritability_estimate",
                        "method",
                        "population",
                        "extraction_metadata"
                    ],
                    "additionalProperties": False
                }
            },
            "extraction_notes": {
                "type": "string",
                "description": "Notes about the extraction."
            }
        },
        "required": ["extractions", "extraction_notes"],
        "additionalProperties": False
        }
    }
}


# ============================================================================
# Genetic Correlation Extraction Schema
# ============================================================================

GENETIC_CORRELATION_EXTRACTION_SCHEMA: Dict[str, Any] = {
    "type": "json_schema",
    "json_schema": {
        "name": "genetic_correlation_extraction",
        "strict": True,
        "schema": {
        "type": "object",
        "properties": {
            "extractions": {
                "type": "array",
                "description": "List of genetic correlations extracted from this paper.",
                "items": {
                    "type": "object",
                    "properties": {
                        "trait_pair": {
                            "type": "object",
                            "properties": {
                                "trait1": {
                                    "type": "string",
                                    "description": "First trait in the correlation pair."
                                },
                                "trait2": {
                                    "type": "string",
                                    "description": "Second trait in the correlation pair."
                                }
                            },
                            "required": ["trait1", "trait2"],
                            "additionalProperties": False
                        },
                        "correlation_estimate": {
                            "type": "object",
                            "properties": {
                                "rg": {
                                    "type": "number",
                                    "description": "Genetic correlation coefficient (-1.0 to 1.0)."
                                },
                                "se": {
                                    "type": ["number", "null"],
                                    "description": "Standard error of the estimate."
                                },
                                "p_value": {
                                    "type": ["number", "null"],
                                    "description": "P-value for the correlation."
                                },
                                "ci_lower": {
                                    "type": ["number", "null"],
                                    "description": "Lower bound of 95% confidence interval."
                                },
                                "ci_upper": {
                                    "type": ["number", "null"],
                                    "description": "Upper bound of 95% confidence interval."
                                }
                            },
                            "required": ["rg", "se", "p_value", "ci_lower", "ci_upper"],
                            "additionalProperties": False
                        },
                        "method": {
                            "type": "object",
                            "properties": {
                                "estimation_method": {
                                    "type": ["string", "null"],
                                    "description": "Method used for genetic correlation estimation.",
                                    "enum": [
                                        "LDSC",
                                        "HDL",
                                        "GNOVA",
                                        "SuperGNOVA",
                                        "HESS",
                                        "other",
                                        None
                                    ]
                                },
                                "method_detail": {
                                    "type": ["string", "null"],
                                    "description": "Additional method details."
                                }
                            },
                            "required": ["estimation_method", "method_detail"],
                            "additionalProperties": False
                        },
                        "population": {
                            "type": "object",
                            "properties": {
                                "sample_size_trait1": {
                                    "type": ["integer", "null"],
                                    "description": "Sample size for trait 1."
                                },
                                "sample_size_trait2": {
                                    "type": ["integer", "null"],
                                    "description": "Sample size for trait 2."
                                },
                                "ancestry": {
                                    "type": ["string", "null"],
                                    "description": "Population ancestry."
                                }
                            },
                            "required": ["sample_size_trait1", "sample_size_trait2", "ancestry"],
                            "additionalProperties": False
                        },
                        "extraction_metadata": {
                            "type": "object",
                            "properties": {
                                "confidence": {
                                    "type": "number",
                                    "description": "Confidence in this extraction (0.0-1.0)."
                                },
                                "source_text": {
                                    "type": "string",
                                    "description": "Verbatim quote from abstract."
                                }
                            },
                            "required": ["confidence", "source_text"],
                            "additionalProperties": False
                        }
                    },
                    "required": [
                        "trait_pair",
                        "correlation_estimate",
                        "method",
                        "population",
                        "extraction_metadata"
                    ],
                    "additionalProperties": False
                }
            },
            "extraction_notes": {
                "type": "string",
                "description": "Notes about the extraction."
            }
        },
        "required": ["extractions", "extraction_notes"],
        "additionalProperties": False
        }
    }
}


# ============================================================================
# Export all schemas
# ============================================================================

ALL_SCHEMAS = {
    "paper_classification": PAPER_CLASSIFICATION_SCHEMA,
    "prs_extraction": PRS_EXTRACTION_SCHEMA,
    "heritability_extraction": HERITABILITY_EXTRACTION_SCHEMA,
    "genetic_correlation_extraction": GENETIC_CORRELATION_EXTRACTION_SCHEMA,
}


def get_schema(schema_name: str) -> Dict[str, Any]:
    """Get a schema by name."""
    if schema_name not in ALL_SCHEMAS:
        raise ValueError(f"Unknown schema: {schema_name}. Available: {list(ALL_SCHEMAS.keys())}")
    return ALL_SCHEMAS[schema_name]
