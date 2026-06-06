import json
import os

# ===================================================================
# FONCTION : sauvegarder_json
# ===================================================================
# But : Sauvegarder une liste de matchs (dictionnaires Python) dans un fichier JSON
# ===================================================================

def sauvegarder_json(matchs: list, chemin_sortie: str):
    """
    Sauvegarde une liste de matchs dans un fichier JSON.
    """
    # os.path.dirname(chemin_sortie) → extrait le dossier du chemin
    # Exemple: "data/1930/matchs.json" → "data/1930"
    # =================================================================
    
    dossier = os.path.dirname(chemin_sortie)  # Ex: "data/1930" ou "output"
    
    if dossier:  # Vérifie si dossier n'est pas vide
        os.makedirs(dossier, exist_ok=True)
        # exist_ok=True = "exist ok" = ne pas planter si le dossier existe déjà
    
    # 'w' (write) → mode écriture (écrase le fichier s'il existe)
    # encoding='utf-8' → supporte les accents et caractères spéciaux
    # =================================================================
    
    with open(chemin_sortie, 'w', encoding='utf-8') as f:
        # json.dump() = convertit un objet Python en JSON et l'écrit dans un fichier
        #
        # Paramètres :
        # - matchs : l'objet Python à convertir (liste de dicts)
        # - f : le fichier où écrire
        # - ensure_ascii=False : permet d'avoir des accents (FrançaiS au lieu de Fran\u00e7aiS)
        # - indent=2 : indentation de 2 espaces pour rendre le JSON lisible
        # =================================================================
        
        json.dump(matchs, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {len(matchs)} matchs sauvegardés dans {chemin_sortie}")