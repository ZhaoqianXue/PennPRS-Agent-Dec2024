library(tidyverse)
library(readr)

args <- commandArgs(trailingOnly = TRUE)
prs_score_file <- args[1]
trait_file <- args[2]
output_file <- args[3]

cat("Processing PRS: ", prs_score_file, "\n")

trait_df <- read_csv(trait_file)

covars <- c("person_id", "age_2025", "sex_at_birth", paste0("PC", 1:10))
all_trait <- setdiff(colnames(trait_df), covars)

prs_score_df <- read_csv(prs_score_file) %>%
    select(IID, SUM) %>%
    rename(person_id = IID, score = SUM)

# merge trait + covariates + score
df <- trait_df %>%
    inner_join(prs_score_df, by = "person_id")

results <- list()
pc_terms <- paste0("PC", 1:10, collapse = " + ")
covar_rhs <- paste("age_2025 + sex_at_birth +", pc_terms)
score_formula <- as.formula(paste("score ~", covar_rhs))

for (trait in all_trait) {
    cat("  Trait: ", trait)

    tmp <- df %>%
        select(all_of(c(trait, "score", "age_2025", "sex_at_birth", paste0("PC", 1:10)))) %>%
        na.omit()

    # skip if sample size is too small for this trait
    if (nrow(tmp) < 50) next

    # regress trait on covariates, get residuals
    trait_formula <- as.formula(
        paste("`", trait, "` ~", covar_rhs, sep = "")
    )
    resid_trait <- residuals(lm(trait_formula, data = tmp))

    # regress score on covariates, get residuals
    resid_score <- residuals(lm(score_formula, data = tmp))

    # partial correlation = correlation between residuals
    partial_r <- cor(resid_trait, resid_score)

    results[[length(results) + 1]] <- data.frame(
        trait = trait,
        partial_r = partial_r
    )
}

final_df <- bind_rows(results)
write_csv(final_df, output_file)
