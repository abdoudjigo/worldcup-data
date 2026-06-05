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

