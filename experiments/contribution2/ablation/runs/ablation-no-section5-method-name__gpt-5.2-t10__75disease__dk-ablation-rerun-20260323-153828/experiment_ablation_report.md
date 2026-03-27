# Ablation Experiment Report: no-section5-method-name

## Experiment Setup

- **Ablation variant**: `no-section5-method-name`
- **Knowledge file**: `/Users/zhaoqianxue/Desktop/UPenn/PennPRS_Agent/experiments/contribution2/ablation/variants/no-section5-method-name.md`
- **Model**: gpt-5.2
- **Domain Knowledge**: Enabled (ablated variant)

## Overall Results

| Metric | Hit@1 | Hit@2 | Hit@3 | Hit@4 | Hit@5 |
|--------|-------|-------|-------|-------|-------|
| Modal Hit Rate | 33.3% | 56.0% | 64.0% | 74.7% | 77.3% |
| Trial Hit Rate | 31.6% | 54.4% | 62.3% | 71.2% | 75.5% |

**Normalized Ranking Score (NRS)**: 0.7320

## Per-Disease Results

| Disease | Modal PGS ID | Selection Freq | Hit@1 | Hit@3 | Hit@5 |
|---------|-------------|----------------|-------|-------|-------|
| abdominal aortic aneurysm | PGS000753 | 9/10 | N | N | Y |
| alcohol dependence | PGS002738 | 10/10 | Y | Y | Y |
| angina pectoris | PGS005052 | 7/10 | N | Y | Y |
| ankylosing spondylitis | PGS002089 | 5/10 | N | N | Y |
| aortic stenosis | PGS005252 | 8/10 | N | N | N |
| arthritis | PGS001135 | 10/10 | N | N | N |
| asthma | PGS002727 | 10/10 | N | N | N |
| atopic eczema | PGS002755 | 10/10 | N | N | Y |
| atrial fibrillation | PGS005168 | 10/10 | N | N | N |
| atrial flutter | PGS001263 | 10/10 | N | N | Y |
| autism spectrum disorder | PGS000327 | 10/10 | N | Y | Y |
| basal cell carcinoma | PGS000452 | 9/10 | N | Y | Y |
| bilirubin metabolism disease | PGS002032 | 10/10 | N | Y | Y |
| bipolar disorder | PGS002786 | 10/10 | Y | Y | Y |
| blood coagulation disease | PGS001033 | 10/10 | Y | Y | Y |
| breast carcinoma | PGS004153 | 7/10 | N | N | N |
| cervical carcinoma | PGS003428 | 10/10 | N | N | Y |
| chronic kidney disease | PGS002237 | 10/10 | N | N | N |
| chronic obstructive pulmonary disease | PGS001783 | 10/10 | Y | Y | Y |
| congenital vitamin k-dependent coagulation factors deficiency | PGS002034 | 10/10 | N | Y | Y |
| corneal dystrophy | PGS002042 | 10/10 | Y | Y | Y |
| coronary artery disease | PGS003725 | 8/10 | N | Y | Y |
| dementia | PGS005170 | 10/10 | N | Y | Y |
| depressive disorder | PGS003333 | 8/10 | N | Y | Y |
| dilated cardiomyopathy | PGS004951 | 6/10 | Y | Y | Y |
| dupuytren contracture | PGS002092 | 10/10 | Y | Y | Y |
| glaucoma | PGS004944 | 5/10 | N | N | Y |
| gout | PGS001789 | 5/10 | N | N | N |
| hashimoto's thyroiditis | PGS005271 | 10/10 | N | Y | Y |
| heart failure | PGS001790 | 4/10 | N | N | N |
| hip osteoarthritis | PGS002763 | 10/10 | Y | Y | Y |
| hodgkins lymphoma | PGS000639 | 10/10 | Y | Y | Y |
| hypertension | PGS001320 | 5/10 | N | N | N |
| hyperthyroidism | PGS005265 | 10/10 | N | Y | Y |
| hypertrophic cardiomyopathy | PGS004911 | 10/10 | Y | Y | Y |
| hypothyroidism | PGS005218 | 10/10 | N | Y | Y |
| iron metabolism disease | PGS002031 | 10/10 | Y | Y | Y |
| juvenile idiopathic arthritis | PGS000114 | 10/10 | Y | Y | Y |
| kidney cancer | PGS004908 | 10/10 | Y | Y | Y |
| kidney failure | PGS004562 | 6/10 | Y | Y | Y |
| knee osteoarthritis | PGS002767 | 10/10 | N | Y | Y |
| late-onset alzheimer's disease | PGS000054 | 7/10 | Y | Y | Y |
| lung cancer | PGS000078 | 9/10 | N | N | N |
| lupus erythematosus | PGS000328 | 5/10 | N | N | N |
| lymphoid leukemia | PGS000788 | 5/10 | N | N | Y |
| macular degeneration | PGS004606 | 10/10 | N | Y | Y |
| melanoma | PGS002247 | 5/10 | N | N | Y |
| myocardial infarction | PGS005039 | 10/10 | N | Y | Y |
| nasal cavity polyp | PGS004535 | 10/10 | N | Y | Y |
| nicotine dependence | PGS002037 | 10/10 | Y | Y | Y |
| nodular goiter | PGS005262 | 10/10 | N | Y | Y |
| obesity | PGS005235 | 7/10 | Y | Y | Y |
| osteoporosis | PGS002768 | 10/10 | N | Y | Y |
| otosclerosis | PGS002046 | 10/10 | Y | Y | Y |
| ovarian neoplasm | PGS000550 | 9/10 | N | N | N |
| parkinson disease | PGS000903 | 10/10 | Y | Y | Y |
| peripheral vascular disease | PGS005217 | 10/10 | Y | Y | Y |
| preeclampsia | PGS003586 | 10/10 | Y | Y | Y |
| prostate cancer | PGS004155 | 8/10 | N | N | N |
| psoriasis | PGS001312 | 10/10 | N | N | N |
| psoriatic arthritis | PGS001287 | 7/10 | Y | Y | Y |
| pulmonary embolism | PGS001280 | 8/10 | N | Y | Y |
| pulmonary fibrosis | PGS001791 | 10/10 | N | Y | Y |
| retinopathy | PGS002027 | 10/10 | N | N | N |
| rheumatoid arthritis | PGS004163 | 10/10 | N | Y | Y |
| sarcoidosis | PGS000922 | 10/10 | N | Y | Y |
| skin carcinoma in situ | PGS000471 | 10/10 | Y | Y | Y |
| sleep apnea | PGS005220 | 9/10 | Y | Y | Y |
| squamous cell carcinoma | PGS000461 | 10/10 | N | N | Y |
| testicular carcinoma | PGS000604 | 10/10 | N | N | N |
| thyroid carcinoma | PGS005259 | 6/10 | N | N | Y |
| urinary bladder cancer | PGS000611 | 7/10 | N | N | N |
| urolithiasis | PGS004563 | 10/10 | Y | Y | Y |
| uterine cancer | PGS003381 | 5/10 | N | Y | Y |
| vitiligo | PGS000738 | 9/10 | N | Y | Y |

## Cost

