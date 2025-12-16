# PennPRS_Agent, use ADRD as example

## Users
- User having indiviual-level data (AD label and genetic data), deployed locally.
- If no indiviual-level data, we have in-house data can be used.
- User may also have GWAS summary statsitcis of interest.

## Focusing
- Risk prediction and stratification.
- Omics data (association and prediction and stratification).

## Function
### Function(1): Benchmarking AD PRS Methods
- Benchmarking AD PRS methods on your local data (PennPRS FinnGen models, use UKB as testing data);
- AD GWAS data resources (FinnGen for now) and PRS methods.

### Function(2): The One: ensemble models cross phenotypes
- (PennPRS models for now)

### Function(3): Proteomics PRS Models
- Protomics PRS models for AD, do marginal proteins, also can we do multiple proteins together?
- Pertentially combine with "The One"
- (PennPRS models for now)

### Function(4): Training PRS Models
- Train PRS models (provide their own GWAS summary statsitcis, no need to click on our website).
- Learn about PennPRS https://pennprs.org/ and PGS Catalog https://www.pgscatalog.org/ then setup the agent workflow. 
- Function(4)Workflow：
    1. input：
        - 首先告诉user PennPRS_Agent 有已经train好的prs model （来自 PennPRS https://pennprs.org/result 和 PGS Catalog https://www.pgscatalog.org/ ） ，并且向用户推荐PennPRS_Agent已有的model或者让用户描述需求后向用户推荐PennPRS_Agent已有的model；
        - 如果user不想使用PennPRS_Agent已有的model，那就允许用户自己训练；
    2. training：
        - 如果user选择PennPRS_Agent已有的model，那就不用训练；
        - 如果user选择自己训练，那就调用PennPRS https://pennprs.org/ 的API（user可以选择PennPRS的GWAS Summary Statistics Data https://pennprs.org/data 也可以上传user自己的GWAS Summary Statistics Data；
    3. output：
        - user无论是选择PennPRS_Agent已有的model，还是自己train model，得到结果后都生成一个report包含model的feature，然后询问user是否要做evaluation（如果要就跳转到Function(1)）。



(Use PGS Catalog but not PennPRS at Function(4))

## Random thoughts
- PennPRS https://pennprs.org/ and PGS Catalog https://www.pgscatalog.org/.
- Pathway analysis.
- UKB-RAP and AOU deployment, for now, we do it locally.
- Can we make it smarter? Which will be useful for certain tasks.
- Follow-up post-PRS analysis code.

# Task
- 请你用中文介绍一下4个Function分别是什么。
- 我的任务是实现Function(4): Training PRS Models，请你用中文解释一下这部分应该做什么，我并不是很理解我的任务。
- Function(4): Training PRS Models 应该被分为两部分： 非Agent部分 & Agent部分 。
- 首先实现非Agent部分，暂时不实现Agent部分，在完成非Agent部分后再开始Agent部分。
- 不需要提供代码。