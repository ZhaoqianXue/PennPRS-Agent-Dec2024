library(tidyverse)
library(readr)

or_multivariable <- function(status, variable, confounders, data) {
    # formulation
    form <- as.formula(
        paste(
            status, "~", variable, "+",
            paste(all.vars(confounders), collapse = " + ")
        )
    )

    model <- glm(
        form,
        family = binomial(link = "logit"),
        data = data
    )

    beta <- coef(model)[[variable]]
    OR <- exp(beta)

    return(OR)
}

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
conf_formula <- as.formula(paste("~ age_2025 + sex_at_birth +", pc_terms))
for (trait in all_trait) {
    cat("  Trait: ", trait)

    res <- or_multivariable(
        status = trait,
        variable = "score",
        confounders = conf_formula,
        data = df
    )

    results[[length(results) + 1]] <- data.frame(
        trait = trait,
        OR = res
    )
}

final_df <- bind_rows(results)
write_csv(final_df, output_file)
