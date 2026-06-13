source("r/connexion.R")
library(ggplot2)

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

ggplot(df, aes(x = annee, y = moyenne_buts)) +
  geom_line(color = "#E8B84B", linewidth = 1.2) +
  geom_point(color = "white", size = 3) +
  geom_text(aes(label = moyenne_buts), vjust = -1, color = "#aaaaaa", size = 3) +
  labs(
    title    = "📈 Évolution de la moyenne de buts par match",
    subtitle = "1930 → 2022",
    x        = "Année", y = "Moyenne buts/match",
    caption  = "Source : openfootball/worldcup"
  ) +
  scale_x_continuous(breaks = df$annee) +
  theme_dark() +
  theme(
    plot.title    = element_text(face = "bold", size = 16, color = "white"),
    plot.subtitle = element_text(size = 11, color = "#aaaaaa"),
    axis.text.x   = element_text(angle = 45, hjust = 1, color = "white"),
    axis.text.y   = element_text(color = "white"),
    axis.title    = element_text(color = "white"),
    plot.caption  = element_text(color = "#888888")
  )

ggsave("r/output/viz_04_evolution.png", width = 12, height = 6, dpi = 150)
cat("✅ viz_04 sauvegardé\n")