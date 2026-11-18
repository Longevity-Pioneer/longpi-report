# Reference run of MiMIR 1.5 (GPL-3; CRAN archive) MetaboHealth (comp.mort_score) on its own synthetic
# Nightingale dataset. Only the two base-R functions are evaluated; nothing from MiMIR is redistributed.
# usage: Rscript mimir_reference.R <MiMIR source dir> <out dir>
args <- commandArgs(trailingOnly = TRUE)
mdir <- args[1]; odir <- args[2]
src <- readLines(file.path(mdir, "R", "predictors_functions.R"))
endf <- function(st) {
  depth <- 0
  for (i in st:length(src)) {
    depth <- depth + nchar(gsub("[^{]", "", src[i])) - nchar(gsub("[^}]", "", src[i]))
    if (depth == 0 && i > st) return(i)
  }
}
s1 <- grep("^prep_met_for_scores <- function", src)
s2 <- grep("^comp.mort_score <- function", src)
load(file.path(mdir, "data", "mort_betas.rda"))
eval(parse(text = src[s1:endf(s1)]))
eval(parse(text = src[s2:endf(s2)]))
load(file.path(mdir, "data", "synthetic_metabolic_dataset.rda"))
load(file.path(mdir, "data", "PARAM_metaboAge.rda"))
d <- synthetic_metabolic_dataset
ms <- comp.mort_score(d, quiet = TRUE)
out <- data.frame(row = seq_len(nrow(d)), d[, mort_betas$Abbreviation], mortScore = ms$mortScore)
write.csv(out, file.path(odir, "mimir_synthetic_mortscore.csv"), row.names = FALSE)
b <- mort_betas
b$logMEAN <- PARAM_metaboAge$logMEAN[b$Abbreviation]
b$logSD <- PARAM_metaboAge$logSD[b$Abbreviation]
b$MEAN <- PARAM_metaboAge$MEAN[b$Abbreviation]
b$SD <- PARAM_metaboAge$SD[b$Abbreviation]
write.csv(b, file.path(odir, "metabohealth_betas_bbmri_ref.csv"), row.names = FALSE)
print(b, digits = 10)
cat(sum(d[, mort_betas$Abbreviation] == 0, na.rm = TRUE), "zeros; NA:", sum(is.na(d[, mort_betas$Abbreviation])), "\n")
