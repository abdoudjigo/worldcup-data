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


def charger_equipes_avec_code(cur, matchs):
    """
    Insère les équipes avec leur code pays (FRA pour France, etc.)
    """
    
    # =================================================================
    # Dictionnaire de correspondance (à enrichir)
    # =================================================================
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