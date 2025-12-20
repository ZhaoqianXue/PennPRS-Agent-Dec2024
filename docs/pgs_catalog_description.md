# PGS Catalog
- https://www.pgscatalog.org/

## PGS Catalog Materials
1. Documentation: https://www.pgscatalog.org/about/
2. View available PGS Catalog downloads: https://www.pgscatalog.org/downloads/
3. Programmatic access to the Catalog metadata through our REST API: https://www.pgscatalog.org/rest/
4. Command line download via the pgscatalog_utils Python package: https://pypi.org/project/pgscatalog-utils/
5. Software for reproducible calculation of PGS Catalog and custom polygenic scores (pgsc_calc): https://pgsc-calc.readthedocs.io/en/latest/


## PGS Catalog FTP Structure
- The PGS Catalog FTP allows for consistent access to the bulk downloads, and is indexed by Polygenic Score (PGS) ID to allow programmatic access to score level data. The following diagram illustrates the FTP structure:
```md
ftp://ftp.ebi.ac.uk/pub/databases/spot/pgs
  ├── pgs_scores_list.txt (list of Polygenic Score IDs)
  ├── **metadata/**
  │     ├── pgs_all_metadata.xlsx
  │     ├── pgs_all_metadata_[sheet_name].csv (7 files)
  │     ├── pgs_all_metadata.tar.gz (xlsx + csv files)
  │     ├── **publications/** (metadata for large studies)
  │     └── **previous_releases/**
  └── **scores/**
        ├── **PGS000001/**
        │     ├── **Metadata/**
        │     │     ├── PGS000001_metadata.xlsx
        │     │     ├── PGS000001_metadata_[sheet_name].csv (7 files)
        │     │     ├── PGS000001_metadata.tar.gz (xlsx + csv files)
        │     │     └── **archived_versions/**
        │     └── **ScoringFiles/**
        │           ├── PGS000001.txt.gz
        │           ├── **archived_versions/**
        │           └── **Harmonized/**
        │                 ├── PGS000001_hmPOS_GRCh37.txt.gz
        │                 └── PGS000001_hmPOS_GRCh38.txt.gz
        ├── **PGS000002/**
        ·     ├─ ···
        ·     └─ ···
        ·
        └── **PGS00XXXX/**
              ├─ ···
              └─ ···
```

## PGS Catalog Metadata

Bulk download of the entire PGS Catalog's metadata, describing all PGS in terms of their publication source, samples used for development/evaluation, and related performance metrics. Download Metadata file.xlsx

The bulk download contains a single Excel file with multiple sheets describing each of the data types. The sheets are also provided as individual `.csv` files for easier import in analysis tools, and are provided on the FTP in the `metadata/` folder.

- **Readme**: PGS Catalog Release Date and Summary Information.
- **Publications**: Lists the publication sources for the PGS and PGS evaluations in the catalog.
- **EFO Traits**: Lists the ontology-mapped traits information for all PGS in the catalog.
- **Scores**: Lists all PGS scores and their associated metadata.
- **Score Development Samples**: Lists the samples used to create the PGS: samples used to discover the variant associations (GWAS), samples used for score development/training.
- **Performance Metrics**: Lists all performance metrics and the associated PGS Scores and Publications.
- **Evaluation Sample Sets**: Describes the samples used to evaluate PGS performance (refferenced as Polygenic Score Sample Sets (PSS).
- **Cohorts**: Lists all the cohorts used in the different samples.

## PGS Scoring Files
### Formatted Files
Each scoring file (variant information, effect alleles/weights) is formatted to be a gzipped **tab-delimited** text file, labelled by its PGS Catalog Score ID (e.g. `PGS000001.txt.gz`).

They can be found in URLs like this:
```md
ftp://ftp.ebi.ac.uk/pub/databases/spot/pgs/scores/PGS######/ScoringFiles/
```

#### Formatted Files — Header

The PGS Scoring Files header contains the following metadata:

**Header Fields Description:**

- `#format_version`: Version of the scoring file format, e.g. '2.0'
- `#pgs_id`: PGS identifier, e.g. 'PGS000001'
- `#pgs_name`: PGS name, e.g. 'PRS77BC' (optional)
- `#trait_reported`: Reported trait, e.g. 'Breast Cancer'
- `#trait_mapped`: Ontology trait name, e.g. 'breast carcinoma'
- `#trait_efo`: Ontology trait ID (EFO), e.g. 'EFO0000305'
- `#genome_build`: Genome build/assembly, e.g. 'GRCh38'
- `#variants_number`: Number of variants listed in the PGS
- `#weight_type`: Variant weight type, e.g. 'beta', 'OR/HR' (default 'NR')
- `#pgp_id`: PGS publication identifier, e.g. 'PGP000001'
- `#citation`: Information about the publication
- `#license`: License and terms of PGS use/distribution

**Note:** The `#trait_mapped` and `#trait_efo` metadata can contain multiple values (separated by a `|` "pipe"), e.g.:
- `#trait_mapped`=Ischemic stroke|stroke
- `#trait_efo`=HP_0002140|EFO_0000712

**Example of PGS Scoring Files header:**

```md
###PGS CATALOG SCORING FILE - see https://www.pgscatalog.org/downloads/#dl_ftp_scoring for additional information
**#format_version**=2.0
##POLYGENIC SCORE (PGS) INFORMATION
**#pgs_id**=PGS000348
**#pgs_name**=PRS_PrCa
**#trait_reported**=Prostate cancer
**#trait_mapped**=prostate carcinoma
**#trait_efo**=EFO_0001663
**#genome_build**=GRCh37
**#variants_number**=72
**#weight_type**=log(OR)
##SOURCE INFORMATION
**#pgp_id**=PGP000113
**#citation**=Black M et al. Prostate (2020). doi:10.1002/pros.24058
**#license**=Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0). © 2020 Ambry Genetics.
rsIDchr_namechr_positioneffect_alleleother_alleleeffect_weight...
```

#### Formatted Files — Columns

The scoring files contain the following columns with standardized headings:

| Column Header | Field Name | Field Requirement | Field Description |
|:--------------|:-----------|:------------------|:------------------|
| **Variant Description:** ||||
| `rsID` | dbSNP Accession ID (rsID) | Optional | The SNP's rs ID. This column also contains HLA alleles in the standard notation (e.g. HLA-DQA1*0102) that aren't always provided with chromosomal positions. |
| `chr_name` | Location - Chromosome | Required | Chromosome name/number associated with the variant. |
| `chr_position` | Location within the Chromosome | Required | Chromosomal position associated with the variant. |
| `effect_allele` | Effect Allele | Required | The allele that's dosage is counted (e.g. {0, 1, 2}) and multiplied by the variant's weight (**effect_weight**) when calculating score. The effect allele is also known as the 'risk allele'. Note: this does not necessarily need to correspond to the minor allele/alternative allele. |
| `other_allele` | Other allele(s) | Recommended | The other allele(s) at the loci. Note: this does not necessarily need to correspond to the reference allele. |
| `locus_name` | Locus Name | Optional | This is kept in for loci where the variant may be referenced by the gene (APOE e4). It is also common (usually in smaller PGS) to see the variants named according to the genes they impact. |
| `is_haplotype is_diplotype` | FLAG: Haplotype or Diplotype | Optional | This is a TRUE/FALSE variable that flags whether the effect allele is a haplotype/diplotype rather than a single SNP. Constituent SNPs in the haplotype are semi-colon separated. |
| `imputation_method` | Imputation Method | Optional | This described whether the variant was specifically called with a specific imputation or variant calling method. This is mostly kept to describe HLA-genotyping methods (e.g. flag SNP2HLA, HLA*IMP) that gives alleles that are not referenced by genomic position. |
| `variant_description` | Variant Description | Optional | This field describes any extra information about the variant (e.g. how it is genotyped or scored) that cannot be captured by the other fields. |
| `inclusion_criteria` | Score Inclusion Criteria | Optional | Explanation of when this variant gets included into the PGS (e.g. if it depends on the results from other variants). |
| **Weight Information:** ||||
| `effect_weight` | Variant Weight | Required | Value of the effect that is multiplied by the dosage of the effect allele (**effect_allele**) when calculating the score. Additional information on how the effect_weight was derived is in the **weight_type** field of the header, and score development method in the metadata downloads. |
| `is_interaction` | FLAG: Interaction | Optional | This is a TRUE/FALSE variable that flags whether the weight should be multiplied with the dosage of more than one variant. Interactions are demarcated with a _\_x\__ between entries for each of the variants present in the interaction. |
| `is_dominant` | FLAG: Dominant Inheritance Model | Optional | This is a TRUE/FALSE variable that flags whether the weight should be added to the PGS sum if there is at least 1 copy of the effect allele (e.g. it is a dominant allele). |
| `is_recessive` | FLAG: Recessive Inheritance Model | Optional | This is a TRUE/FALSE variable that flags whether the weight should be added to the PGS sum only if there are 2 copies of the effect allele (e.g. it is a recessive allele). |
| `dosage_0_weight` | Effect weight with 0 copy of the effect allele | Optional | Weights that are specific to different dosages of the **effect_allele** (e.g. {0, 1, 2} copies) can also be reported when the the contribution of the variants to the score is not encoded as additive, dominant, or recessive. In this case three columns are added corresponding to which variant weight should be applied for each dosage, where the column name is formated as **dosage_#_weight** where the **#** sign indicates the number of effect_allele copies. |
| `dosage_1_weight` | Effect weight with 1 copy of the effect allele | Optional | |
| `dosage_2_weight` | Effect weight with 2 copies of the effect allele | Optional | |
| **Other information:** ||||
| `OR HR` | Odds Ratio [OR], Hazard Ratio [HR] | Optional | Author-reported effect sizes can be supplied to the Catalog. If no other _effect\_weight_ is given the weight is calculated using the log(OR) or log(HR). |
| `allelefrequency_effect` | Effect Allele Frequency | Optional | Reported effect allele frequency, if the associated locus is a haplotype then haplotype frequency will be extracted. |
| `allelefrequency_effect_ Ancestry` | Population-specific effect allele frequency | Optional | Reported effect allele frequency in a specific population (described by the authors). |

**Note on Column Schema:** The scoring files have been edited to have consistent column headings based on a standardized schema. The column order may vary depending on which optional columns are included in each specific PGS file.

**Example of PGS Scoring Files data:**

_Scoring Files header_
```md
rsID        chr_name  chr_position  effect_allele  other_allele  effect_weight
rs2843152   1         2245570       G              C             -2.76009e-02
rs35465346  1         22132518      G              A             2.39340e-02
rs28470722  1         38386727      G              A             -1.74935e-02
rs11206510  1         55496039      T              C             2.93005e-02
rs9970807   1         56965664      C              T             4.70027e-02
rs61772626  1         57015668      A              G             -2.71202e-02
rs7528419   1         109817192     A              G             2.91912e-02
rs1277930   1         109822143     A              G             2.60105e-02
rs11102000  1         110298166     G              C             2.45969e-02
rs11810571  1         151762308     G              C             2.09215e-02
rs6689306   1         154395946     G              A             -1.97906e-02
rs72702224  1         154911689     G              A             -2.81310e-02
rs3738591   1         155764808     C              G             4.23731e-02
...
```

### Harmonized Files

Format: 2.0

PGS Scoring Files in the Catalog are currently provided in a consistent format with standardized column names and data types, along with information about the genome build given by authors. The variant-level information in PGS is often heterogeneously described and may lack chromosome/position information, contain a mix of positions and/or rsIDs, or be mapped to a genome build different from your sample genotypes. To make PGS easier to apply we have created a new set of files that contain **additional columns** with harmonized variant information (chromosome name and base pair position) and variant identifiers (updated rsID), in commonly used genome builds (GRCh37/hg19 and GRCh38/hg38) to make variant matching and PGS calculation easier.

The generation of these harmonized files is done by using the pgs-harmonizer tool. It is based on the Open Targets and GWAS Catalog Summary Statistics harmonizer pipelines. To harmonize the variant positions the pgs-harmonizer performs the following tasks:
- **Mapping rsIDs to chromosomal positions**: we use Ensembl (VCF files and REST APIs) on GRCh37 and GRCh38. We use Ensembl version **105**.
- **Liftover - mapping chromosomal positions across builds** (only when generating a Scoring file on a different genome build): we use the UCSC liftover tools via the Python library pyliftover.

The resultant files create new columns, indicating the source of the variant annotation (**hm_source**), as well as consistently annotated chromosome (**hm_chr**) / position (**hm_pos**), and rsID (**hm_rsID**) which can be used to match variants in your dataset along with the alleles (**effect_allele**, and **other_allele**).

**Warning:** Complex variants in the human leukocyte antigen (HLA) region (alleles/haplotypes/diplotypes) and larger copy number variants (CNVs) without explicit positions will have missing harmonized positions as they are not indexed in the ENSEMBL VCFs. For these variants we suggest using the author-reported annotations, specifically the **effect_allele** column, for variant matching in absence of positional information.

Harmonized scoring files can be accessed via our FTP, in a separate directory for each score:

```md
ftp://ftp.ebi.ac.uk/pub/databases/spot/pgs/scores/PGS######/ScoringFiles/Harmonized/
```

**Note:** The harmonized scoring file URLs can also be found for any Score result within the REST API.

#### Harmonized Files — File name

The file name is composed of 3 parts, separated by underscores (`_`):
1. **PGS ID**, e.g. 'PGS000001'
2. **Type of harmonized file**, e.g. 'hmPOS'
3. **Genome build**, either 'GRCh37' or 'GRCh38'

For instance: **PGS000001**`_`**hmPOS**`_`**GRCh37**.txt.gz

#### Harmonized Files — Header

**Note:** The first part of the header (before the line `##HARMONIZATION DETAILS`) is a copy-paste of the Scoring file header.

Here is a description of the PGS Harmonized Scoring Files header:

- `#format_version`: Version of the scoring file format, e.g. '2.0'
- `#pgs_id`: PGS identifier, e.g. 'PGS000001'
- `#pgs_name`: PGS name, e.g. 'PRS77BC' (optional)
- `#trait_reported`: trait, e.g. 'Breast Cancer'
- `#trait_mapped`: Ontology trait name, e.g. 'breast carcinoma'
- `#trait_efo`: Ontology trait ID (EFO), e.g. 'EFO0000305'
- `#genome_build`: Genome build/assembly, e.g. 'GRCh38'
- `#variants_number`: Number of variants listed in the PGS
- `#weight_type`: Variant weight type, e.g. 'beta', 'OR/HR' (default 'NR')
- `#pgp_id`: PGS publication identifier, e.g. 'PGP000001'
- `#citation`: Information about the publication
- `#license`: License and terms of PGS use/distribution - refers to the EMBL-EBI Terms of Use by default
- `#HmPOS_build`: Genome build of the harmonized file, e.g. 'GRCh38'
- `#HmPOS_date`: Date of the harmonized file creation, e.g. '2022-05-26'
- `#HmPOS_match_chr`: Number of entries matching and not matching the given chromosome, e.g. {"True": 5210, "False": 8}
- `#HmPOS_match_pos`: Number of entries matching and not matching the given position, e.g. {"True": 5210, "False": 8}

Column headers:
```
rsID...hm_sourcehm_rsIDhm_chrhm_poshm_inferOtherAllelehm_match_chrhm_match_pos
```

**Example of PGS Harmonized Scoring Files header:**

```md
###PGS CATALOG SCORING FILE - see https://www.pgscatalog.org/downloads/#dl_ftp_scoring for additional information
**#format_version**=2.0
##POLYGENIC SCORE (PGS) INFORMATION
**#pgs_id**=PGS000348
...
**#license**=Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0). © 2020 Ambry Genetics.
##HARMONIZATION DETAILS
**#HmPOS_build**=GRCh37
**#HmPOS_date**=2022-07-26
**#HmPOS_match_chr**={"True": 72, "False":0}
**#HmPOS_match_pos**={"True": 72, "False":0}
rsID...hm_sourcehm_rsIDhm_chrhm_poshm_inferOtherAllelehm_match_chrhm_match_pos
```

#### Harmonized Files — Additional Columns

The formatted scoring file (in the original genome build) has the following additional columns describing the variants in the **specified genome build** for each HmPOS file:

| Additional Column Header | Field Name | Field Description |
|:-------------------------|:-----------|:------------------|
| `hm_source` | Provider of the harmonized variant information | Data source of the variant position. Options include: ENSEMBL, liftover, author-reported _(if being harmonized to the same build)_. |
| `hm_rsID` | Harmonized rsID | Current rsID. Differences between this column and the author-reported column (rsID) indicate variant merges and annotation updates from dbSNP. |
| `hm_chr` | Harmonized chromosome name | Chromosome that the harmonized variant is present on, preferring matches to chromosomes over patches present in later builds. |
| `hm_pos` | Harmonized chromosome position | Chromosomal position (base pair location) where the variant is located, preferring matches to chromosomes over patches present in later builds. |
| `hm_inferOtherAllele` | Harmonized other alleles | If only the **effect_allele** is given we attempt to infer the non-effect/other allele(s) using Ensembl/dbSNP alleles. |
| `hm_match_chr` | FLAG: matching chromosome name | _Used for QC_. Only provided if the scoring file is being harmonized to the same genome build, and where the chromosome name is provided in the column **chr_name**. |
| `hm_match_pos` | FLAG: matching chromosome position | _Used for QC_. Only provided if the scoring file is being harmonized to the same genome build, and where the chromosome name is provided in the column **chr_position**. |

#### Example of PGS Harmonized File (GRCh37 file harmonized on GRCh38)

```md
###PGS CATALOG SCORING FILE - see https://www.pgscatalog.org/downloads/#dl_ftp_scoring for additional information
**#format_version**=2.0
##POLYGENIC SCORE (PGS) INFORMATION
**#pgs_id**=PGS000116
...
**#genome_build**=GRCh37
...
##HARMONIZATION DETAILS
**#HmPOS_build**=GRCh38
...
rsID         chr_name  chr_position  effect_allele  other_allele  effect_weight  hm_source  hm_rsID      hm_chr  hm_pos
rs1921       1          949608       A              G             -0.003965      ENSEMBL    rs1921       1       1014228
rs2710887    1          986443       T              C             -0.000846      ENSEMBL    rs2710887    1       1051063
rs11260596   1         1002434       T              C              0.000789      ENSEMBL    rs11260596   1       1067054
rs113355263  1         1069535       A              G             -0.001627      ENSEMBL    rs113355263  1       1134155
rs11260539   1         1109903       T              C              0.000170      ENSEMBL    rs11260539   1       1174523
...
```

