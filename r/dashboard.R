.libPaths("~/R/library")

cat("🚀 Génération des visualisations WorldCup...\n\n")

source("r/viz_01_buts_edition.R")
source("r/viz_02_buts_equipe.R")
source("r/viz_03_distribution.R")
source("r/viz_04_evolution.R")
source("r/viz_05_confrontations.R")

cat("\n✅ Tous les graphiques sont dans r/output/\n")