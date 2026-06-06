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
        "Dutch East Indies": "IDN",
        
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
    Insère les tournois (années) uniques dans la table tournois.
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
    """
    stades_uniques = {}
    
    for match in matchs:
        stade = match.get('stade')
        if stade and stade not in stades_uniques:
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
                'pays': None
            }
    
    print(f"📋 {len(stades_uniques)} stades uniques trouvés")
    
    for stade_info in stades_uniques.values():
        cur.execute("""
            INSERT INTO stades (nom, ville, pays) 
            VALUES (%s, %s, %s) 
            ON CONFLICT (nom) DO NOTHING
        """, (stade_info['nom'], stade_info['ville'], stade_info['pays']))
    
    print(f"✅ Stades insérés (doublons ignorés)")


# ===================================================================
# FONCTION : CHARGER LES MATCHS (avec retour des IDs)
# ===================================================================

def charger_matchs(cur, matchs):
    """
    Parcourt tous les matchs et insère chaque match dans la table matchs.
    
    Returns:
        dict: Dictionnaire {index: match_id}
    """
    
    match_ids = {}
    matchs_inseres = 0
    matchs_ignores = 0
    
    for index, match in enumerate(matchs):
        # Récupérer l'ID du tournoi
        cur.execute("SELECT id FROM tournois WHERE annee = %s", (match['annee'],))
        result = cur.fetchone()
        if not result:
            print(f"⚠️  Tournoi non trouvé pour l'année {match['annee']}")
            matchs_ignores += 1
            continue
        tournoi_id = result[0]
        
        # Récupérer l'ID du stade
        stade_id = None
        if match.get('stade'):
            nom_stade = match['stade'].split(',')[0].strip()
            cur.execute("SELECT id FROM stades WHERE nom = %s", (nom_stade,))
            result = cur.fetchone()
            if result:
                stade_id = result[0]
        
        # Récupérer l'ID de l'équipe domicile
        cur.execute("SELECT id FROM equipes WHERE nom = %s", (match['equipe_dom'],))
        result = cur.fetchone()
        if not result:
            print(f"⚠️  Équipe non trouvée: {match['equipe_dom']}")
            matchs_ignores += 1
            continue
        equipe_dom_id = result[0]
        
        # Récupérer l'ID de l'équipe extérieure
        cur.execute("SELECT id FROM equipes WHERE nom = %s", (match['equipe_ext'],))
        result = cur.fetchone()
        if not result:
            print(f"⚠️  Équipe non trouvée: {match['equipe_ext']}")
            matchs_ignores += 1
            continue
        equipe_ext_id = result[0]
        
        # Construire la date
        date_match = None
        if match.get('date') and match['date'].get('jour') and match['date'].get('mois_num'):
            annee = match['annee']
            mois = match['date']['mois_num']
            jour = match['date']['jour']
            date_match = f"{annee}-{mois:02d}-{jour:02d}"
        
        # Déterminer la phase
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
        
        # Extraire la lettre du groupe
        groupe = None
        if match.get('groupe'):
            group_match = re.search(r'Group\s+([A-Z0-9]+)', match['groupe'])
            if group_match:
                groupe = group_match.group(1)
        
        # Insérer le match
        cur.execute("""
            INSERT INTO matchs (
                tournoi_id, stade_id, equipe_dom_id, equipe_ext_id,
                score_dom, score_ext, date_match, heure,
                timezone, phase, groupe, prolongation, tirs_au_but
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            tournoi_id, stade_id, equipe_dom_id, equipe_ext_id,
            match['score_dom'], match['score_ext'], date_match, match.get('heure'),
            match.get('timezone'), phase, groupe,
            match.get('prolongation', False), match.get('tirs_au_but', False)
        ))
        
        match_id = cur.fetchone()[0]
        match_ids[index] = match_id
        matchs_inseres += 1
    
    print(f"✅ Matchs insérés : {matchs_inseres}")
    if matchs_ignores > 0:
        print(f"⚠️  Matchs ignorés : {matchs_ignores}")
    
    return match_ids


# ===================================================================
# FONCTIONS UTILITAIRES
# ===================================================================

def get_tournoi_id(cur, annee):
    cur.execute("SELECT id FROM tournois WHERE annee = %s", (annee,))
    result = cur.fetchone()
    return result[0] if result else None


def get_stade_id(cur, stade_complet):
    if not stade_complet:
        return None
    nom_stade = stade_complet.split(',')[0].strip()
    cur.execute("SELECT id FROM stades WHERE nom = %s", (nom_stade,))
    result = cur.fetchone()
    return result[0] if result else None


def get_equipe_id(cur, nom_equipe):
    cur.execute("SELECT id FROM equipes WHERE nom = %s", (nom_equipe,))
    result = cur.fetchone()
    return result[0] if result else None


# ===================================================================
# FONCTION : NETTOYER UN NOM DE JOUEUR
# ===================================================================

def nettoyer_nom_joueur(joueur_brut: str) -> list:
    """
    Prend une chaîne brute et retourne une liste de noms propres.
    Gère : séparateurs " - ", remplacements, cartons, parenthèses.
    """
    joueur_brut = joueur_brut.strip().lstrip('(')
    joueur_brut = re.sub(r'\s*\[[^\]]*\]\s*', ' ', joueur_brut)
    joueur_brut = re.sub(r'\(?\d+\+?\d*\'[^)]*\)?', '', joueur_brut)
    joueur_brut = re.sub(r'[()]', '', joueur_brut)
    noms = joueur_brut.split(' - ')
    
    resultats = []
    for nom in noms:
        nom = re.sub(r'\s+', ' ', nom).strip()
        if len(nom) >= 2 and any(c.isalpha() for c in nom):
            resultats.append(nom)
    
    return resultats


# ===================================================================
# FONCTION : CHARGER LES JOUEURS
# ===================================================================

def charger_joueurs(cur, matchs):
    """
    Parcourt tous les matchs et insère les joueurs uniques dans la table joueurs.
    """
    joueurs_uniques = set()
    
    for match in matchs:
        cur.execute("SELECT id FROM equipes WHERE nom = %s", (match['equipe_dom'],))
        result = cur.fetchone()
        equipe_dom_id = result[0] if result else None
        
        cur.execute("SELECT id FROM equipes WHERE nom = %s", (match['equipe_ext'],))
        result = cur.fetchone()
        equipe_ext_id = result[0] if result else None
        
        if match.get('composition_dom') and match['composition_dom'].get('joueurs_bruts'):
            for joueur_brut in match['composition_dom']['joueurs_bruts']:
                for nom_propre in nettoyer_nom_joueur(joueur_brut):
                    if nom_propre and equipe_dom_id:
                        joueurs_uniques.add((nom_propre, equipe_dom_id))
        
        if match.get('composition_ext') and match['composition_ext'].get('joueurs_bruts'):
            for joueur_brut in match['composition_ext']['joueurs_bruts']:
                for nom_propre in nettoyer_nom_joueur(joueur_brut):
                    if nom_propre and equipe_ext_id:
                        joueurs_uniques.add((nom_propre, equipe_ext_id))
    
    print(f"📋 {len(joueurs_uniques)} joueurs uniques trouvés")
    
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
# FONCTIONS POUR LES BUTS
# ===================================================================

def get_joueur_id_par_equipe(cur, nom_joueur, nom_equipe):
    """Retourne l'ID d'un joueur à partir de son nom et du nom de son équipe"""
    cur.execute("""
        SELECT j.id FROM joueurs j
        JOIN equipes e ON j.equipe_id = e.id
        WHERE j.nom = %s AND e.nom = %s
    """, (nom_joueur, nom_equipe))
    result = cur.fetchone()
    return result[0] if result else None


def nettoyer_nom_buteur(nom: str) -> str:
    """Nettoie le nom d'un buteur"""
    nom = nom.lstrip('(').strip()
    nom = re.sub(r'\s*\[[^\]]*\].*', '', nom).strip()
    if ' - ' in nom:
        nom = nom.split(' - ')[0].strip()
    return nom


def charger_buts(cur, matchs, match_ids):
    """Version finale - cherche le joueur dans les deux équipes si nécessaire"""
    buts_inseres = 0
    buts_ignores = 0

    for index, match in enumerate(matchs):
        match_id = match_ids.get(index)
        if not match_id:
            buts_ignores += 1
            continue

        # Traiter les buteurs domicile
        for buteur in match.get('buteurs_dom', []):
            nom = nettoyer_nom_buteur(buteur['nom'])
            if not nom:
                buts_ignores += 1
                continue
            
            # 1. Chercher dans equipe_dom d'abord
            joueur_id = get_joueur_id_par_equipe(cur, nom, match['equipe_dom'])
            
            # 2. Si pas trouvé, chercher dans equipe_ext (cas: Brazil v France 0-3)
            if not joueur_id:
                joueur_id = get_joueur_id_par_equipe(cur, nom, match['equipe_ext'])
            
            if not joueur_id:
                print(f"⚠️  Joueur non trouvé: {nom}")
                buts_ignores += 1
                continue
            
            cur.execute("SELECT equipe_id FROM joueurs WHERE id = %s", (joueur_id,))
            equipe_id = cur.fetchone()[0]
            
            cur.execute("""
                INSERT INTO buts (match_id, joueur_id, equipe_id, minute, type)
                VALUES (%s, %s, %s, %s, %s)
            """, (match_id, joueur_id, equipe_id, buteur['minute'], buteur['type']))
            buts_inseres += 1

        # Traiter les buteurs extérieur
        for buteur in match.get('buteurs_ext', []):
            nom = nettoyer_nom_buteur(buteur['nom'])
            if not nom:
                buts_ignores += 1
                continue
            
            # 1. Chercher dans equipe_ext d'abord
            joueur_id = get_joueur_id_par_equipe(cur, nom, match['equipe_ext'])
            
            # 2. Si pas trouvé, chercher dans equipe_dom
            if not joueur_id:
                joueur_id = get_joueur_id_par_equipe(cur, nom, match['equipe_dom'])
            
            if not joueur_id:
                print(f"⚠️  Joueur non trouvé: {nom}")
                buts_ignores += 1
                continue
            
            cur.execute("SELECT equipe_id FROM joueurs WHERE id = %s", (joueur_id,))
            equipe_id = cur.fetchone()[0]
            
            cur.execute("""
                INSERT INTO buts (match_id, joueur_id, equipe_id, minute, type)
                VALUES (%s, %s, %s, %s, %s)
            """, (match_id, joueur_id, equipe_id, buteur['minute'], buteur['type']))
            buts_inseres += 1

    print(f"✅ Buts insérés : {buts_inseres}")
    if buts_ignores > 0:
        print(f"⚠️  Buts ignorés : {buts_ignores}")