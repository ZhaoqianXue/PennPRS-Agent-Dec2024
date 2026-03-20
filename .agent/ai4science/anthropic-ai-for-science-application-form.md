---
source_url: https://docs.google.com/forms/d/e/1FAIpQLSfwDGfVg2lHJ0cc0oF_ilEnjvr_r4_paYi7VLlr5cLNXASdvA/viewform?usp=header
---

# Application Form - Anthropic's AI for Science Program

Thank you for your interest in Anthropic's AI for Science Program. This program provides API credits to researchers working on high-impact scientific projects, with a particular focus on biology and life sciences applications.

## About this Program

The AI for Science program offers API credits to qualified nonprofit and academic researchers who will be selected based on their scientific credentials, the potential impact of their proposed research, and AI's ability to meaningfully accelerate their work. We are particularly interested in supporting applications in biology and life sciences where AI can assist in accelerating processes related to understanding complex biological systems, analyzing genetic data, accelerating drug discovery especially for some of the largest global disease burdens, increasing agricultural productivity, and more.

This program provides free API credits for our standard model suite. Applicants through this program do not receive exemption from our Usage Policy, our Trust & Safety team will follow our standard enforcement procedures and take action whenever an organization's prompt activity hits our violation rate thresholds.

## About our Process

1. We evaluate submissions on the first Monday of each month. This schedule helps us manage the program sustainably. Please note that if this timeline poses a significant obstacle for the applicant, it does not block them from simply purchasing API credits in the interim.
2. If successful, after a 30 minute video call, we will apply up to $50,000 API credits to your account. The specific amount will be communicated as part of the evaluation process.
3. Given the substantial number of applications we receive, we regret that we cannot provide individual responses to unapproved submissions. However, we appreciate the time and effort put into each submission and will carefully review all entries.

---

## Contact information

_Please enter academic emails and credentials where possible_

Sign in to Google to save your progress. Learn more

\* Indicates required question

---

**Email \***

**Answer**

Jin.Jin@Pennmedicine.upenn.edu





---

**Name of primary contact \***

**Answer**

Jin Jin





---

**Name of organization/research institution \***

**Answer**

University of Pennsylvania, Perelman School of Medicine, Department of Biostatistics, Epidemiology and Informatics





---

**Position/title at organization \***

**Answer**

Assistant Professor of Biostatistics





---

**Website of organization/research group, link to Google Scholar or GitHub \***

**Answer**

- Lab / personal site: https://jin93.github.io/
- Google Scholar: https://scholar.google.com/citations?user=mm7KQPYAAAAJ&hl=en
- GitHub (representative): https://github.com/Jin93
- Penn DBEI faculty profile: https://dbei.med.upenn.edu/staff/jin-jin-phd/





---

**Where did you hear about this program?**

**Answer**

Learned about this program through a colleague in my department.





---

## Project information

---

**Project title \***

**Answer**

PennPRS Agent: Evidence-Guided AI Co-Scientist for Polygenic Risk Score Recommendation in Precision Medicine




---

**Scientific field(s) (select all that apply) \***


- [x] Biology / Life Sciences
- [ ] Chemistry
- [x] Medicine/Healthcare
- [ ] Environmental Science
- [ ] Physics
- [ ] Earth Science
- [x] Computer Science
- [ ] Other: _______________




---

**Which Organization ID would you like the credits applied to? Note: this can be found under https://console.anthropic.com/settings/organization. It will look something like: 1bc14c5d-6442-4fa9-bgjj-c1ejei29aef01v. If you have not yet set up an account, please set up an account at https://console.anthropic.com before submitting this form. \***

**Answer**

Your answer





---

## Research Team

---

**In less than 300 words, please provide a description of the research team, including relevant expertise and credentials in both the scientific domain and AI/ML experience \***

**Answer**

This project is led by Jin Jin, Ph.D., Assistant Professor of Biostatistics at the University of Pennsylvania Perelman School of Medicine. Dr. Jin is an NIH K99/R00-funded statistical geneticist whose research centers on multi-ancestry disease risk prediction and translating large-scale human genetics into clinically relevant prediction tools. Her group developed and maintains PennPRS, the first cloud computing platform for privacy-preserving PRS model training and application, which has publicly released pre-trained models for over 8,000 phenotypes across multiple ancestry groups. She has published multi-ancestry PRS methods in Nature Genetics and Nature Communications, and leads the scientific direction of this project, including study design, benchmark construction, and statistical validation.

The team’s AI/ML and engineering capability is led by Zhaoqian Xue, Research Assistant at the University of Pennsylvania and lead LLM systems engineer for the PennPRS Agent. Xue is responsible for agent architecture, context engineering, tool-integrated workflows, evaluation pipelines, and experiment automation. Together, the team combines deep expertise in statistical genetics and PRS methodology with hands-on LLM engineering, enabling both rigorous scientific evaluation and production-grade development of domain-specialized AI workflows for genetic risk prediction.





---

**Please list the key team members who will be using Claude for this research (name, title, and brief description of role in project) \***

**Answer**

- **Jin Jin** — Assistant Professor of Biostatistics (PI). NIH K99/R00-funded statistical geneticist and developer of PennPRS, MUSSEL, and MRLE; leads scientific direction, study design, benchmark construction, statistical validation, and integration of PRS methodology with clinically relevant risk prediction.
- **Zhaoqian Xue** — Research Assistant, University of Pennsylvania (Jin Jin Lab). Lead LLM systems engineer for this project, responsible for agent architecture, prompt/context engineering, tool orchestration, evaluation and benchmarking infrastructure, experiment automation, and end-to-end engineering of Claude-assisted research workflows.





---

**Please provide links to Google Scholar profiles or other academic/professional profiles of key team members**

**Answer**

- **Jin Jin** — Lab / personal site: https://jin93.github.io/ ; Google Scholar: https://scholar.google.com/citations?user=mm7KQPYAAAAJ&hl=en ; Penn DBEI faculty profile: https://dbei.med.upenn.edu/staff/jin-jin-phd/
- **Zhaoqian Xue** — Google Scholar: https://scholar.google.com/citations?user=HG63crgAAAAJ&hl=en ; LinkedIn: https://www.linkedin.com/in/zhaoqian-xue-531982211?lipi=urn%3Ali%3Apage%3Ad_flagship3_profile_view_base_contact_details%3Boh7xJhk3RI61NA5PQKkyDw%3D%3D





---

## Research Proposal

---

**In less than 500 words, please describe your research project, including:**

- Scientific question or problem being addressed
- Methodology and approach
- Expected outcomes and deliverables
- Timeline for completion \*

**Answer**

Polygenic risk scores (PRS) are among the most promising tools for realizing the vision of genomic medicine—using an individual's genetic information to predict disease risk, enable earlier intervention, and guide prevention for complex conditions such as cardiovascular disease, cancers, diabetes, and neurodegenerative disorders. Thousands of PRS models now exist (the PGS Catalog hosts over 5,000), yet a critical translational bottleneck persists: for most diseases, determining which published model is actually best suited for a given population still requires labor-intensive expert review of heterogeneous metadata, ancestry composition, and performance benchmarks. This process does not scale to the breadth of diseases and populations that stand to benefit, leaving many—especially those involving underserved ancestries—without adequate genetic risk prediction tools.

Our project, PennPRS Agent, addresses this bottleneck by developing an AI co-scientist that can reliably select the best available PRS model across a large and diverse set of diseases. The central scientific question is whether an LLM, equipped with structured genetic evidence and domain context, can match expert-level judgment in recommending high-quality PRS models—and, when direct models are unavailable, identify scientifically plausible alternatives through shared genetic architecture across diseases. Rather than replacing human expertise, this system amplifies it: enabling expert-level decisions at a scale and speed far beyond what manual review can achieve.

Expected outcomes include: (1) the first systematic benchmark of PGS Catalog models evaluated on a unified, large-scale cohort (All of Us); (2) an AI-driven recommendation workflow validated against this benchmark across 75+ diseases; (3) empirical evaluation of how domain knowledge and structured evidence improve recommendation quality; and (4) integration with PennPRS, our cloud computing platform for PRS training, to provide end-to-end support when published models are insufficient.

Timeline: We are in the core evaluation phase. By Q2 2026, we will complete the benchmark and recommendation evaluation. By Q3 2026, we will finalize the integrated workflow and submit the manuscript to Nature Genetics.





---

**How specifically will Claude's capabilities be used in your research? Please be as detailed as possible about the tasks Claude will perform and how this integrates with your research workflow (1-2 sentences, 300 words max) \***

**Answer**

Claude functions as a scientific reasoning partner—not merely a data analysis tool—that accelerates the full arc of our research workflow. Specifically, Claude performs three core tasks: (1) Evidence synthesis: integrating heterogeneous PRS model metadata, benchmark results, disease ontology mappings, and genetic correlation data to evaluate and rank candidate models for each disease. (2) Cross-disease reasoning: when direct models are unavailable or insufficient, Claude leverages genetic architecture evidence to identify related diseases whose PRS models may transfer, producing biologically grounded justifications. (3) Scientific reporting: generating structured recommendation reports and manuscript-ready analyses across the full disease benchmark. Claude's extended context window and multi-step reasoning capabilities are uniquely well-suited for this work, as each recommendation requires synthesizing dozens of model-level features and cross-disease evidence within a single coherent reasoning chain. In practice, Claude drives the recommendation pipeline end to end, allowing the team to scale evaluation across 75+ diseases where manual expert review would be limited to a handful.





---

**How will Claude significantly accelerate or enhance your research compared to existing methods or tools? (1-2 sentences, 200 words max) \***

**Answer**

Claude compresses work that would otherwise require months of manual expert review into a scalable, consistent workflow. Today, selecting the best PRS model for a single disease requires a domain expert to review dozens of candidate models across heterogeneous metadata—a process that takes hours per disease and does not scale. Claude enables us to perform this evaluation across 75+ diseases systematically, surface evidence gaps that manual review would miss, and produce structured outputs ready for scientific analysis. Compared with conventional spreadsheet-based comparison or literature review, Claude provides a qualitative leap in both throughput and consistency, accelerating manuscript-ready analyses on a timeline that would be infeasible with existing methods.





---

## Impact Assessment

---

**Please describe the potential scientific impact of your research if successful (1-2 sentences, 200 words max) \***

**Answer**

If successful, this research would directly advance the translation of human genetics into preventive medicine—one of the most impactful applications of AI in the life sciences. By establishing the first validated, AI-driven framework for PRS model selection across a broad disease landscape, this work would improve how researchers and clinicians identify the best genetic risk prediction tools for complex diseases including cardiovascular disease, cancers, and diabetes. It would also systematically reveal where existing PRS models are weak or missing, particularly for underserved ancestries and understudied diseases, directing future methodological effort where it is most needed and helping to make genomic risk prediction a more equitable and routine component of healthcare.





---

**Does your research have potential applications beyond pure scientific discovery? If so, please describe any possible practical applications, societal benefits, or paths to scale your research (1-2 sentences, 200 words max) \***

**Answer**

Yes. Beyond pure scientific discovery, this work could function as a decision-support and research-infrastructure layer for biobanks, academic medical centers, and population health studies by helping investigators more consistently identify suitable PRS models, recognize when published models are weak or missing, and move more efficiently toward follow-up validation or model training. Because it is built on public genetic resources and a deployable PennPRS workflow, it also has a clear path to scale as a low-marginal-cost platform for more transparent, accessible, and equitable use of genomic risk prediction, especially for diseases and populations that are currently underserved.





---

**How do you plan to measure the success of using Claude in your research? Please list specific metrics or objectives that would indicate successful integration of our API (1-2 sentences, 200 words max) \***

**Answer**

We will measure success by whether Claude's recommendations consistently identify the best-performing PRS models across a large benchmark of diseases, as evaluated against empirical performance in the All of Us cohort. Specific objectives include: (1) recommendation accuracy—whether Claude's top-ranked model matches or closely approximates the empirically best model across the benchmark disease set; (2) consistency—whether repeated runs produce stable, reproducible recommendations; (3) output quality—low rates of invalid, unsupported, or non-interpretable outputs; and (4) research efficiency—whether Claude measurably reduces the time required to synthesize fragmented genetic evidence into transparent reports and manuscript-ready analyses, allowing us to scale reproducible evaluation to substantially more diseases and populations within the same project timeline.





---

## Resource Requirements

---

**How much money in API credits do you anticipate you will need? Please provide information on how this credit amount will lead to impact in your project \***

**Answer**

We anticipate needing approximately $10,000–$15,000 in API credits. The majority will support large-scale Claude-assisted evaluation across 75+ diseases with multiple recommendation configurations, including repeated benchmark runs, ablation analyses comparing different evidence and context conditions, and generation of transparent research reports. A smaller portion will support Claude-assisted scientific writing and manuscript preparation for submission to Nature Genetics. This level of support would allow us to validate and iterate on the recommendation workflow at a scale and depth that would be difficult to achieve within a typical academic budget, accelerating the development of a reproducible and scalable resource for genetic risk prediction.





---

## Biosecurity assessment

---

**Does your research involve any of the following? \***

- [ ] Pathogen research or virology
- [ ] Drug resistance studies
- [ ] Toxicology
- [ ] Synthetic biology
- [x] None of the above




---

**If you checked any of the above, please explain the biosecurity safeguards in place for your research and confirm that your work complies with all relevant institutional and regulatory requirements (1-2 sentences, 200 words max)**

**Answer**

Your answer





---

## Additional information

---

**Is there anything else you would like the review committee to know about your application?**

**Answer**

Your answer
