# Cette fonction lit un fichier texte et retourne une liste de matchs
from parser import parser_fichier
# Cette fonction sauvegarde une liste de matchs dans un fichier JSON
from utils import sauvegarder_json


# ===================================================================
# POINT D'ENTRÉE PRINCIPAL
# ===================================================================

if __name__ == "__main__":
    
    import os
    import json

    # Dossier source : là où se trouvent les fichiers _full.txt
    base = "/home/abdoulaye/Documents/Orange Digital center/projets/worldcup-data/worldcup/more/"    
    # Dossier destination : fichier JSON de sortie unique
    sortie = "/home/abdoulaye/Documents/Orange Digital center/projets/worldcup-data/data/worldcup_raw.json"

    # =================================================================
    # tous_les_matchs = []  → crée une liste vide
    # On va y ajouter les matchs de chaque année
    # =================================================================
    
    tous_les_matchs = []
    
    # os.listdir(base) → retourne la liste de TOUS les fichiers/dossiers
    # Exemple : ["1930_full.txt", "1934_full.txt", "README.md", ...]
    #
    # sorted() → trie par ordre alphabétique (1930, 1934, 1938...)
    # =================================================================
    
    for fichier in sorted(os.listdir(base)):
        
        # =================================================================
        # FILTRAGE : garder uniquement les fichiers _full.txt
        # =================================================================
        
        if fichier.endswith('_full.txt'):

            # fichier = "1930_full.txt"
            # .replace('_full.txt', '') → enlève "_full.txt" → "1930"
            # =================================================================
            
            annee = fichier.replace('_full.txt', '')  # "1930"
            
            # os.path.join(base, fichier) → fusionne dossier + nom du fichier
            # Exemple : base + "1930_full.txt" 
            # =================================================================
            
            chemin = os.path.join(base, fichier)

            # parser_fichier(chemin) → lit le fichier et retourne une LISTE
            # de matchs pour cette année (ex: 18 matchs pour 1930)
            # =================================================================
            
            matchs = parser_fichier(chemin)
            
            # Pour chaque match de la liste, on ajoute une clé "annee"
            # Exemple : match devient {..., "annee": 1930}
            # =================================================================
            
            for match in matchs:
                match['annee'] = int(annee)  # Convertit "1930" en 1930 (int)
            
            tous_les_matchs.extend(matchs)
    
    # =================================================================
    # SAUVEGARDER EN JSON
    # =================================================================
    # sauvegarder_json(liste_matchs, chemin_destination)
    # Crée le dossier si nécessaire et écrit le fichier JSON
    # =================================================================
    
    sauvegarder_json(tous_les_matchs, sortie)
    