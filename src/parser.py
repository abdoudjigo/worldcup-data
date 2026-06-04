import re

def parser_ligne_match(ligne: str) -> dict:
    """
    Parse une ligne de match
    """
    #on enleve les espace  debut et fin
    ligne = ligne.strip() 
    
    # Séparer la partie match du stade avec ' @ '
    if '@' not in ligne :
        raise ValueError(f"Separateur non trouve: {ligne}")
    
    #decoupe ligne en 2 partie avec affectation 2 variables
    infos_match, stade = ligne.split('@', 1)
    stade = stade.strip()


    #on extrait le score a travers infosmatch
    score_match = re.search(r'(\d+)-(\d+)', infos_match)
    if not score_match:
        raise ValueError(f"Score Invalide: {infos_match}")
    
    #on prends la valeur de chak score
    score_dom = int(score_match.group(1)) #group c le nom de la fonction permettant 
    score_ext = int(score_match.group(2)) # d'acceder au partie capturer par le regex
    score_texe = score_match.group(0)
    
    #trouver la position du score
    pos_score = infos_match.find(score_texe) #index d'une sous chaine dans une chaine

    # Partie avant le score (contient heure, timezone, equipe_dom)
    avant_score = infos_match[:pos_score].strip()

    # Partie après le score (contient equipe_ext)
    apres_score = infos_match[pos_score + len(score_texe):].strip()

    # Supprimer tout ce qui est entre parenthèses
    apres_score = re.sub(r'\(.*?\)', '', apres_score).strip()
     
    # Extraire heure et timezone de la partie avantscore
    partie_avant = avant_score.split()

    heure = partie_avant[0]
    timezone = partie_avant[1]

    # Le reste de la partie avant est equipe_dom
    equipe_dom = ' '.join(partie_avant[2:])
    # equipe_ext est directement la partie après
    equipe_ext = apres_score

    return{
        'heure': heure,
        'timezone' : timezone,
        'equipe_dom' : equipe_dom,
        'equipe_ext': equipe_ext,
        'score_dom' : score_dom,
        'score_ext' : score_ext,
        'stade' : stade
    }

ligne = "15:00 UTC-3   Chile  1-0  France   @ Estadio Centenario, Montevideo"
# Cas 1 - équipe avec deux mots
ligne1 = "  15:00 UTC-3   South Africa  1-0  France   @ Stade, Ville"

# Cas 2 - score avec prolongation
ligne2 = "  20:00 UTC+1   Argentina  3-3  France   @ Lusail Stadium, Qatar"

# Cas 3 - équipe ext avec deux mots
ligne3 = "  15:00 UTC-3   Chile  3-0  West Germany   @ Stade, Ville"
# Cas 4 - prolongation
ligne4 = "  20:00 UTC+3   Argentina  3-3 (a.e.t.)  France   @ Lusail Stadium, Qatar"
print(parser_ligne_match(ligne4))
print(parser_ligne_match(ligne))
print(parser_ligne_match(ligne1))
print(parser_ligne_match(ligne2))
print(parser_ligne_match(ligne3))






