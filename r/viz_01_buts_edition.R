.libPaths("~/R/library")
source("r/connexion.R")
library(ggplot2)
library(hrbrthemes)
library(viridis)

query <- "
  SELECT t.annee, COUNT(b.id) AS total_buts
  FROM tournois t
  LEFT JOIN matchs m ON m.tournoi_id = t.id
  LEFT JOIN buts b ON b.match_id = m.id
  GROUP BY t.annee
  ORDER BY t.annee
"
df <- dbGetQuery(con, query)
df$annee <- as.integer(df$annee)
df$total_buts <- as.integer(df$total_buts)

ggplot(df, aes(x = factor(annee), y = total_buts, fill = total_buts)) +
  geom_bar(stat = "identity", width = 0.75, color = NA) +
  geom_text(aes(label = total_buts), vjust = -0.5, size = 3.2, color = "grey30", fontface = "bold") +
  scale_fill_viridis(option = "C", direction = -1) +
  labs(
    title    = "Buts par édition de la Coupe du Monde",
    subtitle = "1930 → 2022 — 22 éditions FIFA",
    x        = NULL, y = "Nombre de buts",
    caption  = "Source : openfootball/worldcup"
  ) +
  theme_ipsum(base_size = 12) +
  theme(
    plot.title       = element_text(face = "bold", size = 18),
    plot.subtitle    = element_text(size = 12, color = "grey50"),
    axis.text.x      = element_text(angle = 45, hjust = 1),
    legend.position  = "none",
    panel.grid.major.x = element_blank()
  )

ggsave("r/output/viz_01_buts_edition.png", width = 13, height = 7, dpi = 180)
cat("✅ viz_01 sauvegardé\n")