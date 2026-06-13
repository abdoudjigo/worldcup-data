source("r/connexion.R")
library(ggplot2)

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

ggplot(df, aes(x = buts_encaisses, y = buts_marques, label = nom)) +
  geom_point(color = "#E8B84B", size = 4, alpha = 0.8) +
  geom_text(vjust = -0.8, size = 3, color = "white") +
  geom_abline(slope = 1, intercept = 0, linetype = "dashed", color = "#888888") +
  labs(
    title    = "🎯 Attaque vs Défense — Top 20 nations",
    subtitle = "Au-dessus de la diagonale = plus de buts marqués qu'encaissés",
    x        = "Buts encaissés", y = "Buts marqués",
    caption  = "Source : openfootball/worldcup — min. 10 matchs"
  ) +
  theme_dark() +
  theme(
    plot.title    = element_text(face = "bold", size = 16, color = "white"),
    plot.subtitle = element_text(size = 11, color = "#aaaaaa"),
    axis.text     = element_text(color = "white"),
    axis.title    = element_text(color = "white"),
    plot.caption  = element_text(color = "#888888")
  )

ggsave("r/output/viz_05_confrontations.png", width = 11, height = 8, dpi = 150)
cat("✅ viz_05 sauvegardé\n")