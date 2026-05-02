"""
Script per calcolare statistiche territoriali per i grafici
Output: data/processed/stats_territorio.json
"""

import json
import os
from shapely.geometry import shape

INPUT_SUOLO    = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'uso_suolo_rimini.geojson')
INPUT_EDIFICI  = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'edifici_rimini.geojson')
INPUT_QUARTIERI = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'quartieri_rimini.geojson')
OUTPUT_FILE    = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'stats_territorio.json')

# Fattore conversione gradi → m² (approssimato per latitudine 44°)
DEG2M2 = 111320 * 111320 * 0.72  # ~8.9 miliardi m² per grado²

def calcola_superficie_m2(geometry):
    """Calcola la superficie in m² di un poligono GeoJSON"""
    try:
        geom = shape(geometry)
        return abs(geom.area) * DEG2M2
    except:
        return 0

def carica_geojson(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def analisi_uso_suolo(suolo_data):
    """Calcola superficie totale per tipo di uso del suolo"""
    print("Analizzando uso del suolo...")
    superfici = {}
    conteggi = {}

    for feat in suolo_data['features']:
        landuse = feat['properties'].get('landuse', 'other')
        geom = feat.get('geometry', {})
        if geom.get('type') == 'Polygon':
            sup = calcola_superficie_m2(geom)
            superfici[landuse] = superfici.get(landuse, 0) + sup
            conteggi[landuse] = conteggi.get(landuse, 0) + 1

    # Converti in ettari e ordina
    superfici_ha = {k: round(v / 10000, 1) for k, v in superfici.items()}
    top10 = sorted(superfici_ha.items(), key=lambda x: -x[1])[:10]

    print(f"   Tipi trovati: {len(superfici_ha)}")
    for tipo, ha in top10:
        print(f"   {tipo}: {ha} ha")

    return {
        "superfici_ha": superfici_ha,
        "conteggi": conteggi,
        "top10_superficie": [{"tipo": k, "ha": v} for k, v in top10],
    }

def analisi_edifici(edifici_data, quartieri_data):
    """Analizza distribuzione edifici per tipo e per quartiere"""
    print("Analizzando edifici...")

    # Distribuzione per tipo
    tipi = {}
    for feat in edifici_data['features']:
        tipo = feat['properties'].get('building', 'yes')
        tipi[tipo] = tipi.get(tipo, 0) + 1

    top_tipi = sorted(tipi.items(), key=lambda x: -x[1])[:15]
    print(f"   Tipi edifici trovati: {len(tipi)}")

    # Associa edifici ai quartieri tramite punto centrale
    from shapely.geometry import Point, shape as shp

    # Crea poligoni quartieri (solo quelli con polygon geometry)
    quartieri_poly = []
    for feat in quartieri_data['features']:
        geom = feat.get('geometry', {})
        nome = feat['properties'].get('nome', '')
        if geom.get('type') == 'Polygon':
            try:
                poly = shp(geom)
                quartieri_poly.append((nome, poly))
            except:
                pass

    print(f"   Quartieri con poligono: {len(quartieri_poly)}")

    # Conta edifici per quartiere
    edifici_per_quartiere = {}
    tipi_per_quartiere = {}

    if quartieri_poly:
        for feat in edifici_data['features']:
            geom = feat.get('geometry', {})
            if geom.get('type') != 'Polygon':
                continue
            try:
                poly = shp(geom)
                centroid = poly.centroid
                tipo = feat['properties'].get('building', 'yes')

                for nome_q, poly_q in quartieri_poly:
                    if poly_q.contains(centroid):
                        edifici_per_quartiere[nome_q] = edifici_per_quartiere.get(nome_q, 0) + 1
                        if nome_q not in tipi_per_quartiere:
                            tipi_per_quartiere[nome_q] = {}
                        tipi_per_quartiere[nome_q][tipo] = tipi_per_quartiere[nome_q].get(tipo, 0) + 1
                        break
            except:
                continue
    else:
        print("    Nessun poligono quartiere disponibile — skip analisi per quartiere")

    return {
        "tipi_totali": {k: v for k, v in top_tipi},
        "edifici_per_quartiere": edifici_per_quartiere,
        "tipi_per_quartiere": tipi_per_quartiere,
    }

def main():
    print("Caricando dati...")
    suolo_data    = carica_geojson(INPUT_SUOLO)
    edifici_data  = carica_geojson(INPUT_EDIFICI)
    quartieri_data = carica_geojson(INPUT_QUARTIERI)

    stats = {
        "uso_suolo": analisi_uso_suolo(suolo_data),
        "edifici":   analisi_edifici(edifici_data, quartieri_data),
    }

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(f"\n Salvato in: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()