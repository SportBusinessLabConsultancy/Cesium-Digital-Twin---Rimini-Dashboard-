"""
processa_monumenti.py
─────────────────────────────────────────────────────────────
Esegui questo script UNA VOLTA nella cartella data/processed/
per aggiungere il campo 'tipo' al file grezzo del SIT.

USO (dalla cartella data/processed/):
    python processa_monumenti.py
"""
import json, os

FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'monumenti_rimini.geojson')

def normalizza(cat, uso):
    cat = (cat or '').lower().strip()
    uso = (uso or '').lower().strip()
    if 'culto' in cat or 'logo di culto' in cat:
        if 'convento' in uso: return 'convento'
        return 'chiesa'
    elif 'fortif' in cat:
        return 'castello' if 'rocca' in uso else 'arco'
    elif 'infrastruttur' in cat:
        return 'ponte' if 'ponte' in uso else 'infrastruttura'
    elif 'monumento' in cat: return 'monumento'
    elif 'cimiter' in cat:   return 'cimitero'
    elif 'pubblico' in cat or 'pubblic' in cat:
        return 'teatro' if 'teatro' in uso or 'anfiteatro' in uso else 'palazzo_pubblico'
    elif 'residenziale' in cat: return 'palazzo_privato'
    elif 'ricettiv' in cat:     return 'ricettivo'
    elif 'produttiv' in cat or 'commerciale' in cat: return 'commerciale'
    return 'altro'

with open(FILE, encoding='utf-8') as f:
    data = json.load(f)

# Verifica se già processato
if data['features'] and 'tipo' in data['features'][0]['properties']:
    print(" File già processato — campo 'tipo' presente")
else:
    print(f"Processando {len(data['features'])} features...")
    from collections import Counter
    tipi = Counter()
    for feat in data['features']:
        p = feat['properties']
        tipo = normalizza(p.get('CATEGORIAU',''), p.get('USO',''))
        p['tipo']       = tipo
        p['nome']       = p.get('NOME','') or p.get('USO','')
        p['tipo_label'] = {'chiesa':'Chiese','palazzo_privato':'Edifici residenziali storici',
            'palazzo_pubblico':'Edifici pubblici storici','convento':'Conventi',
            'infrastruttura':'Infrastrutture storiche','arco':'Porte e mura',
            'teatro':'Teatri','castello':'Rocche e torri','ponte':'Ponti storici',
            'ricettivo':'Strutture ricettive storiche','monumento':'Monumenti',
            'commerciale':'Edifici commerciali','cimitero':'Cimiteri','altro':'Altro'
        }.get(tipo, tipo)
        tipi[p['tipo_label']] += 1

    with open(FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f" Salvato con campo 'tipo':")
    for t,n in sorted(tipi.items(), key=lambda x:-x[1]):
        print(f"   {t}: {n}")