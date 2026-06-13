.libPaths("~/R/library")
source("r/connexion.R")
library(ggplot2)
library(hrbrthemes)
library(viridis)

query <- "
  SELECT e.nom, COUNT(b.id) AS total_buts
  FROM equipes e
  JOIN matchs m ON (m.equipe_dom_id = e.id OR m.equipe_ext_id = e.id)
  JOIN buts b ON b.match_id = m.id AND b.equipe_id = e.id
  GROUP BY e.nom
  ORDER BY total_buts DESC
  LIMIT 15
"
df <- dbGetQuery(con, query)
df$total_buts <- as.integer(df$total_buts)
df$nom <- factor(df$nom, levels = rev(df$nom))

ggplot(df, aes(x = nom, y = total_buts, fill = total_buts)) +
  geom_bar(stat = "identity", width = 0.75, color = NA) +
  geom_text(aes(label = total_buts), hjust = -0.3, size = 3.5, fontface = "bold", color = "grey30") +
  scale_fill_viridis(option = "D", direction = -1) +
  coord_flip() +
  labs(
    title    = "Top 15 nations — Buts marqués",
    subtitle = "Toutes éditions confondues (1930–2022)",
    x        = NULL, y = "Nombre de buts",
    caption  = "Source : openfootball/worldcup"
  ) +
  theme_ipsum(base_size = 12) +
  theme(
    plot.title      = element_text(face = "bold", size = 18),
    plot.subtitle   = element_text(size = 12, color = "grey50"),
    legend.position = "none",
    panel.grid.major.y = element_blank()
  )

ggsave("r/output/viz_02_buts_equipe.png", width = 11, height = 8, dpi = 180)
cat("✅ viz_02 sauvegardé\n")