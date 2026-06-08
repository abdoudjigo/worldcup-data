import json

with open("/home/abdoulaye/Documents/Orange Digital center/projets/worldcup-data/data/worldcup_raw.json") as f:
    matchs = json.load(f)

# Chercher la finale 1998
for m in matchs:
    if m['annee'] == 1998 and 'France' in [m['equipe_dom'], m['equipe_ext']] and 'Brazil' in [m['equipe_dom'], m['equipe_ext']]:
        print("equipe_dom:", m['equipe_dom'])
        print("equipe_ext:", m['equipe_ext'])
        print("buteurs_dom:", m['buteurs_dom'])
        print("buteurs_ext:", m['buteurs_ext'])

import json

with open("/home/abdoulaye/Documents/Orange Digital center/projets/worldcup-data/data/worldcup_raw.json") as f:
    matchs = json.load(f)

# Chercher des matchs avec Semi ou Final dans le groupe
for m in matchs:
    if m.get('groupe') and ('Final' in str(m['groupe']) or 'Semi' in str(m['groupe'])):
        print(m['annee'], m['groupe'], m['equipe_dom'], m['equipe_ext'])
        break

# Voir aussi les matchs sans groupe
count = sum(1 for m in matchs if not m.get('groupe'))
print(f"\nMatchs sans groupe: {count}")

# Voir les valeurs uniques de groupe
groupes = set(m.get('groupe') for m in matchs)
print(f"\nGroupes uniques: {groupes}")