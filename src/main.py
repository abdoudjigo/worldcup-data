import os
import psycopg2
from parser import parser_fichier
from utils import sauvegarder_json
from load import (
    charger_equipes_avec_code,
    charger_tournois,
    charger_stades,
    charger_matchs,
    charger_joueurs,
    charger_buts,
    charger_arbitres,
    charger_compositions,
    get_equipe_id,
    get_tournoi_id,
    get_stade_id,
    get_arbitre_id
)

BASE_MORE = "/home/abdoulaye/Documents/Orange Digital center/projets/worldcup-data/worldcup/more/"
BASE_WORLDCUP = "/home/abdoulaye/Documents/Orange Digital center/projets/worldcup-data/worldcup/"
SORTIE = "/home/abdoulaye/Documents/Orange Digital center/projets/worldcup-data/data/worldcup_raw.json"

# 1. Parser tous les fichiers + extraire pays hôte
tous_les_matchs = []
tournois_info = {}  # {1930: 'Uruguay', 1934: 'Italy', ...}

for fichier in sorted(os.listdir(BASE_MORE)):
    if fichier.endswith('_full.txt'):
        annee = int(fichier.replace('_full.txt', ''))

        # Trouver le dossier correspondant dans worldcup/
        dossiers = [d for d in os.listdir(BASE_WORLDCUP)
                    if d.startswith(str(annee) + '--')]

        if dossiers:
            pays_hote = dossiers[0].split('--')[1].replace('-', ' ').title()
        else:
            pays_hote = None

        tournois_info[annee] = pays_hote

        # Parser les matchs
        matchs = parser_fichier(os.path.join(BASE_MORE, fichier))
        for match in matchs:
            match['annee'] = annee
        tous_les_matchs.extend(matchs)

print(f"✅ {len(tous_les_matchs)} matchs parsés")

# 2. Sauvegarder JSON
sauvegarder_json(tous_les_matchs, SORTIE)

# 3. Charger en base
conn = psycopg2.connect(
    dbname="worldcup",
    user="postgres",
    password="5853500",
    host="localhost"
)
cur = conn.cursor()


# Pour eviter les doublons lors du chargement, on nettoie les tables avant de charger les nouvelles données
print("🧹 Nettoyage de la base...")
cur.execute("TRUNCATE TABLE matchs CASCADE;")
cur.execute("TRUNCATE TABLE joueurs CASCADE;")
cur.execute("TRUNCATE TABLE stades CASCADE;")
cur.execute("TRUNCATE TABLE tournois CASCADE;")
cur.execute("TRUNCATE TABLE equipes CASCADE;")
conn.commit()
print("✅ Base nettoyée")



charger_equipes_avec_code(cur, tous_les_matchs)
charger_tournois(cur, tournois_info)
charger_stades(cur, tous_les_matchs)
match_ids = charger_matchs(cur, tous_les_matchs)
charger_joueurs(cur, tous_les_matchs)
charger_buts(cur, tous_les_matchs, match_ids)
charger_arbitres(cur, tous_les_matchs, match_ids)
charger_compositions(cur, tous_les_matchs, match_ids)
conn.commit()

# 4. Vérifications
cur.execute("SELECT COUNT(*) FROM equipes")
print(f"Equipes: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM tournois")
print(f"Tournois: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM stades")
print(f"Stades: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM matchs")
print(f"Matchs: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM joueurs")
print(f"Joueurs: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM arbitres")
print(f"Arbitres: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM matchs_arbitres")
print(f"Matchs_arbitres: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM buts")
print(f"Buts: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM compositions")
print(f"Compositions: {cur.fetchone()[0]}")

cur.close()
conn.close()