"""Build a 10-trait rerun manifest with the reworked skill baked in.

The pairwise-rerank runner rebuilds the system prompt and user instruction live
from the within_prompts module (so prompt edits apply automatically), but it
reuses the `skill_context` frozen inside each request's Context JSON. This script
refreshes that skill_context from the *current* prs-model-recommendation skill
(SKILL.md + corpus, via the production loader) and filters the manifest to the 10
target traits. Candidate pools and the AoU answer key (`benchmark_ranked_ids`)
are reused verbatim, so before/after ranks are comparable on identical data.

No API calls.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[5]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.contribution2.recommendation.scripts.run_experiment_with_domain import (
    _domain_query,
    _skill_context_from_domain_result,
)
from src.server.core.tools.prs_model_tools import prs_model_domain_knowledge

SRC_MANIFEST = (
    PROJECT_ROOT
    / "experiments/contribution2/recommendation/runs"
    / "with-domain-gpt-5.4-t1__44disease__efoclean44-prs-agent-final-20260614"
    / "experiment_with_domain_batch_manifest.json"
)
OUT_MANIFEST = (
    PROJECT_ROOT
    / "experiments/contribution2/recommendation/analysis/target10_hit1"
    / "rerun_manifest_target10_newskill.json"
)

TARGETS = {
    "type 2 diabetes mellitus", "breast carcinoma", "prostate carcinoma",
    "hypertension", "asthma", "alzheimer disease", "thyroid carcinoma",
    "major depressive disorder", "psoriasis", "ovarian neoplasm",
}

MARKER = "Context:\n"


def _fresh_skill_context(ontology: str, target_ancestry: str) -> dict:
    query = _domain_query(ontology, target_ancestry)
    domain = prs_model_domain_knowledge(query, max_snippets=8).model_dump()
    return _skill_context_from_domain_result(domain)


def main() -> int:
    manifest = json.loads(SRC_MANIFEST.read_text(encoding="utf-8"))

    manifest["requests"] = [r for r in manifest["requests"] if r["ontology"] in TARGETS]
    manifest["disease_metadata"] = [
        d for d in manifest["disease_metadata"] if d["ontology"] in TARGETS
    ]
    manifest["total_ontologies"] = len(manifest["disease_metadata"])
    manifest["total_requests"] = len(manifest["requests"])
    manifest["run_tag"] = "target10-newskill"

    old_len = new_len = 0
    for req in manifest["requests"]:
        content = req["request"]["body"]["messages"][1]["content"]
        head, raw_ctx = content.split(MARKER, 1)
        ctx = json.loads(raw_ctx)
        old_len = max(old_len, len(ctx["skill_context"]["full_text"]))
        ctx["skill_context"] = _fresh_skill_context(ctx["target_trait"], ctx["target_ancestry"])
        new_len = max(new_len, len(ctx["skill_context"]["full_text"]))
        req["request"]["body"]["messages"][1]["content"] = (
            head + MARKER + json.dumps(ctx, separators=(",", ":"), ensure_ascii=False)
        )

    OUT_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {OUT_MANIFEST}")
    print(f"traits: {len(manifest['requests'])}  | skill_context.full_text: {old_len} -> {new_len} chars")
    print("ontologies:", sorted(r["ontology"] for r in manifest["requests"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
