library(readr)
library(dplyr)
library(tidyr)

auc_manual <- function(x, y){
  # x = sensitivity
  # y = 1 - specificity  (FPR)
  
  ord <- order(y)
  x <- x[ord]
  y <- y[ord]
  
  # trapezoidal rule
  sum(diff(y) * (head(x, -1) + tail(x, -1)) / 2)
}

roc.binary <- function(status, variable, confounders, data, precision=seq(0.05, 0.95, by=0.025))
{
cut.off <- quantile(data[,variable], probs=precision, na.rm=TRUE)

if((max(precision)==1) | (min(precision)==0)){stop("The cut-off values have to be different from the minimum or the maximum of the variable") }

if(any(is.na(data[, c(status, all.vars(confounders))]))){stop("Error: missing values are not allowed")}

data$YyY54 <- data[, status]
data$YyY54 <- data[[status]]
form <- update.formula(confounders, YyY54 ~ .)
W <- glm(form, family = binomial(link = logit), data = data)$fitted.values

se <- function(x) {
	sum(1 * (data[, variable] > cut.off[x]) * data[, 
		status] * pmin(1/(W),1/(mean(W)^2*0.1)))/sum(data[, status] * 
		pmin(1/(W),1/(mean(W)^2*0.1)))
}
sp <- function(x) {
	sum(1 * (data[, variable] <= cut.off[x]) * (data[, 
		status] - 1) * pmin(1/(1-W),1/(mean(1-W)^2*0.1)))/sum((data[, status] - 
		1) * pmin(1/(1-W),1/(mean(1-W)^2*0.1)))
}

temp.se <- sapply(1:length(cut.off), FUN = "se")
temp.sp <- sapply(1:length(cut.off), FUN = "sp")

.tab <- data.frame( cut.off = cut.off, se = temp.se, sp1 = 1-temp.sp)

.tab$se[.tab$se > 1] <- NA
.tab$sp1[.tab$sp1 > 1] <- NA

.tab.res.temp <- .tab[!is.na(.tab$sp1 + .tab$se), ]
.tab.res.temp <- .tab.res.temp[order(.tab.res.temp$sp1, .tab.res.temp$se), ]
.tab.res.temp <- rbind(c(NA, 0, 0), .tab.res.temp, c(NA, 1, 1)) 
colnames(.tab.res.temp) <- colnames(.tab)

.tab$sp <- 1 - .tab$sp1
.tab <- rbind(c(min(data[,variable]),1,1,0) ,.tab, c(max(data[,variable]),0,0,1))

if(dim(.tab.res.temp)[1]>2){
.auc <- auc_manual(.tab.res.temp$se, 1-.tab.res.temp$sp1)
}else{.auc<-NA}

.obj <- list(table=.tab[,c("cut.off", "se", "sp")], auc = .auc)

class(.obj) <- "rocrisca"

return(.obj)

}

args <- commandArgs(trailingOnly = TRUE)
prs_score_file <- args[1]
trait_file <- args[2]
output_file <- args[3]

cat("Processing PRS: ", prs_score_file, "\n")

# trait information
trait_df <- read_csv(trait_file)

covars <- c("person_id", "age_2025", "sex_at_birth", paste0("PC", 1:10))
all_trait <- setdiff(colnames(trait_df), covars)

# score information
prs_score_df <- read_csv(prs_score_file)

prs_score_df <- prs_score_df %>%
  select(IID, SUM) %>%
  rename(person_id = IID, score = SUM)

results <- list()
pc_terms <- paste0("PC", 1:10, collapse = " + ")
conf_formula <- as.formula(paste("~ age_2025 + sex_at_birth +", pc_terms))

# merge trait + covariates + score
df <- trait_df %>%
  inner_join(prs_score_df, by = "person_id")

for (trait in all_trait) {

  cat("  Trait: ", trait)

  roc_obj <- roc.binary(
    status = trait,
    variable = "score",
    confounders = conf_formula,
    data = df,
    precision = seq(0.05, 0.95, by = 0.05)
  )

  results[[length(results) + 1]] <- data.frame(
    trait = trait,
    adjauc = as.numeric(roc_obj$auc)
  )
}

final_df <- bind_rows(results)
write_csv(final_df, output_file)

