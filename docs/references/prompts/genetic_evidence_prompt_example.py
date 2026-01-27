from openai import OpenAI
client = OpenAI()

response = client.responses.create(
  model="gpt-5",
  input=[
    {
      "role": "developer",
      "content": [
        {
          "type": "input_text",
          "text": "## ROLE AND OBJECTIVE\nYou are an expert in human genetics, functional genomics, systems biology, model‑organism genetics with domain knowledge in **{{indication_name}}**. Your task is to determine whether a given Target-Indication (T-I) pair reflects a **causal, human-relevant biological relationship** by integrating all relevant evidence from human genetics, functional studies, and animal models.\n \n**Downstream use:** we will use your causal, human-relevant calls to **evaluate whether genetic evidence improves clinical-trial success prediction**. To avoid leakage/circularity, **do not consult, use, or mention any information about drugs, drug classes, therapeutic modalities, or clinical-trial design/results/endpoints/approvals** anywhere in your reasoning, evidence gathering, scoring, or summaries.\n  \n## FOCUS T-I PAIR\n* Target (gene or protein): **{{target_symbol}}**\n* Indication (disease or phenotype): **{{indication_name}}**\n \n## EVIDENCE UNIVERSE (GATHER AND SUMMARIZE)\nSynthesize evidence from broad literature and data sources (**prioritize curated/peer-reviewed sources; among curated sources, prefer the latest releases**). **Summarize what each source claims with identifiers/accessions.**\n\n* **(A) Human genetics:** GWAS Catalog and summary statistics; **Open Targets Genetics credible sets**; Gene Burden (e.g., whole genome sequence and exome sequence such as  GeneBass); Cancer Gene Census; IntOGen; fine-mapping; **colocalization with molecular QTLs** (eQTLs, sQTLs, pQTLs, caQTLs, mQTLs); transcriptome-wide association study (**TWAS**); proteome-wide association study (**PWAS**); phenome-wide association (**PheWAS**); Mendelian randomization; **rare variant burden/LoF (“human knockouts”)**; mutational constraint.\n* **(B) Functional genomics:** tissue or cell type expression (e.g., **GTEx**, Expression Atlas/Single Cell Expression Atlas, **Human Protein Atlas**); regulatory and epigenomic context; perturbation data (e.g., **CRISPR** or **Perturb-seq**), **MPRA**; pathway or process membership (e.g., **Reactome / GO**); protein-protein and genetic interaction networks (e.g., **STRING / BioGRID**); Variant-to-Gene (V2G) links (e.g., promoter capture Hi-C/HiChIP/PLAC-seq, enhancer-promoter models, allele-specific chromatin, and CRISPRi/a enhancer tiling that connect noncoding signals to **{{target_symbol}}**).\n* **(C) Animal and model organisms:** knockout or knock-in phenotypes; **require orthology quality (Ensembl Compara) and uPheno/Monarch phenotype alignment before counting as supportive**; otherwise mark **non-informative**.\n* **(D) Literature-mined knowledge for breadth:** **Europe PMC / PubMed / PMC** for primaries; **Crossref** for metadata; **LitVar 2.0** for variant-literature linking; **SemMedDB** for mined predicates. **Always verify mined claims with primary sources.**\n \n**Deduplication:** Count each finding once per unique primary study/accession; mark mirrored databases in notes.\n\n## REASONING REQUIREMENTS\n* **Direction of Effect (DoE):** infer whether **increased or decreased target activity/expression** is linked to **increased or decreased indication risk/severity**, **prioritizing convergent human lines of evidence** (fine-mapped loci, colocalized QTLs, rare LoF or missense, PheWAS).\n* **Cells of action:** infer the most plausible tissues or cell types using **ct-eQTL**, **sc-eQTL**, expression, **ATAC-seq**, and related data.\n* **Gene–gene context:** consider **paralogs**, functional redundancy, **network neighbors**, pathway role, and potential **synthetic/epistatic interactions**.\n* **Functional and animal work:** use as **support only when orthology is strong**, phenotype class maps via **uPheno/Monarch**, and **DoE and tissue context align with human evidence**; otherwise mark **non-informative**. Only when orthology is strong and the uPheno/Monarch phenotype class is discordant should animal evidence be treated as refuting.\n* **Conflict handling:** if credible studies disagree (e.g., alternative causal gene at locus, discordant DoE across tissues, assay artifacts), **present both sides and justify which is stronger** based on design, replication, and relevance.\n* **Cross-ancestry replication:** **ancestry-specific effects are expected** for many T-I pairs. Record ancestry-specific effects in HGC (with notes). Do **not** count heterogeneity as inconsistency or include it in CONSISTENCY unless a study explicitly refutes causality.\n* **Leakage control (canonical):** Exclude all interventional or treatment-stratified findings and **do not consult, use, or cite** any drug/clinical-trial sources (e.g., ClinicalTrials.gov, FDA/EMA labels, DrugBank, ChEMBL **drug-response** entries, Open Targets Drugs module, trial papers, company press releases). Use only non-interventional human genetics and aligned functional/model evidence.\n* **Causality:** make a **carefully considered call only when multiple, orthogonal lines of evidence converge**. **Prioritize coherent, mutually reinforcing findings** indicating a truly causal, human-relevant relationship and **justify the assigned score**.\n \n## EVIDENCE LEDGER\n* The JSON field ``evidence_register’’ is the canonical evidence ledger. Every claim asserted in any section of the JSON must have >=1 supporting entry in ``evidence_register’’.\n* **Evidence:** human genetic anchors (fine-mapped + QTL colocalization; replicated rare variant associations; coherent PheWAS), functional assays, animal phenotypes aligned via uPheno/Monarch, null findings, alternative gene at the locus, platform artifacts (e.g., pQTL epitope binding), tissue mismatch, credible animal models showing discordant phenotypes.\n \n## SCORING (**QUALITATIVE ONLY; NO NEW COMPUTATIONS**)\nAssign **conservative 0--6 scores** with one decimal place. **Report what sources claim; do not compute new statistics.**\n* **HGC (Human Genetic Causality, 0--6):** strength and replication of human genetic anchors; clarity of causal gene; **cross-ancestry support**; clarity of **DoE**.\n* **BIO_COH (Biological Coherence, 0--6):** tissue/cell relevance, pathway placement, **network proximity**; consistency of mechanism with observed phenotypes.\n* **FUNC_ANIMAL (Functional and Animal, 0--6):** rigor and **human alignment** of functional and animal evidence; **penalize discordance or weak orthology**.\n* **CONSISTENCY (Consistency of Evidence, 0--6):** agreement across different studies and across the HGC, BIO_COH, and FUNC_ANIMAL categories. **Higher means greater consistency**; 0 = severe, replicated contradictions; 3 = mixed/unclear; 6 = highly coherent across lines. Cross-ancestry heterogeneity is not inconsistency.\n* **ICES (Integrated Causal Evidence Score, 0--6):** a **brief (2--10 sentence) rationale** integrating the above.\n**Verdict is determined solely from ICES:**\n* **0.0--1.9** Insufficient\n* **2.0--2.9** Weak\n* **3.0--3.9** Moderate\n* **4.0--4.9** Strong\n* **5.0--6.0** Very Strong.\nDo not average other sub-scores to set the verdict.\n \n# LLM MODE QUALITY GUARDS\n- **Cite or omit rule**: do not assert facts (effects, directions, replication) without a citation to a primary or curated source such as GWAS Catalog, GTEx or eQTL Catalogue, pQTL resources, ClinGen or GenCC, IMPC or MGI, Reactome or GO, STRING or BioGRID, PubMed or PMC.\n- **Two-source confirmation for major claims**: for the **main causal claim** and **DoE**, cite at least two independent sources or one large multi-cohort source.\n- **Refutation duty**: actively search for counterevidence (null findings, alternative gene at locus, discordant functional or animal results) and record it in the summarized evidence.\n- **Do not compute**: report statistics as stated in sources (for example PP4, p values, effect sizes). Do not run coloc, MR, or TWAS yourself.\n- **Assay and platform caveats**: flag potential pQTL assay artifacts, including epitope-binding and platform discordance (Olink vs SomaScan). Prefer cis pQTL replicated across platforms.\n- **Cross-species mapping**: treat animal phenotypes as supportive only if **orthology is strong** and **phenotype class aligns** via **uPheno or Monarch**; otherwise mark as **non-informative**. With strong orthology but discordant phenotype class after uPheno/Monarch mapping, mark as refuting.\n- **Source credibility and freshness**: prefer **peer-reviewed primary studies with high citations or well-curated databases**; label preprints and mined triples (i.e., LitVar/SemMedDB) clearly and verify them with primaries.\n \n## OUTPUT (**STRICT JSON BY SUB-CATEGORY**)\n**Return a single JSON object**. For transparency and traceability, organize all evidence by scoring sub-category (HGC, BIO_COH, FUNC_ANIMAL, CONSISTENCY, ICES) with the following structure. For each sub-category, provide a summarized evidence list (no distinction between supporting and refuting). If there is no evidence for a sub-category, please state no available evidence identified. Include context links to evidence in all categories. Furthermore, scores must be based **only** on genetics/functional/model evidence above; **do not** use drug/trial information to raise or lower scores. Wrap the object in a fenced code block labeled `json`:\n```json\n{\n\"target\": \"{{target_symbol}}\",\n\"indication\": \"{{indication_name}}\",\n\"verdict\": \"Very Strong | Strong | Moderate | Weak | Insufficient\",\n\"scores\": {\n\"HGC\": x.x,\n\"BIO_COH\": x.x,\n\"FUNC_ANIMAL\": x.x,\n\"CONSISTENCY\": x.x,\n\"ICES\": x.x\n},\n\"evidence\": {\n\"HGC\": [\n{ \"summary\": \"Summary of evidence for HGC\", \"citation\": \"PMID or DOI or URL\" }\n],\n\"BIO_COH\": [\n{ \"summary\": \"Summary of evidence for BIO_COH\", \"citation\": \"PMID or DOI or URL\" }\n],\n\"FUNC_ANIMAL\": [\n{ \"summary\": \"Summary of evidence for FUNC_ANIMAL\", \"citation\": \"PMID or DOI or URL\" }\n],\n\"CONSISTENCY\": [\n{ \"summary\": \"Synthesis of agreement/discordance across different studies and across the HGC, BIO_COH, and FUNC_ANIMAL categories; note any explicit refutations.\", \"citation\": \"PMID or DOI or URL\" }\n],\n\"ICES\": {\n\"integration_summary\": \"2--10 sentence rationale integrating the above evidence with clear citations.\"\n}\n},\n\"evidence_register\": [\n{\n\"source_type\": \"Human genetics | Functional genomics | Animal model | Literature-mined | Review\",\n\"id_or_url\": \"...\",\n\"trait_or_tissue\": \"...\",\n\"notes\": \"...\"\n}\n],\n\"notes\": \"Maximum 500 words. Concise synthesis explaining why ICES and verdict are appropriate; cite 1 to 10 key sources.\"\n}\n```"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": "Identify and summarize **causal, human-relevant biological relationship** by integrating all relevant evidence from human genetics, functional studies, and animal models for the following **Target-Indication** (T-I) pair:\n\n* **Target (HGNC symbol or protein): **{{target_symbol}}**\n* **Indication (disease or phenotype): **{{indication_name}}**"
        }
      ]
    }
  ],
  text={
    "format": {
      "type": "json_schema",
      "name": "target_indication_evidence_summary",
      "strict": True,
      "schema": {
        "type": "object",
        "properties": {
          "target": {
            "type": "string",
            "description": "Gene or target symbol."
          },
          "indication": {
            "type": "string",
            "description": "Name of the disease or phenotype under investigation."
          },
          "verdict": {
            "type": "string",
            "description": "Overall verdict based solely on available evidence (not drugs/trials).",
            "enum": [
              "Very Strong",
              "Strong",
              "Moderate",
              "Weak",
              "Insufficient"
            ]
          },
          "scores": {
            "type": "object",
            "properties": {
              "HGC": {
                "type": "number",
                "description": "Score for Human Genetic Correlation sub-category."
              },
              "BIO_COH": {
                "type": "number",
                "description": "Score for Biochemical Cohort sub-category."
              },
              "FUNC_ANIMAL": {
                "type": "number",
                "description": "Score for Functional/Animal model sub-category."
              },
              "CONSISTENCY": {
                "type": "number",
                "description": "Score for Consistency/Agreement sub-category."
              },
              "ICES": {
                "type": "number",
                "description": "Integrated Combined Evidence Score."
              }
            },
            "required": [
              "HGC",
              "BIO_COH",
              "FUNC_ANIMAL",
              "CONSISTENCY",
              "ICES"
            ],
            "additionalProperties": False
          },
          "evidence": {
            "type": "object",
            "properties": {
              "HGC": {
                "type": "array",
                "description": "Summarized evidence list for Human Genetics (HGC). State no available evidence if empty.",
                "items": {
                  "type": "object",
                  "properties": {
                    "summary": {
                      "type": "string",
                      "description": "Summary of supporting or refuting evidence."
                    },
                    "citation": {
                      "type": "string",
                      "description": "Context link or reference (PMID, DOI, or URL)."
                    }
                  },
                  "required": [
                    "summary",
                    "citation"
                  ],
                  "additionalProperties": False
                }
              },
              "BIO_COH": {
                "type": "array",
                "description": "Summarized evidence list for Biochemical Cohorts (BIO_COH). State no available evidence if empty.",
                "items": {
                  "type": "object",
                  "properties": {
                    "summary": {
                      "type": "string",
                      "description": "Summary of supporting or refuting evidence."
                    },
                    "citation": {
                      "type": "string",
                      "description": "Context link or reference (PMID, DOI, or URL)."
                    }
                  },
                  "required": [
                    "summary",
                    "citation"
                  ],
                  "additionalProperties": False
                }
              },
              "FUNC_ANIMAL": {
                "type": "array",
                "description": "Summarized evidence list for Functional/Animal models (FUNC_ANIMAL). State no available evidence if empty.",
                "items": {
                  "type": "object",
                  "properties": {
                    "summary": {
                      "type": "string",
                      "description": "Summary of supporting or refuting evidence."
                    },
                    "citation": {
                      "type": "string",
                      "description": "Context link or reference (PMID, DOI, or URL)."
                    }
                  },
                  "required": [
                    "summary",
                    "citation"
                  ],
                  "additionalProperties": False
                }
              },
              "CONSISTENCY": {
                "type": "array",
                "description": "Summarized synthesis of agreement or discordance, including explicit refutations. State no available evidence if empty.",
                "items": {
                  "type": "object",
                  "properties": {
                    "summary": {
                      "type": "string",
                      "description": "Synthesis of (dis)agreement across evidence lines; explicit refutations noted."
                    },
                    "citation": {
                      "type": "string",
                      "description": "Context link or reference (PMID, DOI, or URL)."
                    }
                  },
                  "required": [
                    "summary",
                    "citation"
                  ],
                  "additionalProperties": False
                }
              },
              "ICES": {
                "type": "object",
                "properties": {
                  "integration_summary": {
                    "type": "string",
                    "description": "2--10 sentence narrative integrating all above evidence and context links."
                  }
                },
                "required": [
                  "integration_summary"
                ],
                "additionalProperties": False
              }
            },
            "required": [
              "HGC",
              "BIO_COH",
              "FUNC_ANIMAL",
              "CONSISTENCY",
              "ICES"
            ],
            "additionalProperties": False
          },
          "evidence_register": {
            "type": "array",
            "description": "Register of indexed primary evidence sources for full transparency.",
            "items": {
              "type": "object",
              "properties": {
                "source_type": {
                  "type": "string",
                  "description": "Type of evidence source.",
                  "enum": [
                    "Human genetics",
                    "Functional genomics",
                    "Animal model",
                    "Literature-mined",
                    "Review"
                  ]
                },
                "id_or_url": {
                  "type": "string",
                  "description": "Identifier or URL of the evidence item."
                },
                "trait_or_tissue": {
                  "type": "string",
                  "description": "Trait or tissue context for the evidence."
                },
                "notes": {
                  "type": "string",
                  "description": "Evidence-specific notes."
                }
              },
              "required": [
                "source_type",
                "id_or_url",
                "trait_or_tissue",
                "notes"
              ],
              "additionalProperties": False
            }
          },
          "notes": {
            "type": "string",
            "description": "Maximum 500 words. Concise synthesis explaining why ICES and verdict are appropriate; cite 1 to 10 key sources."
          }
        },
        "required": [
          "target",
          "indication",
          "verdict",
          "scores",
          "evidence",
          "evidence_register",
          "notes"
        ],
        "additionalProperties": False
      }
    },
    "verbosity": "high"
  },
  reasoning={
    "effort": "high",
    "summary": "auto"
  },
  tools=[],
  store=True,
  include=[
    "reasoning.encrypted_content",
    "web_search_call.action.sources"
  ]
)