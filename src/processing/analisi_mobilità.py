"""
Script per calcolare statistiche mobilità per i grafici
Output: data/processed/stats_mobilita.json
"""

import json
import os

INPUT_TRAFFICO  = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'traffico_rimini.geojson')
INPUT_INCIDENTI = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'incidenti_rimini.geojson')
INPUT_TPL       = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'trasporto_pubblico_rimini.geojson')
OUTPUT_FILE     = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'stats_mobilita.json')

def carica_geojson(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def analisi_traffico(data):
    print("Analizzando traffico...")
    maxspeed = {}
    lanes = {}
    highway = {}

    for feat in data['features']:
        p = feat['properties']

        # Velocità massima
        speed = p.get('maxspeed', '').strip()
        if speed == '': speed = 'Non specificato'
        maxspeed[speed] = maxspeed.get(speed, 0) + 1

        # Corsie
        l = p.get('lanes', '').strip()
        if l == '': l = 'Non specificato'
        lanes[l] = lanes.get(l, 0) + 1

        # Tipo strada
        h = p.get('highway', 'unclassified')
        highway[h] = highway.get(h, 0) + 1

    # Ordina per valore
    maxspeed_sorted = sorted(
        [(k, v) for k, v in maxspeed.items() if k != 'Non specificato'],
        key=lambda x: int(x[0]) if x[0].isdigit() else 0
    )
    # Aggiungi non specificato in fondo
    if 'Non specificato' in maxspeed:
        maxspeed_sorted.append(('Non spec.', maxspeed['Non specificato']))

    print(f"   Tratti totali: {len(data['features'])}")
    print(f"   Limiti velocità trovati: {len(maxspeed)}")

    return {
        "maxspeed": {k: v for k, v in maxspeed_sorted},
        "lanes": lanes,
        "highway": highway,
        "totale_tratti": len(data['features']),
    }

def analisi_incidenti(data):
    print("Analizzando sicurezza stradale...")
    tipi = {}

    LABELS = {
        'semaforo': 'Semaforo',
        'attraversamento_semaforico': 'Attraversamento semaforico',
        'autovelox': 'Autovelox',
    }

    for feat in data['features']:
        tipo = feat['properties'].get('tipo', 'altro')
        label = LABELS.get(tipo, tipo)
        tipi[label] = tipi.get(label, 0) + 1

    print(f"   Elementi totali: {len(data['features'])}")
    for k, v in tipi.items():
        print(f"   {k}: {v}")

    return {
        "tipi": tipi,
        "totale": len(data['features']),
    }

def analisi_tpl(data):
    print("Analizzando trasporto pubblico...")
    tipi = {}
    operatori_raw = {}

    TIPO_LABELS = {
        'fermata_bus': 'Fermata bus',
        'stazione_ferroviaria': 'Stazione ferroviaria',
        'stazione_bus': 'Stazione bus',
        'terminal_traghetti': 'Terminal traghetti',
    }

    # Normalizza nomi operatori
    def normalizza_operatore(op):
        op = op.strip()
        if 'Start Romagna' in op: return 'Start Romagna'
        if op == '': return 'Non specificato'
        return op

    for feat in data['features']:
        p = feat['properties']

        tipo = p.get('tipo', 'altro')
        label = TIPO_LABELS.get(tipo, tipo)
        tipi[label] = tipi.get(label, 0) + 1

        op = normalizza_operatore(p.get('operator', ''))
        operatori_raw[op] = operatori_raw.get(op, 0) + 1

    # Rimuovi non specificato dagli operatori se vuoi
    operatori = {k: v for k, v in operatori_raw.items() if k != 'Non specificato'}
    operatori['Non specificato'] = operatori_raw.get('Non specificato', 0)

    print(f"   Fermate totali: {len(data['features'])}")
    for k, v in tipi.items():
        print(f"   {k}: {v}")
    print("   Operatori normalizzati:")
    for k, v in sorted(operatori.items(), key=lambda x: -x[1]):
        print(f"   {k}: {v}")

    return {
        "tipi": tipi,
        "operatori": operatori,
        "totale": len(data['features']),
    }

def main():
    print("Caricando dati mobilità...")
    traffico_data  = carica_geojson(INPUT_TRAFFICO)
    incidenti_data = carica_geojson(INPUT_INCIDENTI)
    tpl_data       = carica_geojson(INPUT_TPL)

    stats = {
        "traffico":  analisi_traffico(traffico_data),
        "sicurezza": analisi_incidenti(incidenti_data),
        "tpl":       analisi_tpl(tpl_data),
    }

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(f"\n Salvato in: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()