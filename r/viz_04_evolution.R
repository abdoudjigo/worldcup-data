.libPaths("~/R/library")
source("r/connexion.R")
library(ggplot2)
library(hrbrthemes)

query <- "
  SELECT t.annee,
         ROUND(AVG(m.score_dom + m.score_ext), 2) AS moyenne_buts
  FROM matchs m
  JOIN tournois t ON t.id = m.tournoi_id
  WHERE m.score_dom IS NOT NULL AND m.score_ext IS NOT NULL
  GROUP BY t.annee
  ORDER BY t.annee
"
df <- dbGetQuery(con, query)
df$annee <- as.integer(df$annee)
df$moyenne_buts <- as.numeric(df$moyenne_buts)

ggplot(df, aes(x = annee, y = moyenne_buts)) +
  geom_area(fill = "#3498DB", alpha = 0.15) +
  geom_line(color = "#2980B9", linewidth = 1.4) +
  geom_point(color = "#E74C3C", size = 3.5) +
  geom_text(aes(label = moyenne_buts), vjust = -1, size = 3, color = "grey40") +
  scale_x_continuous(breaks = df$annee) +
  labs(
    title    = "Évolution de la moyenne de buts par match",
    subtitle = "1930 → 2022 — tendance sur 92 ans",
    x        = NULL, y = "Moyenne buts / match",
    caption  = "Source : openfootball/worldcup"
  ) +
  theme_ipsum(base_size = 12) +
  theme(
    plot.title    = element_text(face = "bold", size = 18),
    plot.subtitle = element_text(size = 12, color = "grey50"),
    axis.text.x   = element_text(angle = 45, hjust = 1)
  )

ggsave("r/output/viz_04_evolution.png", width = 13, height = 7, dpi = 180)
cat("✅ viz_04 sauvegardé\n")