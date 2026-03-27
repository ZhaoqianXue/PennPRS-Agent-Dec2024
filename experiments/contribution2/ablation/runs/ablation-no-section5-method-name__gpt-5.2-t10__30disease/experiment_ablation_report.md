# Ablation Experiment Report: no-section5-method-name

## Experiment Setup

- **Ablation variant**: `no-section5-method-name`
- **Knowledge file**: `/Users/zhaoqianxue/Desktop/UPenn/PennPRS_Agent/experiments/contribution2/ablation/variants/no-section5-method-name.md`
- **Model**: gpt-5.2
- **Domain Knowledge**: Enabled (ablated variant)

## Overall Results

| Metric | Hit@1 | Hit@2 | Hit@3 | Hit@4 | Hit@5 |
|--------|-------|-------|-------|-------|-------|
| Modal Hit Rate | 56.7% | 76.7% | 86.7% | 90.0% | 93.3% |
| Trial Hit Rate | 56.0% | 76.0% | 85.0% | 88.0% | 91.7% |

**Normalized Ranking Score (NRS)**: 0.8597

## Per-Disease Results

| Disease | Modal PGS ID | Selection Freq | Hit@1 | Hit@3 | Hit@5 |
|---------|-------------|----------------|-------|-------|-------|
| abdominal aortic aneurysm | PGS003972 | 7/10 | N | Y | Y |
| age-related macular degeneration | PGS004606 | 10/10 | Y | Y | Y |
| alcohol dependence | PGS002738 | 10/10 | Y | Y | Y |
| ankylosing spondylitis | PGS001267 | 9/10 | N | Y | Y |
| aortic stenosis | PGS005254 | 10/10 | Y | Y | Y |
| cervical carcinoma | PGS003428 | 10/10 | N | N | Y |
| cutaneous melanoma | PGS003382 | 10/10 | Y | Y | Y |
| graves disease | PGS005265 | 10/10 | N | Y | Y |
| hashimoto's thyroiditis | PGS005271 | 10/10 | N | Y | Y |
| hodgkins lymphoma | PGS000639 | 10/10 | Y | Y | Y |
| hypertrophic cardiomyopathy | PGS004911 | 10/10 | Y | Y | Y |
| hypothyroidism | PGS005218 | 9/10 | N | Y | Y |
| juvenile idiopathic arthritis | PGS000114 | 10/10 | Y | Y | Y |
| kidney cancer | PGS004908 | 10/10 | Y | Y | Y |
| late-onset alzheimer's disease | PGS000054 | 10/10 | Y | Y | Y |
| nodular goiter | PGS005262 | 10/10 | N | Y | Y |
| obesity | PGS005235 | 7/10 | Y | Y | Y |
| obstructive sleep apnea | PGS005220 | 10/10 | Y | Y | Y |
| open-angle glaucoma | PGS004944 | 10/10 | Y | Y | Y |
| peripheral vascular disease | PGS005217 | 9/10 | Y | Y | Y |
| preeclampsia | PGS003586 | 10/10 | Y | Y | Y |
| prostate cancer | PGS004155 | 9/10 | N | N | N |
| pulmonary embolism | PGS001280 | 10/10 | N | Y | Y |
| renal carcinoma | PGS004908 | 10/10 | Y | Y | Y |
| skin carcinoma in situ | PGS000471 | 10/10 | Y | Y | Y |
| sleep apnea | PGS005220 | 10/10 | Y | Y | Y |
| testicular neoplasm | PGS000604 | 10/10 | N | N | N |
| thyroid carcinoma | PGS005259 | 6/10 | N | N | Y |
| uterine carcinoma | PGS003381 | 10/10 | N | Y | Y |
| vitiligo | PGS000738 | 10/10 | N | Y | Y |

## Cost

