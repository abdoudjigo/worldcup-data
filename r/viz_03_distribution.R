.libPaths("~/R/library")
source("r/connexion.R")
library(ggplot2)
library(hrbrthemes)
library(viridis)

query <- "
  SELECT t.annee,
         (m.score_dom + m.score_ext) AS buts_match
  FROM matchs m
  JOIN tournois t ON t.id = m.tournoi_id
  WHERE m.score_dom IS NOT NULL AND m.score_ext IS NOT NULL
"
df <- dbGetQuery(con, query)
df$annee <- as.integer(df$annee)
df$buts_match <- as.integer(df$buts_match)
df$decennie <- paste0(floor(df$annee / 10) * 10, "s")

ggplot(df, aes(x = decennie, y = buts_match, fill = decennie)) +
  geom_boxplot(color = "grey30", outlier.color = "#E74C3C", outlier.size = 2.5, alpha = 0.85) +
  scale_fill_viridis(discrete = TRUE, option = "C", alpha = 0.9) +
  labs(
    title    = "Distribution des buts par match",
    subtitle = "Par décennie — 1930 → 2020s",
    x        = "Décennie", y = "Buts par match",
    caption  = "Source : openfootball/worldcup"
  ) +
  theme_ipsum(base_size = 12) +
  theme(
    plot.title      = element_text(face = "bold", size = 18),
    plot.subtitle   = element_text(size = 12, color = "grey50"),
    legend.position = "none"
  )

ggsave("r/output/viz_03_distribution.png", width = 12, height = 7, dpi = 180)
cat("✅ viz_03 sauvegardé\n")