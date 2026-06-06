import re

#=========================================================================
#=============== FONCTION PARSER LIGNE MATCH =============================
#=========================================================================

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



#=========================================================================
#=============== FONCTION PARSER BUTEURS =================================
#=========================================================================

def parser_ligne_buteur(ligne_buteurs: str) -> dict:
    """
    Parse une ligne de buteurs comme:
    (Lucien LAURENT 19', Marcel LANGILLER 40';
    Juan CARRENO 70')
    """

    # on enlève les parenthèses extérieures
    ligne_buteurs = ligne_buteurs.strip()
    if ligne_buteurs.startswith('(') and ligne_buteurs.endswith(')'):
        ligne_buteurs = ligne_buteurs[1:-1] 

    # on sépare les buteurs dom et ext avec le point virgule
    parties = ligne_buteurs.split(';')

    buteurs_dom = []
    buteurs_ext = []

    # FONCTION INTERNE pour parser une liste de buteurs
    def parser_liste_buteurs(texte_buteurs: str) -> list:
        """
        Parse "Lucien LAURENT 19', Marcel LANGILLER 40', Andre MASCHINOT 43', 87'"
        Retourne une liste de dicts
        """
        if not texte_buteurs.strip():
            return []
        
        # Étape 1 : découper par virgule
        # ["Lucien LAURENT 19'", " Marcel LANGILLER 40'", " Andre MASCHINOT 43'", " 87'"]
        elements = texte_buteurs.split(',')
        
        buteurs = []
        dernier_nom = None  # Variable pour mémoriser le nom du dernier buteur
        
        for element in elements:
            element = element.strip()
          
            # VÉRIFIER si l'élément contient des lettres
            # =============================================
            # any(c.isalpha() for c in element) 
            # → True si au moins une lettre (a-z, A-Z) est présente
            # → False si seulement chiffres, espaces, apostrophes
            contient_lettres = any(c.isalpha() for c in element)
            
            if contient_lettres:
                # =============================================
                # CAS 1 : Nouveau buteur (avec nom)
                # Exemple: "Lucien LAURENT 19'" ou "Andre MASCHINOT 43'"
                # =============================================
                # Regex pour capturer le nom et la minute
                # (.+?) : nom (non-greedy)
                # \s+ : espaces
                # (\d+) : minute
                # \' : apostrophe
                # (?:\((\w+)\))? : optionnel : (p) ou (og)
                match = re.search(r'(.+?)\s+(\d+)\'(?:\((\w+)\))?', element)
                
                if match:
                    nom = match.group(1).strip()
                    minute = int(match.group(2))
                    type_flag = match.group(3)
                    
                    # Mémoriser le nom pour les éventuelles minutes suivantes
                    dernier_nom = nom
                    
                    # Déterminer le type de but
                    if type_flag == 'p':
                        type_but = 'penalty'
                    elif type_flag == 'og':
                        type_but = 'contre_son_camp'
                    else:
                        type_but = 'normal'
                    
                    buteurs.append({
                        'nom': nom,
                        'minute': minute,
                        'type': type_but
                    })
            
            else:
                # CAS 2 : Minute seule (même buteur que précédent)
                # Exemple: "87'" ou "87'(p)"
                # =============================================
                # On vérifie qu'on a un dernier_nom (sécurité)
                if dernier_nom and element:
                    # Regex pour capturer seulement la minute
                    match = re.search(r'(\d+)\'(?:\((\w+)\))?', element)
                    
                    if match:
                        minute = int(match.group(1))
                        type_flag = match.group(2)
                        
                        # Déterminer le type de but
                        if type_flag == 'p':
                            type_but = 'penalty'
                        elif type_flag == 'og':
                            type_but = 'contre_son_camp'
                        else:
                            type_but = 'normal'
                        
                        # Ajouter un nouveau but avec le même nom
                        buteurs.append({
                            'nom': dernier_nom,
                            'minute': minute,
                            'type': type_but
                        })
        
        return buteurs
    
    # TRAITEMENT DOMICILE
    # =====================================================
    if len(parties) > 0 and parties[0].strip():
        buteurs_dom = parser_liste_buteurs(parties[0])
    
    # =====================================================
    # TRAITEMENT EXTERIEUR
    if len(parties) > 1 and parties[1].strip():
        buteurs_ext = parser_liste_buteurs(parties[1])
    
    return {
        'buteurs_dom': buteurs_dom,
        'buteurs_ext': buteurs_ext
    }



#================================================================
#=================== FONCTION PARSER DATE =======================
#================================================================

def parser_date(ligne_date: str) -> dict:
    """
    Parse une ligne de date comme 'Sun Jul 13' ou 'Sat Jul 19'
    """
    # Nettoyer les espaces
    ligne_date = ligne_date.strip()
    
    # Séparer les trois parties : jour_semaine, mois, jour
    parties = ligne_date.split()
    
    if len(parties) != 3:
        raise ValueError(f"Format de date invalide: {ligne_date}")
    
    jour_semaine = parties[0]
    mois = parties[1]
    jour = int(parties[2])
    
    # Dictionnaire de conversion mois (abréviation → numéro)
    mois_map = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
        'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
        'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    
    mois_num = mois_map.get(mois, 0)  # 0 si mois non trouvé
    
    return {
        'jour_semaine': jour_semaine,
        'jour': jour,
        'mois': mois,
        'mois_num': mois_num
    }


#================================================================
#============= FONCTION PARSER MATCH SANS STADE =================
#================================================================

def parser_match_sans_stade(ligne: str) -> dict:
    """
    Parse une ligne de match comme '  France v Mexico  4-1'
    (sans heure, sans stade)
    
    Returns:
        dict: {
            'equipe_dom': str,
            'equipe_ext': str,
            'score_dom': int,
            'score_ext': int
        }
    """
    ligne = ligne.strip()
    
    # Extraire le score
    score_match = re.search(r'(\d+)-(\d+)', ligne)
    if not score_match:
        raise ValueError(f"Score invalide: {ligne}")
    
    score_dom = int(score_match.group(1))
    score_ext = int(score_match.group(2))
    score_texte = score_match.group(0)
    
    # Enlever le score pour avoir les équipes
    sans_score = ligne.replace(score_texte, '').strip()
    
    # Séparer par ' v '
    if ' v ' not in sans_score:
        raise ValueError(f"Séparateur ' v ' non trouvé: {sans_score}")
    
    equipe_dom, equipe_ext = sans_score.split(' v ', 1)
    
    return {
        'equipe_dom': equipe_dom.strip(),
        'equipe_ext': equipe_ext.strip(),
        'score_dom': score_dom,
        'score_ext': score_ext
    }


#================================================================
#============= FONCTION PARSER COMPOSITION ======================
#================================================================

def parser_composition(ligne: str) -> dict:
    """
    Parse une ligne de composition comme:
    'France: Alex THEPOT - Marcel CAPELLE, Etienne MATTLER - Augustin CHANTREL...'
    
    Returns:
        dict: {
            'equipe': str,
            'joueurs': {
                'gardien': str,
                'defenseurs': list,
                'milieux': list,
                'attaquants': list
            }
        }
    """
    ligne = ligne.strip()
    
    # Séparer le nom de l'équipe du reste
    if ':' not in ligne:
        raise ValueError(f"Format composition invalide: {ligne}")
    
    equipe, joueurs_str = ligne.split(':', 1)
    equipe = equipe.strip()
    joueurs_str = joueurs_str.strip()
    
    # Pour l'instant, on retourne juste la liste brute
    # Plus tard on pourra parser les positions (- pour défense, etc.)
    joueurs = [j.strip() for j in joueurs_str.split(',')]
    
    return {
        'equipe': equipe,
        'joueurs_bruts': joueurs,
        'joueurs_texte': joueurs_str
    }


#================================================================
#============= FONCTION PARSER ARBITRES =========================
#================================================================

def parser_arbitres(ligne: str) -> list:
    """
    Parse une ligne d'arbitres comme:
    'Refs: Domingo LOMBARDI (URU), Henry CRISTOPHE (BEL), Gilberto REGO (BRA)'
    
    Returns:
        list: [{'nom': str, 'nationalite': str}, ...]
    """
    ligne = ligne.strip()
    
    # Enlever 'Refs: ' au début
    if ligne.startswith('Refs:'):
        ligne = ligne[5:].strip()
    
    arbitres = []
    
    # Séparer par virgule
    for arbitre in ligne.split(','):
        arbitre = arbitre.strip()
        # Extraire le nom et la nationalité: "Domingo LOMBARDI (URU)"
        match = re.search(r'(.+?)\s+\((\w+)\)', arbitre)
        if match:
            arbitres.append({
                'nom': match.group(1).strip(),
                'nationalite': match.group(2)
            })
        else:
            arbitres.append({
                'nom': arbitre,
                'nationalite': None
            })
    
    return arbitres


#================================================================
#=================== FONCTION PARSER FICHIER ====================
#================================================================

def parser_fichier(chemin: str) -> list:
    """
    Lit un fichier de matchs au format _full.txt et retourne une liste de matchs.
    
    Structure attendue:
        Sun Jul 13 15:00 UTC-3 @ Pocitos, Montevideo
          France v Mexico  4-1
             (Lucien LAURENT 19', ...)
        France: Alex THEPOT - Marcel CAPELLE...
        Mexico: Oscar BONFIGLIO - Rafael GARZA...
        Refs: Domingo LOMBARDI (URU), ...
    """
    
    with open(chemin, 'r', encoding='utf-8') as f:
        lignes = f.readlines()
    
    matchs = []
    
    # Variables d'état
    groupe_actuel = None
    match_actuel = None
    texte_buteurs = None
    ligne_buteurs_en_cours = False
    
    i = 0
    while i < len(lignes):
        ligne = lignes[i].rstrip('\n')
        
        # 1. Détection du groupe (▪▪ Group 1, ▪▪ Group 2, etc.)
        if ligne.startswith('▪▪'):
            groupe_actuel = ligne.strip()
            i += 1
            continue
        
        # 2. Détection d'une ligne qui contient date + heure + stade
        # Format: "Sun Jul 13 15:00 UTC-3 @ Pocitos, Montevideo"
        if re.match(r'^[A-Z][a-z]{2}\s+[A-Z][a-z]{2}\s+\d+', ligne.strip()):
            
            # Sauvegarder le match précédent s'il existe
            if match_actuel is not None:
                matchs.append(match_actuel)
            
            ligne_complete = ligne.strip()
            parties = ligne_complete.split()
            
            # Extraire la date (3 premiers éléments)
            # parties[0] = "Sun", parties[1] = "Jul", parties[2] = "13"
            jour_semaine = parties[0]
            mois = parties[1]
            jour = int(parties[2])
            
            # Construire le dictionnaire date
            mois_map = {
                'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
                'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
                'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
            }
            date_actuelle = {
                'jour_semaine': jour_semaine,
                'jour': jour,
                'mois': mois,
                'mois_num': mois_map.get(mois, 0)
            }
            
            # Extraire l'heure (4ème élément) et timezone (5ème élément)
            # parties[3] = "15:00", parties[4] = "UTC-3"
            heure_actuelle = parties[3]
            timezone_actuelle = parties[4]
            
            # Extraire le stade (tout ce qui est après @)
            # Exemple: "Sun Jul 13 15:00 UTC-3 @ Pocitos, Montevideo"
            # On cherche la position de '@'
            if '@' in ligne_complete:
                stade_actuel = ligne_complete.split('@', 1)[1].strip()
            else:
                stade_actuel = None
            
            # Créer un nouveau match vide avec les infos collectées
            match_actuel = {
                'groupe': groupe_actuel,
                'date': date_actuelle,
                'heure': heure_actuelle,
                'timezone': timezone_actuelle,
                'stade': stade_actuel,
                'equipe_dom': None,
                'equipe_ext': None,
                'score_dom': None,
                'score_ext': None,
                'buteurs_dom': [],
                'buteurs_ext': [],
                'composition_dom': None,
                'composition_ext': None,
                'arbitres': None
            }
            
            texte_buteurs = None
            ligne_buteurs_en_cours = False
            i += 1
            continue
        
        # 3. Détection d'une ligne de match (format: "  France v Mexico  4-1")
        if ' v ' in ligne and re.search(r'\d+-\d+', ligne):
            # Parser le match
            infos_match = parser_match_sans_stade(ligne)
            if match_actuel:
                match_actuel['equipe_dom'] = infos_match['equipe_dom']
                match_actuel['equipe_ext'] = infos_match['equipe_ext']
                match_actuel['score_dom'] = infos_match['score_dom']
                match_actuel['score_ext'] = infos_match['score_ext']
            i += 1
            continue
        
        # 4. Détection du début des buteurs (ligne qui commence par '(')
        if ligne.strip().startswith('('):
            texte_buteurs = ligne
            ligne_buteurs_en_cours = True
            i += 1
            continue
        
        # 5. Suite des buteurs (accumulation)
        if ligne_buteurs_en_cours:
            texte_buteurs += ' ' + ligne
            if ')' in ligne:
                buteurs = parser_ligne_buteur(texte_buteurs)
                if match_actuel:
                    match_actuel['buteurs_dom'] = buteurs['buteurs_dom']
                    match_actuel['buteurs_ext'] = buteurs['buteurs_ext']
                ligne_buteurs_en_cours = False
            i += 1
            continue
        
        # 6. Détection des compositions d'équipes (format: "France: Alex THEPOT...")
        if re.match(r'^[A-Z][a-zA-Z\s]+:', ligne.strip()) and not ligne.strip().startswith('Refs:'):
            texte_composition = ligne
            # Accumuler les lignes suivantes indentées
            while i + 1 < len(lignes):
                ligne_suivante = lignes[i + 1].rstrip('\n')
                if ligne_suivante.startswith('      '):  # ligne indentée = suite
                    texte_composition += ' ' + ligne_suivante.strip()
                    i += 1
                else:
                    break
            # Parser la composition complète
            if match_actuel:
                # Vérifier si c'est l'équipe domicile ou extérieure
                if match_actuel['equipe_dom'] and match_actuel['equipe_dom'] in ligne:
                    match_actuel['composition_dom'] = parser_composition(texte_composition)
                elif match_actuel['equipe_ext'] and match_actuel['equipe_ext'] in ligne:
                    match_actuel['composition_ext'] = parser_composition(texte_composition)
                # Si on n'a pas encore les équipes, on regarde le début de la ligne
                elif ligne.startswith('France:'):
                    match_actuel['composition_dom'] = parser_composition(texte_composition)
                elif ligne.startswith('Mexico:'):
                    match_actuel['composition_ext'] = parser_composition(texte_composition)
            i += 1
            continue
        
        # 7. Détection des arbitres (format: "Refs: ...")
        if ligne.strip().startswith('Refs:'):
            if match_actuel:
                match_actuel['arbitres'] = parser_arbitres(ligne)
            i += 1
            continue
        
        i += 1
    
    # Ajouter le dernier match
    if match_actuel is not None:
        matchs.append(match_actuel)
    
    return matchs

if __name__ == "__main__":
    import json
    matchs = parser_fichier(
        "/home/abdoulaye/Documents/Orange Digital center/projets/worldcup-data/worldcup/more/1930_full.txt"
    )
    print(f"Nombre de matchs trouvés: {len(matchs)}")
    print("\n=== Premier match ===")
    print(json.dumps(matchs[0], indent=2, ensure_ascii=False))