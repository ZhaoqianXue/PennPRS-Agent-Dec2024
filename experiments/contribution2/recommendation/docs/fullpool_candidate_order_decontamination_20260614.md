# Fullpool candidate-order decontamination - 2026-06-14

## Finding

The previous single-stage fullpool requests were order-contaminated: the
LLM-visible `direct_models.models` order matched `benchmark_ranked_ids`.

- full44 old dry-run: 44/44 candidate lists matched benchmark order; benchmark
  top1 appeared at position 1 in 44/44.
- target10 old dry-run: 10/10 candidate lists matched benchmark order; benchmark
  top1 appeared at position 1 in 10/10.

Those runs are therefore usable only as contaminated order ablations, not as
clean method-performance evidence.

## Fix

Production prepare now defaults to `stable_hash_shuffle`:

```text
sha256(candidate_order_seed || ontology || pgs_id)
```

This preserves the candidate set but makes the LLM-visible order independent of
benchmark rank, publication date, and PGS ID lexicographic order. Explicit
ablation modes remain available through `--candidate-order benchmark`,
`--candidate-order reverse_benchmark`, and `--candidate-order lexicographic`.

Each manifest/request now records:

- `candidate_order_source`
- `candidate_order_seed`
- `candidate_order_matches_benchmark_order`
- `benchmark_top1_position_in_candidate_order`

## Request Inspection

### target10 stable hash

Run:

```text
with-domain-gpt-5.4-mini-t1__44disease__target10-cleanorder-dryrun-20260614
```

Result:

- candidate order equals benchmark order: 0/10
- benchmark top1 at candidate position 1: 0/10
- top1 positions: 138, 32, 89, 25, 32, 29, 16, 13, 11, 16
- request-context order mismatches: 0
- LLM-visible benchmark/top1 text leakage: 0

### full44 stable hash

Run:

```text
with-domain-gpt-5.4-mini-t1__44disease__full44-cleanorder-dryrun-20260614
```

Result:

- candidate order equals benchmark order: 0/44
- benchmark top1 at candidate position 1: 3/44
- request-context order mismatches: 0
- LLM-visible benchmark/top1 text leakage: 0

### full44 reverse benchmark ablation

Run:

```text
with-domain-gpt-5.4-mini-t1__44disease__full44-reverseorder-dryrun-20260614
```

Result:

- candidate order equals benchmark order: 0/44
- candidate order equals reversed benchmark order: 44/44
- benchmark top1 at candidate position 1: 0/44
- LLM-visible benchmark/top1 text leakage: 0

## API Runs

All API runs used `gpt-5.4-mini`.

| Run | Candidate order | Hit@1 | Hit@5 | Input tokens | Cached input | Output tokens | USD |
|---|---:|---:|---:|---:|---:|---:|---:|
| target10-singlefullpool-guardrail-20260614-20260614-065928 | contaminated benchmark order | 4/10 | 7/10 | 528,986 | 0 | 2,147 | 0.4064 |
| target10-cleanorder-singlefullpool-20260614-20260614-163721 | stable_hash_shuffle | 0/10 | 0/10 | 528,986 | 0 | 2,230 | 0.4068 |
| full44-singlefullpool-guardrail-20260614-20260614-065945 | contaminated benchmark order | 29/44 | 36/44 | 1,157,724 | 525,824 | 9,275 | 0.5551 |
| full44-cleanorder-singlefullpool-20260614-20260614-163739 | stable_hash_shuffle | 7/44 | 22/44 | 1,157,724 | 525,824 | 9,405 | 0.5557 |
| full44-reverseorder-singlefullpool-20260614-20260614-163849 | reverse_benchmark | 7/44 | 16/44 | 1,157,724 | 0 | 9,582 | 0.9114 |

New API cost in this decontamination pass:

```text
target10 stable hash: 0.4068 USD
full44 stable hash:  0.5557 USD
full44 reverse:      0.9114 USD
total:               1.8739 USD
```

## Interpretation

The clean full44 baseline is 7/44 Hit@1, not 29/44. The clean target10 baseline
is 0/10 Hit@1, not 4/10. The old 29/44 and 4/10 figures should be treated as
contaminated order-ablation results.

Hash and reverse full44 both reach 7/44 Hit@1, but their winners differ in
27/44 diseases. That means the current fullpool selector remains order-sensitive
even after benchmark-order leakage is removed. The next improvement target is
order-robust architecture, not additional skill wording.

## General/no-skill decontamination

The old General/no-skill manifests were also contaminated.

- `without-domain-gpt-5.4-mini-t1__44disease__general-newprompt-mini-20260614`:
  44/44 candidate orders matched benchmark order; benchmark top1 appeared first
  in 44/44.
- `with-domain-gpt-5.4-mini-t1__44disease__full44-restoredguardrail-noskill-dryrun-20260614-efoclean44`:
  44/44 candidate orders matched benchmark order; benchmark top1 appeared first
  in 44/44.
- `pairwise-rerank-gpt-5.4-mini-t1__44disease__full44-restoredguardrail-noskill-singlefullpool-20260614-20260614-074314`:
  22/44 Hit@1, 31/44 Hit@5, but contaminated by the upstream candidate order.

Clean General/no-skill manifests:

| Manifest | Candidate order | equals benchmark | top1 first | visible benchmark leakage | visible skill leakage |
|---|---:|---:|---:|---:|---:|
| `without-domain-gpt-5.4-mini-t1__44disease__general-cleanorder-dryrun-20260614` | stable_hash_shuffle / `pennprs-order-v1` | 0/44 | 3/44 | 0 | 0 |
| `without-domain-gpt-5.4-mini-t1__44disease__target10-general-cleanorder-dryrun-20260614` | stable_hash_shuffle / `pennprs-order-v1` | 0/10 | 0/10 | 0 | 0 |

Clean General/no-skill API runs:

| Run | Hit@1 | Hit@5 | Input tokens | Cached input | Output tokens | USD |
|---|---:|---:|---:|---:|---:|---:|
| `full44-general-cleanorder-singlefullpool-20260614-20260614-165557` | 7/44 | 25/44 | 940,056 | 0 | 6,734 | 0.7353 |
| `target10-general-cleanorder-singlefullpool-20260614-20260614-165824` | 0/10 | 0/10 | 479,523 | 475,648 | 1,427 | 0.0450 |

Clean same-order comparison at seed `pennprs-order-v1`:

| Arm | Hit@1 | Hit@5 |
|---|---:|---:|
| PRS Agent fullpool | 7/44 | 22/44 |
| General/no-skill fullpool | 7/44 | 25/44 |

Under clean order, this does not support a strong skill advantage for the current
single-stage fullpool selector.

## PRS Agent 3-seed order sensitivity

Additional PRS Agent full44 clean stable-hash runs:

| Seed | Run | equals benchmark | top1 first | Hit@1 | Hit@5 | USD |
|---|---|---:|---:|---:|---:|---:|
| `pennprs-order-v1` | `full44-cleanorder-singlefullpool-20260614-20260614-163739` | 0/44 | 3/44 | 7/44 | 22/44 | 0.5557 |
| `pennprs-order-v2` | `full44-cleanorder-seed2-singlefullpool-20260614-20260614-165701` | 0/44 | 3/44 | 11/44 | 24/44 | 0.9114 |
| `pennprs-order-v3` | `full44-cleanorder-seed3-singlefullpool-20260614-20260614-165731` | 0/44 | 3/44 | 8/44 | 23/44 | 0.9115 |

Winner stability across the three clean PRS Agent seeds:

- same winner in 3/3 seeds: 10/44 diseases
- same winner in 2/3 seeds: 16/44 diseases
- all three winners distinct: 18/44 diseases
- pairwise same-winner overlap: 15-16/44

Upper-bound diagnostics from the three clean PRS Agent seeds:

- oracle Hit@1 if any seed picked benchmark top1: 14/44
- oracle Hit@5 if any seed picked benchmark top5: 31/44
- all-three-seeds Hit@1 agreement: 3/44
- deterministic plurality vote with seed-order tiebreak: 10/44 Hit@1, 24/44 Hit@5

Interpretation: there is real order sensitivity, but also extractable signal. A
position-balanced multi-order aggregator could plausibly improve over one seed,
but the 3-seed oracle ceiling is still far below the contaminated 29/44 result.

Additional API cost after the first decontamination pass:

```text
General full44 clean:      0.7353 USD
PRS Agent full44 seed v2:  0.9114 USD
PRS Agent full44 seed v3:  0.9115 USD
General target10 clean:    0.0450 USD
subtotal:                  2.6032 USD
```

Total API cost recorded across both decontamination passes:

```text
first pass subtotal:       1.8739 USD
second pass subtotal:      2.6032 USD
total:                     4.4771 USD
```

## Verification

```text
54 passed, 6 warnings
```

Command:

```text
python -m pytest tests/unit/test_within_hit1_guardrails.py \
  tests/unit/test_general_biomedical_llm_routing.py \
  tests/unit/test_system_prompts.py \
  tests/unit/test_pgs_single_record.py \
  tests/unit/test_pennprs_agent_service.py -q
```
