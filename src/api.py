# src/api.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(
    title="WorldCup API",
    description="API pour explorer les données de la Coupe du Monde 1930-2022",
    version="1.0"
)

# ===================================================================
# CONFIGURATION CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================================================================
# CONNEXION À LA BASE
# ===================================================================

def get_conn():
    """Retourne une connexion PostgreSQL avec RealDictCursor"""
    return psycopg2.connect(
        dbname="worldcup",
        user="postgres",
        password="5853500",
        host="localhost",
        cursor_factory=RealDictCursor
    )


# ===================================================================
# ENDPOINTS : TOURNOIS
# ===================================================================

@app.get("/tournois", response_model=List[Dict[str, Any]])
def get_tournois():
    """
    Liste de tous les tournois (1930-2022)
    """
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT annee, pays_hote 
        FROM tournois 
        ORDER BY annee
    """)
    
    resultats = cur.fetchall()
    cur.close()
    conn.close()
    
    return resultats


@app.get("/tournois/{annee}")
def get_tournois_detail(annee: int):
    """
    Détail d'un tournoi avec ses matchs
    """
    conn = get_conn()
    cur = conn.cursor()
    
    # Récupérer les infos du tournoi
    cur.execute("""
        SELECT annee, pays_hote 
        FROM tournois 
        WHERE annee = %s
    """, (annee,))
    
    tournoi = cur.fetchone()
    if not tournoi:
        raise HTTPException(status_code=404, detail=f"Tournoi {annee} non trouvé")
    
    # Récupérer les matchs du tournoi
    cur.execute("""
        SELECT 
            m.id,
            m.date_match,
            m.heure,
            m.stade_id,
            s.nom as stade,
            s.ville as stade_ville,
            ed.nom as equipe_dom,
            ee.nom as equipe_ext,
            m.score_dom,
            m.score_ext,
            m.phase,
            m.groupe,
            m.prolongation,
            m.tirs_au_but
        FROM matchs m
        JOIN equipes ed ON m.equipe_dom_id = ed.id
        JOIN equipes ee ON m.equipe_ext_id = ee.id
        LEFT JOIN stades s ON m.stade_id = s.id
        WHERE m.tournoi_id = (SELECT id FROM tournois WHERE annee = %s)
        ORDER BY m.date_match, m.heure
    """, (annee,))
    
    matchs = cur.fetchall()
    cur.close()
    conn.close()
    
    return {
        "annee": tournoi['annee'],
        "pays_hote": tournoi['pays_hote'],
        "nombre_matchs": len(matchs),
        "matchs": matchs
    }


# ===================================================================
# ENDPOINTS : ÉQUIPES
# ===================================================================

@app.get("/equipes", response_model=List[Dict[str, Any]])
def get_equipes():
    """
    Liste de toutes les équipes
    """
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, nom, code_pays 
        FROM equipes 
        ORDER BY nom
    """)
    
    resultats = cur.fetchall()
    cur.close()
    conn.close()
    
    return resultats


@app.get("/equipes/{nom}")
def get_equipe_stats(nom: str):
    """
    Statistiques d'une équipe (matchs joués, buts marqués, etc.)
    """
    conn = get_conn()
    cur = conn.cursor()
    
    # Vérifier que l'équipe existe
    cur.execute("SELECT id, nom, code_pays FROM equipes WHERE nom = %s", (nom,))
    equipe = cur.fetchone()
    
    if not equipe:
        raise HTTPException(status_code=404, detail=f"Équipe '{nom}' non trouvée")
    
    equipe_id = equipe['id']
    
    # Matchs joués
    cur.execute("""
        SELECT 
            COUNT(*) as total_matchs,
            SUM(CASE WHEN m.score_dom > m.score_ext AND m.equipe_dom_id = %s THEN 1 ELSE 0 END) +
            SUM(CASE WHEN m.score_ext > m.score_dom AND m.equipe_ext_id = %s THEN 1 ELSE 0 END) as victoires,
            SUM(CASE WHEN m.score_dom = m.score_ext THEN 1 ELSE 0 END) as nuls,
            SUM(CASE WHEN m.score_dom < m.score_ext AND m.equipe_dom_id = %s THEN 1 ELSE 0 END) +
            SUM(CASE WHEN m.score_ext < m.score_dom AND m.equipe_ext_id = %s THEN 1 ELSE 0 END) as defaites
        FROM matchs m
        WHERE m.equipe_dom_id = %s OR m.equipe_ext_id = %s
    """, (equipe_id, equipe_id, equipe_id, equipe_id, equipe_id, equipe_id))
    
    stats_matchs = cur.fetchone()
    
    # Buts marqués et encaissés
    cur.execute("""
        SELECT 
            COALESCE(SUM(b.minute), 0) as total_buts_marques,
            COALESCE(SUM(CASE WHEN b.equipe_id != %s THEN 1 ELSE 0 END), 0) as total_buts_encaisses
        FROM buts b
        WHERE b.equipe_id = %s
    """, (equipe_id, equipe_id))
    
    stats_buts = cur.fetchone()
    
    # Participations aux tournois
    cur.execute("""
        SELECT DISTINCT t.annee, t.pays_hote
        FROM tournois t
        JOIN matchs m ON m.tournoi_id = t.id
        WHERE m.equipe_dom_id = %s OR m.equipe_ext_id = %s
        ORDER BY t.annee
    """, (equipe_id, equipe_id))
    
    participations = cur.fetchall()
    
    # Meilleurs buteurs
    cur.execute("""
        SELECT 
            j.nom as joueur,
            COUNT(b.id) as buts
        FROM buts b
        JOIN joueurs j ON b.joueur_id = j.id
        WHERE b.equipe_id = %s
        GROUP BY j.id, j.nom
        ORDER BY buts DESC
        LIMIT 10
    """, (equipe_id,))
    
    meilleurs_buteurs = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return {
        "equipe": {
            "id": equipe['id'],
            "nom": equipe['nom'],
            "code_pays": equipe['code_pays']
        },
        "statistiques": {
            "matchs_joues": stats_matchs['total_matchs'],
            "victoires": stats_matchs['victoires'],
            "nuls": stats_matchs['nuls'],
            "defaites": stats_matchs['defaites'],
            "buts_marques": stats_buts['total_buts_marques'],
            "buts_encaisses": stats_buts['total_buts_encaisses']
        },
        "participations": participations,
        "meilleurs_buteurs": meilleurs_buteurs
    }


# ===================================================================
# ENDPOINTS ADDITIONNELS (optionnels)
# ===================================================================

@app.get("/matchs/{match_id}")
def get_match_detail(match_id: int):
    """
    Détail complet d'un match (avec buts, compositions, arbitres)
    """
    conn = get_conn()
    cur = conn.cursor()
    
    # Infos match
    cur.execute("""
        SELECT 
            m.id,
            t.annee,
            m.date_match,
            m.heure,
            s.nom as stade,
            s.ville as stade_ville,
            ed.nom as equipe_dom,
            ee.nom as equipe_ext,
            m.score_dom,
            m.score_ext,
            m.phase,
            m.groupe,
            m.prolongation,
            m.tirs_au_but
        FROM matchs m
        JOIN tournois t ON m.tournoi_id = t.id
        LEFT JOIN stades s ON m.stade_id = s.id
        JOIN equipes ed ON m.equipe_dom_id = ed.id
        JOIN equipes ee ON m.equipe_ext_id = ee.id
        WHERE m.id = %s
    """, (match_id,))
    
    match = cur.fetchone()
    if not match:
        raise HTTPException(status_code=404, detail=f"Match {match_id} non trouvé")
    
    # Buts
    cur.execute("""
        SELECT j.nom as joueur, e.nom as equipe, b.minute, b.type
        FROM buts b
        JOIN joueurs j ON b.joueur_id = j.id
        JOIN equipes e ON b.equipe_id = e.id
        WHERE b.match_id = %s
        ORDER BY b.minute
    """, (match_id,))
    
    buts = cur.fetchall()
    
    # Compositions
    cur.execute("""
        SELECT j.nom as joueur, e.nom as equipe, c.est_capitaine
        FROM compositions c
        JOIN joueurs j ON c.joueur_id = j.id
        JOIN equipes e ON c.equipe_id = e.id
        WHERE c.match_id = %s
        ORDER BY e.nom, c.id
    """, (match_id,))
    
    compositions = cur.fetchall()
    
    # Arbitres
    cur.execute("""
        SELECT a.nom, a.nationalite, ma.role
        FROM matchs_arbitres ma
        JOIN arbitres a ON ma.arbitre_id = a.id
        WHERE ma.match_id = %s
    """, (match_id,))
    
    arbitres = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return {
        "match": match,
        "buts": buts,
        "compositions": compositions,
        "arbitres": arbitres
    }


@app.get("/stats/globales")
def get_stats_globales():
    """
    Statistiques globales de la Coupe du Monde
    """
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as total_matchs FROM matchs")
    total_matchs = cur.fetchone()['total_matchs']
    
    cur.execute("SELECT COUNT(*) as total_buts FROM buts")
    total_buts = cur.fetchone()['total_buts']
    
    cur.execute("SELECT AVG(total) as moyenne_buts_par_match FROM (SELECT COUNT(*) as total FROM buts GROUP BY match_id) sub")
    moyenne_buts = cur.fetchone()['moyenne_buts_par_match']
    
    # Équipe avec le plus de titres
    cur.execute("""
        SELECT e.nom, COUNT(*) as titres
        FROM matchs m
        JOIN equipes e ON m.equipe_dom_id = e.id OR m.equipe_ext_id = e.id
        WHERE m.phase = 'Final'
        GROUP BY e.id, e.nom
        ORDER BY titres DESC
        LIMIT 1
    """)
    plus_titree = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return {
        "total_matchs": total_matchs,
        "total_buts": total_buts,
        "moyenne_buts_par_match": round(moyenne_buts, 2) if moyenne_buts else 0,
        "equipe_plus_titree": plus_titree
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)