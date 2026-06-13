source("r/connexion.R")
library(ggplot2)

query <- "
  SELECT t.annee,
         (m.score_dom + m.score_ext) AS buts_match
  FROM matchs m
  JOIN tournois t ON t.id = m.tournoi_id
  WHERE m.score_dom IS NOT NULL AND m.score_ext IS NOT NULL
"
df <- dbGetQuery(con, query)
df$decennie <- paste0(floor(df$annee / 10) * 10, "s")

ggplot(df, aes(x = decennie, y = buts_match, fill = decennie)) +
  geom_boxplot(color = "white", outlier.color = "#E8B84B", outlier.size = 2) +
  labs(
    title    = "📦 Distribution des buts par match",
    subtitle = "Par décennie — 1930 → 2022",
    x        = "Décennie", y = "Buts par match",
    caption  = "Source : openfootball/worldcup"
  ) +
  theme_dark() +
  theme(
    plot.title    = element_text(face = "bold", size = 16, color = "white"),
    plot.subtitle = element_text(size = 11, color = "#aaaaaa"),
    axis.text     = element_text(color = "white"),
    axis.title    = element_text(color = "white"),
    plot.caption  = element_text(color = "#888888"),
    legend.position = "none"
  )

ggsave("r/output/viz_03_distribution.png", width = 11, height = 6, dpi = 150)
cat("✅ viz_03 sauvegardé\n")