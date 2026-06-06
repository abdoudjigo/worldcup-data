# import_data.py
import re
import psycopg2
import json
import os

# ===================================================================
# CONNEXION À LA BASE
# ===================================================================

conn = psycopg2.connect(
    dbname="worldcup",
    user="postgres",
    password="5853500",
    host="localhost"
)
cur = conn.cursor()

# ===================================================================
# FONCTION POUR CHARGER LES ÉQUIPES AVEC LEUR CODE PAYS
# ===================================================================

def charger_equipes_avec_code(cur, matchs):
    """
    Insère les équipes avec leur code pays (FRA pour France, etc.)
    """
    
    # Dictionnaire de correspondance (à enrichir)
    code_pays_map = {
        # Europe
        "France": "FRA",
        "Germany": "GER", "West Germany": "GER",
        "Italy": "ITA",
        "Spain": "ESP",
        "Netherlands": "NED",
        "England": "ENG",
        "Portugal": "POR",
        "Belgium": "BEL",
        "Sweden": "SWE",
        "Denmark": "DEN",
        "Croatia": "CRO",
        "Switzerland": "SUI",
        "Serbia": "SRB", "Yugoslavia": "YUG",
        "Scotland": "SCO",
        "Ireland": "IRL",
        "Norway": "NOR",
        "Romania": "ROU",
        "Greece": "GRE",
        "Czechoslovakia": "TCH", "Czechia": "CZE",
        "Hungary": "HUN",
        "Austria": "AUT",
        "Poland": "POL",
        "Russia": "RUS", "Soviet Union": "URS",
        "Turkey": "TUR",
        
        # Amérique du Sud
        "Argentina": "ARG",
        "Brazil": "BRA",
        "Uruguay": "URU",
        "Chile": "CHI",
        "Colombia": "COL",
        "Peru": "PER",
        "Paraguay": "PAR",
        "Ecuador": "ECU",
        "Bolivia": "BOL",
        
        # Amérique du Nord
        "Mexico": "MEX",
        "USA": "USA",
        "Canada": "CAN",
        "Costa Rica": "CRC",
        "Honduras": "HON",
        "El Salvador": "SLV",
        "Trinidad and Tobago": "TRI",
        "Panama": "PAN",
        "Jamaica": "JAM",
        "Haiti": "HAI",
        "Cuba": "CUB",
        
        # Afrique
        "Morocco": "MAR",
        "Tunisia": "TUN",
        "Senegal": "SEN",
        "Cameroon": "CMR",
        "Nigeria": "NGA",
        "Ghana": "GHA",
        "Côte d'Ivoire": "CIV",
        "Egypt": "EGY",
        "South Africa": "RSA",
        "Algeria": "ALG",
        "Angola": "ANG",
        "Togo": "TOG",
        
        # Asie / Océanie
        "Japan": "JPN",
        "South Korea": "KOR",
        "Australia": "AUS",
        "Saudi Arabia": "KSA",
        "Iran": "IRN",
        "Qatar": "QAT",
        "United Arab Emirates": "UAE",
        "Kuwait": "KUW",
        "Iraq": "IRQ",
        "New Zealand": "NZL",
        "North Korea": "PRK",
        "Dutch East Indies": "IDN", # Ancien nom de l'Indonésie 

        "Zaire": "ZAI",
        "Bulgaria": "BUL",
        "Slovakia": "SVK",
        "Serbia and Montenegro": "SCG",
        "China": "CHN",
        "East Germany": "GDR",
        "Northern Ireland": "NIR",
        "Israel": "ISR",
        "Bosnia-Herzegovina": "BIH",
        "Ukraine": "UKR",
        "Iceland": "ISL",
        "Slovenia": "SVN",
        "Wales": "WAL",
    }
    
    equipes_uniques = set()
    for match in matchs:
        equipes_uniques.add(match['equipe_dom'])
        equipes_uniques.add(match['equipe_ext'])
    
    print(f"📋 {len(equipes_uniques)} équipes uniques trouvées")
    
    for equipe_nom in equipes_uniques:
        code = code_pays_map.get(equipe_nom)
        
        if code:
            cur.execute("""
                INSERT INTO equipes (nom, code_pays) 
                VALUES (%s, %s) 
                ON CONFLICT (nom) DO UPDATE 
                SET code_pays = EXCLUDED.code_pays
            """, (equipe_nom, code))
        else:
            # Équipe sans code pays
            cur.execute("""
                INSERT INTO equipes (nom) 
                VALUES (%s) 
                ON CONFLICT (nom) DO NOTHING
            """, (equipe_nom,))
            print(f"⚠️  Code pays manquant pour : {equipe_nom}")
    
    print(f"✅ Équipes insérées (doublons ignorés)")




# ===================================================================
# FONCTION : CHARGER LES TOURNOIS
# ===================================================================

def charger_tournois(cur, tournois_info: dict):
    """
    Parcourt tous les matchs et insère les tournois (années) uniques dans la table tournois.
    
    Args:
        cur: Curseur PostgreSQL
        tournois_info: Dictionnaire contenant les informations sur les tournois {année: pays_hôte}
    """
    
    for annee, pays_hote in tournois_info.items():
        cur.execute("""
            INSERT INTO tournois (annee, pays_hote) 
            VALUES (%s, %s) 
            ON CONFLICT (annee) DO UPDATE 
            SET pays_hote = EXCLUDED.pays_hote
        """, (annee, pays_hote))
    
    print(f"✅ Tournois insérés (doublons ignorés)")


# ===================================================================
# FONCTION : CHARGER LES STADES
# ===================================================================

def charger_stades(cur, matchs):
    """
    Parcourt tous les matchs et insère les stades uniques dans la table stades.
    
    Args:
        cur: Curseur PostgreSQL
        matchs: Liste de dictionnaires (chaque dict = un match)
    """
    
    # Collecter tous les stades uniques
    stades_uniques = {}
    
    for match in matchs:
        stade = match.get('stade')
        if stade and stade not in stades_uniques:
            # Séparer le nom et la ville (format: "Pocitos, Montevideo")
            if ',' in stade:
                nom, ville = stade.split(',', 1)
                nom = nom.strip()
                ville = ville.strip()
            else:
                nom = stade.strip()
                ville = None
            
            stades_uniques[stade] = {
                'nom': nom,
                'ville': ville,
                'pays': None  # À enrichir plus tard
            }
    
    print(f"📋 {len(stades_uniques)} stades uniques trouvés")
    
    # Insérer chaque stade
    for stade_info in stades_uniques.values():
        cur.execute("""
            INSERT INTO stades (nom, ville, pays) 
            VALUES (%s, %s, %s) 
            ON CONFLICT (nom) DO NOTHING
        """, (stade_info['nom'], stade_info['ville'], stade_info['pays']))
    
    print(f"✅ Stades insérés (doublons ignorés)")


# ===================================================================
# FONCTION POUR RÉCUPÉRER L'ID D'UN STADE
# ===================================================================

def get_stade_id(cur, nom_stade):
    """
    Retourne l'ID d'un stade à partir de son nom complet.
    
    Args:
        cur: Curseur PostgreSQL
        nom_stade: Nom complet du stade (ex: "Pocitos, Montevideo")
    
    Returns:
        int: ID du stade, ou None si non trouvé
    """
    if not nom_stade:
        return None
    
    # Extraire le nom seul (sans la ville)
    if ',' in nom_stade:
        nom_seul = nom_stade.split(',', 1)[0].strip()
    else:
        nom_seul = nom_stade.strip()
    
    cur.execute("SELECT id FROM stades WHERE nom = %s", (nom_seul,))
    resultat = cur.fetchone()
    return resultat[0] if resultat else None


# ===================================================================
# FONCTION POUR RÉCUPÉRER L'ID D'UN TOURNOI
# ===================================================================

def get_tournoi_id(cur, annee):
    """
    Retourne l'ID d'un tournoi à partir de son année.
    
    Args:
        cur: Curseur PostgreSQL
        annee: Année du tournoi (ex: 1930)
    
    Returns:
        int: ID du tournoi, ou None si non trouvé
    """
    cur.execute("SELECT id FROM tournois WHERE annee = %s", (annee,))
    resultat = cur.fetchone()
    return resultat[0] if resultat else None


# ===================================================================
# FONCTION : CHARGER LES MATCHS
# ===================================================================

def charger_matchs(cur, matchs):
    """
    Parcourt tous les matchs et insère chaque match dans la table matchs.
    
    Args:
        cur: Curseur PostgreSQL
        matchs: Liste de dictionnaires (chaque dict = un match)
    """
    
    matchs_inseres = 0
    matchs_ignores = 0
    
    for match in matchs:
        # 1. Récupérer l'ID du tournoi
        cur.execute("SELECT id FROM tournois WHERE annee = %s", (match['annee'],))
        result = cur.fetchone()
        if not result:
            print(f"⚠️  Tournoi non trouvé pour l'année {match['annee']}")
            matchs_ignores += 1
            continue
        tournoi_id = result[0]
        
        # 2. Récupérer l'ID du stade
        stade_id = None
        if match.get('stade'):
            nom_stade = match['stade'].split(',')[0].strip()
            cur.execute("SELECT id FROM stades WHERE nom = %s", (nom_stade,))
            result = cur.fetchone()
            if result:
                stade_id = result[0]
        
        # 3. Récupérer l'ID de l'équipe domicile
        cur.execute("SELECT id FROM equipes WHERE nom = %s", (match['equipe_dom'],))
        result = cur.fetchone()
        if not result:
            print(f"⚠️  Équipe non trouvée: {match['equipe_dom']}")
            matchs_ignores += 1
            continue
        equipe_dom_id = result[0]
        
        # 4. Récupérer l'ID de l'équipe extérieure
        cur.execute("SELECT id FROM equipes WHERE nom = %s", (match['equipe_ext'],))
        result = cur.fetchone()
        if not result:
            print(f"⚠️  Équipe non trouvée: {match['equipe_ext']}")
            matchs_ignores += 1
            continue
        equipe_ext_id = result[0]
        
        # 5. Construire la date
        date_match = None
        if match.get('date') and match['date'].get('jour') and match['date'].get('mois_num'):
            annee = match['annee']
            mois = match['date']['mois_num']
            jour = match['date']['jour']
            date_match = f"{annee}-{mois:02d}-{jour:02d}"
        
        # 6. Déterminer la phase avec la logique améliorée
        groupe_brut = match.get('groupe', '') or ''
        
        if 'Final' in groupe_brut and 'Semi' not in groupe_brut and 'Quarter' not in groupe_brut:
            phase = "Final"
        elif 'Semi' in groupe_brut:
            phase = "Semi-final"
        elif 'Quarter' in groupe_brut:
            phase = "Quarter-final"
        elif 'Third' in groupe_brut:
            phase = "Third place"
        elif 'Round' in groupe_brut:
            phase = "Round of 16"
        elif 'Group' in groupe_brut:
            phase = "Group stage"
        else:
            phase = groupe_brut.strip('▪ ').strip()
        
        # 7. Extraire la lettre du groupe (A, B, C, 1, 2...)
        groupe = None
        if match.get('groupe'):
            import re
            group_match = re.search(r'Group\s+([A-Z0-9]+)', match['groupe'])
            if group_match:
                groupe = group_match.group(1)
        
        # 8. Insérer le match
        cur.execute("""
            INSERT INTO matchs (
                tournoi_id, stade_id, equipe_dom_id, equipe_ext_id,
                score_dom, score_ext, date_match, heure,
                timezone, phase, groupe, prolongation, tirs_au_but
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            tournoi_id,
            stade_id,
            equipe_dom_id,
            equipe_ext_id,
            match['score_dom'],
            match['score_ext'],
            date_match,
            match.get('heure'),
            match.get('timezone'),
            phase,
            groupe,
            match.get('prolongation', False),
            match.get('tirs_au_but', False)
        ))
        
        matchs_inseres += 1
    
    print(f"✅ Matchs insérés : {matchs_inseres}")
    if matchs_ignores > 0:
        print(f"⚠️  Matchs ignorés : {matchs_ignores}")



# ===================================================================
# FONCTIONS UTILITAIRES 
# ===================================================================

def get_tournoi_id(cur, annee):
    """Retourne l'ID du tournoi à partir de l'année"""
    cur.execute("SELECT id FROM tournois WHERE annee = %s", (annee,))
    result = cur.fetchone()
    return result[0] if result else None

def get_stade_id(cur, stade_complet):
    """Retourne l'ID du stade à partir du nom complet"""
    if not stade_complet:
        return None
    nom_stade = stade_complet.split(',')[0].strip()
    cur.execute("SELECT id FROM stades WHERE nom = %s", (nom_stade,))
    result = cur.fetchone()
    return result[0] if result else None

def get_equipe_id(cur, nom_equipe):
    """Retourne l'ID de l'équipe à partir de son nom"""
    cur.execute("SELECT id FROM equipes WHERE nom = %s", (nom_equipe,))
    result = cur.fetchone()
    return result[0] if result else None


# ===================================================================
# FONCTION : CHARGER LES JOUEURS
# ===================================================================

def charger_joueurs(cur, matchs):
    """
    Parcourt tous les matchs et insère les joueurs uniques dans la table joueurs.
    
    """
    
    # Ensemble pour stocker les joueurs uniques (nom, equipe_id)
    joueurs_uniques = set()
    
    for match in matchs:
        # Récupérer l'ID de l'équipe domicile
        cur.execute("SELECT id FROM equipes WHERE nom = %s", (match['equipe_dom'],))
        result = cur.fetchone()
        equipe_dom_id = result[0] if result else None
        
        # Récupérer l'ID de l'équipe extérieure
        cur.execute("SELECT id FROM equipes WHERE nom = %s", (match['equipe_ext'],))
        result = cur.fetchone()
        equipe_ext_id = result[0] if result else None
        
        # Traiter composition domicile
        if match.get('composition_dom') and match['composition_dom'].get('joueurs_bruts'):
            for joueur_brut in match['composition_dom']['joueurs_bruts']:
                # Nettoyer le nom du joueur (enlever [c], [Y], [R], etc.)
                nom_propre = re.sub(r'\s*\[[^\]]+\]\s*', ' ', joueur_brut)
                nom_propre = re.sub(r'\s+', ' ', nom_propre).strip()
                
                if nom_propre and equipe_dom_id:
                    joueurs_uniques.add((nom_propre, equipe_dom_id))
        
        # Traiter composition extérieure
        if match.get('composition_ext') and match['composition_ext'].get('joueurs_bruts'):
            for joueur_brut in match['composition_ext']['joueurs_bruts']:
                # Nettoyer le nom du joueur (enlever [c], [Y], [R], etc.)
                nom_propre = re.sub(r'\s*\[[^\]]+\]\s*', ' ', joueur_brut)
                nom_propre = re.sub(r'\s+', ' ', nom_propre).strip()
                
                if nom_propre and equipe_ext_id:
                    joueurs_uniques.add((nom_propre, equipe_ext_id))
    
    print(f"📋 {len(joueurs_uniques)} joueurs uniques trouvés")
    
    # Insérer chaque joueur
    joueurs_inseres = 0
    for nom, equipe_id in joueurs_uniques:
        cur.execute("""
            INSERT INTO joueurs (nom, equipe_id) 
            VALUES (%s, %s) 
            ON CONFLICT (nom, equipe_id) DO NOTHING
        """, (nom, equipe_id))
        
        if cur.rowcount > 0:
            joueurs_inseres += 1
    
    print(f"✅ Joueurs insérés : {joueurs_inseres}")


# ===================================================================
# FONCTION POUR RÉCUPÉRER L'ID D'UN JOUEUR
# ===================================================================

def get_joueur_id(cur, nom_joueur, equipe_id):
    """
    Retourne l'ID d'un joueur à partir de son nom et de son équipe.
    
    Args:
        cur: Curseur PostgreSQL
        nom_joueur: Nom du joueur
        equipe_id: ID de l'équipe
    
    Returns:
        int: ID du joueur, ou None si non trouvé
    """
    cur.execute("""
        SELECT id FROM joueurs 
        WHERE nom = %s AND equipe_id = %s
    """, (nom_joueur, equipe_id))
    result = cur.fetchone()
    return result[0] if result else None