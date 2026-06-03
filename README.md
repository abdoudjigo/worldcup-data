# Coupe du Monde — Pipeline de données complet

> De 1930 à 2022, chaque match, chaque but, chaque équipe. Construit de zéro.

---

## À propos

Ce projet couvre l'intégralité de l'histoire de la Coupe du Monde FIFA sur 23 éditions (1930–2022).
L'objectif est de construire une vraie chaîne data professionnelle — du fichier texte brut jusqu'au dashboard interactif en ligne — en passant par une API et une base de données structurée.

Projet personnel réalisé dans le cadre de ma formation **Dev Data** à la **Sonatel Académie / Orange Digital Center**, Dakar.

---

## Ce que le projet couvre

| Étape | Description | Statut |
|-------|-------------|--------|
| 📥 Parsing | Extraction des données brutes depuis les fichiers `.txt` | 🔄 En cours |
| 🧹 Nettoyage | Normalisation des scores, dates, noms d'équipes | ⏳ À venir |
| 🗄️ Base de données | Chargement dans PostgreSQL, schéma relationnel | ⏳ À venir |
| 🔌 API REST | Endpoints par édition, équipe, statistiques | ⏳ À venir |
| 📊 Dashboard | Visualisations interactives avec Chart.js | ⏳ À venir |
| 🚀 Déploiement | Mise en ligne de l'API et du dashboard | ⏳ À venir |

---

## Stack technique

- **Python** — parsing, nettoyage, scripts ETL
- **PostgreSQL** — stockage et requêtes relationnelles
- **FastAPI** — API REST avec documentation automatique
- **HTML / CSS / JS** — interface web
- **Chart.js** — visualisations interactives
- **Git / GitHub** — versioning et déploiement

---

## Source des données

Les données proviennent du repo open source [openfootball/worldcup](https://github.com/openfootball/worldcup).
Format brut : fichiers `.txt` structurés à la main, couvrant 23 éditions de 1930 (Uruguay) à 2022 (Qatar).

Chaque édition contient selon les années :
- Les groupes et compositions
- Les matchs avec scores et mi-temps
- Les stades et villes hôtes
- Les buteurs et passeurs (éditions récentes)

---

## Structure du projet

```
worldcup-data/
│
├── worldcup/          # Données sources — repo openfootball (ne pas modifier)
│
├── src/               # Scripts Python
│   ├── parser.py      # Extraction des données brutes
│   ├── clean.py       # Nettoyage et normalisation
│   └── load.py        # Chargement PostgreSQL
│
├── data/              # Données transformées
│   ├── raw/           # JSON brut issu du parser
│   └── processed/     # JSON nettoyé et normalisé
│
└── README.md
```

---

## Questions auxquelles le projet répond

- Quelle nation a dominé l'histoire de la Coupe du Monde ?
- Y a-t-il un avantage à jouer à domicile ?
- Comment le nombre de buts par match a-t-il évolué depuis 1930 ?
- Quelle est la meilleure génération de chaque équipe ?
- Quelles confédérations produisent le plus de vainqueurs ?

---

## Auteur

**Abdoulaye Djigo**
Étudiant Dev Data — Sonatel Académie / Orange Digital Center, Dakar, Sénégal
[GitHub](https://github.com/abdoudjigo)