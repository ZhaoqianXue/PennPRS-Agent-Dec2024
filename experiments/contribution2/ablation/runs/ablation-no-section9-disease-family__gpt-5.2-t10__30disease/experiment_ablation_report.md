# Ablation Experiment Report: no-section9-disease-family

## Experiment Setup

- **Ablation variant**: `no-section9-disease-family`
- **Knowledge file**: `/Users/zhaoqianxue/Desktop/UPenn/PennPRS_Agent/experiments/contribution2/ablation/variants/no-section9-disease-family.md`
- **Model**: gpt-5.2
- **Domain Knowledge**: Enabled (ablated variant)

## Overall Results

| Metric | Hit@1 | Hit@2 | Hit@3 | Hit@4 | Hit@5 |
|--------|-------|-------|-------|-------|-------|
| Modal Hit Rate | 46.7% | 70.0% | 76.7% | 86.7% | 93.3% |
| Trial Hit Rate | 47.7% | 71.7% | 78.3% | 84.7% | 92.3% |

**Normalized Ranking Score (NRS)**: 0.8008

## Per-Disease Results

| Disease | Modal PGS ID | Selection Freq | Hit@1 | Hit@3 | Hit@5 |
|---------|-------------|----------------|-------|-------|-------|
| abdominal aortic aneurysm | PGS003973 | 4/10 | Y | Y | Y |
| age-related macular degeneration | PGS004606 | 10/10 | Y | Y | Y |
| alcohol dependence | PGS002738 | 10/10 | Y | Y | Y |
| ankylosing spondylitis | PGS002089 | 5/10 | N | N | Y |
| aortic stenosis | PGS005254 | 10/10 | Y | Y | Y |
| cervical carcinoma | PGS003428 | 10/10 | N | N | Y |
| cutaneous melanoma | PGS003382 | 10/10 | Y | Y | Y |
| graves disease | PGS005265 | 10/10 | N | Y | Y |
| hashimoto's thyroiditis | PGS005271 | 10/10 | N | Y | Y |
| hodgkins lymphoma | PGS000639 | 10/10 | Y | Y | Y |
| hypertrophic cardiomyopathy | PGS004911 | 10/10 | Y | Y | Y |
| hypothyroidism | PGS005218 | 6/10 | N | Y | Y |
| juvenile idiopathic arthritis | PGS000114 | 10/10 | Y | Y | Y |
| kidney cancer | PGS004908 | 10/10 | Y | Y | Y |
| late-onset alzheimer's disease | PGS000053 | 10/10 | N | N | Y |
| nodular goiter | PGS005262 | 10/10 | N | Y | Y |
| obesity | PGS002033 | 5/10 | N | N | Y |
| obstructive sleep apnea | PGS005220 | 8/10 | Y | Y | Y |
| open-angle glaucoma | PGS001797 | 10/10 | N | Y | Y |
| peripheral vascular disease | PGS002055 | 6/10 | N | Y | Y |
| preeclampsia | PGS003586 | 10/10 | Y | Y | Y |
| prostate cancer | PGS004155 | 6/10 | N | N | N |
| pulmonary embolism | PGS001280 | 10/10 | N | Y | Y |
| renal carcinoma | PGS004908 | 10/10 | Y | Y | Y |
| skin carcinoma in situ | PGS000471 | 10/10 | Y | Y | Y |
| sleep apnea | PGS005220 | 10/10 | Y | Y | Y |
| testicular neoplasm | PGS000604 | 10/10 | N | N | N |
| thyroid carcinoma | PGS005259 | 9/10 | N | N | Y |
| uterine carcinoma | PGS003381 | 10/10 | N | Y | Y |
| vitiligo | PGS000738 | 10/10 | N | Y | Y |

## Cost

