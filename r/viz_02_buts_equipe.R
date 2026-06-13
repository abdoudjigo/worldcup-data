source("r/connexion.R")
library(ggplot2)
library(dplyr)

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
df$nom <- factor(df$nom, levels = rev(df$nom))

ggplot(df, aes(x = nom, y = total_buts)) +
  geom_bar(stat = "identity", fill = "#1a9e5c", color = "white") +
  geom_text(aes(label = total_buts), hjust = -0.2, color = "white", size = 3.5) +
  coord_flip() +
  labs(
    title    = "🏆 Top 15 nations — Buts marqués",
    subtitle = "Toutes éditions confondues (1930–2022)",
    x        = NULL, y = "Nombre de buts",
    caption  = "Source : openfootball/worldcup"
  ) +
  theme_dark() +
  theme(
    plot.title    = element_text(face = "bold", size = 16, color = "white"),
    plot.subtitle = element_text(size = 11, color = "#aaaaaa"),
    axis.text     = element_text(color = "white"),
    axis.title    = element_text(color = "white"),
    plot.caption  = element_text(color = "#888888"),
    panel.grid.major.y = element_blank()
  )

ggsave("r/output/viz_02_buts_equipe.png", width = 10, height = 7, dpi = 150)
cat("✅ viz_02 sauvegardé\n")