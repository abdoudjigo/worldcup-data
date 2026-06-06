# import_data.py
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