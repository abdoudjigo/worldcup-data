.libPaths("~/R/library")
source("r/connexion.R")
library(ggplot2)
library(hrbrthemes)
library(viridis)

query <- "
  SELECT e.nom,
         SUM(CASE WHEN m.equipe_dom_id = e.id THEN m.score_dom
                  WHEN m.equipe_ext_id = e.id THEN m.score_ext END) AS buts_marques,
         SUM(CASE WHEN m.equipe_dom_id = e.id THEN m.score_ext
                  WHEN m.equipe_ext_id = e.id THEN m.score_dom END) AS buts_encaisses
  FROM equipes e
  JOIN matchs m ON (m.equipe_dom_id = e.id OR m.equipe_ext_id = e.id)
  WHERE m.score_dom IS NOT NULL AND m.score_ext IS NOT NULL
  GROUP BY e.nom
  HAVING COUNT(m.id) >= 10
  ORDER BY buts_marques DESC
  LIMIT 20
"
df <- dbGetQuery(con, query)
df$buts_marques <- as.integer(df$buts_marques)
df$buts_encaisses <- as.integer(df$buts_encaisses)

ggplot(df, aes(x = buts_encaisses, y = buts_marques, color = buts_marques)) +
  geom_abline(slope = 1, intercept = 0, linetype = "dashed", color = "grey60", linewidth = 0.8) +
  geom_point(size = 5, alpha = 0.9) +
  geom_text(aes(label = nom), vjust = -1, size = 3, color = "grey30", fontface = "bold") +
  scale_color_viridis(option = "C", direction = -1) +
  labs(
    title    = "Attaque vs Défense — Top 20 nations",
    subtitle = "Au-dessus de la diagonale = bilan offensif positif",
    x        = "Buts encaissés", y = "Buts marqués",
    caption  = "Source : openfootball/worldcup — min. 10 matchs"
  ) +
  theme_ipsum(base_size = 12) +
  theme(
    plot.title      = element_text(face = "bold", size = 18),
    plot.subtitle   = element_text(size = 12, color = "grey50"),
    legend.position = "none"
  )

ggsave("r/output/viz_05_confrontations.png", width = 12, height = 9, dpi = 180)
cat("✅ viz_05 sauvegardé\n")