source("r/connexion.R")
library(ggplot2)

# Récupérer les données
query <- "
  SELECT t.annee, COUNT(b.id) AS total_buts
  FROM tournois t
  LEFT JOIN matchs m ON m.tournoi_id = t.id
  LEFT JOIN buts b ON b.match_id = m.id
  GROUP BY t.annee
  ORDER BY t.annee
"
df <- dbGetQuery(con, query)

# Graphique
ggplot(df, aes(x = factor(annee), y = total_buts)) +
  geom_bar(stat = "identity", fill = "#E8B84B", color = "white", width = 0.7) +
  geom_text(aes(label = total_buts), vjust = -0.5, size = 3, color = "white") +
  labs(
    title    = "⚽ Buts par édition de la Coupe du Monde",
    subtitle = "1930 → 2022 — 22 éditions",
    x        = "Année",
    y        = "Nombre de buts",
    caption  = "Source : openfootball/worldcup"
  ) +
  theme_dark() +
  theme(
    plot.title    = element_text(face = "bold", size = 16, color = "white"),
    plot.subtitle = element_text(size = 11, color = "#aaaaaa"),
    axis.text.x   = element_text(angle = 45, hjust = 1, color = "white"),
    axis.text.y   = element_text(color = "white"),
    axis.title    = element_text(color = "white"),
    plot.caption  = element_text(color = "#888888"),
    panel.grid.major.x = element_blank()
  )

ggsave("r/output/viz_01_buts_edition.png", width = 12, height = 6, dpi = 150)
cat("✅ viz_01 sauvegardé\n")