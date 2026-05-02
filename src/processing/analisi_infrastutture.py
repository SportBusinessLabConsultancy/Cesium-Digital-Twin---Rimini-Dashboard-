"""
Script per calcolare statistiche infrastrutturali per i grafici
Output: data/processed/stats_infrastrutture.json
"""

import json
import os
from shapely.geometry import shape
from math import radians, cos, sin, asin, sqrt

INPUT_STRADE    = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'strade_rimini.geojson')
INPUT_CICLABILI = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'ciclabili_rimini.geojson')
INPUT_PARCHEGGI = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'parcheggi_rimini.geojson')
OUTPUT_FILE     = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'stats_infrastrutture.json')

def haversine(lon1, lat1, lon2, lat2):
    """Calcola distanza in km tra due coordinate"""
    R = 6371
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return R * 2 * asin(sqrt(a))

def calcola_km_linestring(coords):
    """Calcola lunghezza in km di una LineString"""
    km = 0
    for i in range(len(coords) - 1):
        km += haversine(coords[i][0], coords[i][1], coords[i+1][0], coords[i+1][1])
    return km

def carica_geojson(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

# ============================================================
# NOMI LEGGIBILI PER TIPO STRADA
# ============================================================
HIGHWAY_LABELS = {
    'motorway':       'Autostrada',
    'motorway_link':  'Svincolo autostrada',
    'trunk':          'Superstrada',
    'trunk_link':     'Svincolo superstrada',
    'primary':        'Strada primaria',
    'primary_link':   'Svincolo primaria',
    'secondary':      'Strada secondaria',
    'tertiary':       'Strada terziaria',
    'tertiary_link':  'Svincolo terziaria',
    'residential':    'Strada residenziale',
    'service':        'Strada di servizio',
    'unclassified':   'Non classificata',
    'services':       'Area di servizio',
}

def analisi_strade(strade_data):
    print("Analizzando rete stradale...")
    km_per_tipo = {}
    count_per_tipo = {}

    for feat in strade_data['features']:
        highway = feat['properties'].get('highway', 'unclassified')
        geom = feat.get('geometry', {})
        if geom.get('type') == 'LineString':
            coords = geom['coordinates']
            km = calcola_km_linestring(coords)
            label = HIGHWAY_LABELS.get(highway, highway)
            km_per_tipo[label] = km_per_tipo.get(label, 0) + km
            count_per_tipo[label] = count_per_tipo.get(label, 0) + 1

    # Arrotonda e ordina
    km_per_tipo = {k: round(v, 1) for k, v in km_per_tipo.items()}
    top_tipi = sorted(km_per_tipo.items(), key=lambda x: -x[1])

    totale_km = sum(km_per_tipo.values())
    print(f"   Totale km strade: {totale_km:.1f}")
    for tipo, km in top_tipi[:8]:
        print(f"   {tipo}: {km} km")

    return {
        "km_per_tipo": km_per_tipo,
        "count_per_tipo": count_per_tipo,
        "totale_km": round(totale_km, 1),
        "top_tipi": [{"tipo": k, "km": v} for k, v in top_tipi],
    }

def analisi_ciclabili(ciclabili_data):
    print("Analizzando piste ciclabili...")
    totale_km = 0

    for feat in ciclabili_data['features']:
        geom = feat.get('geometry', {})
        if geom.get('type') == 'LineString':
            coords = geom['coordinates']
            totale_km += calcola_km_linestring(coords)

    print(f"   Totale km ciclabili: {totale_km:.1f}")
    return {"totale_km": round(totale_km, 1)}

def analisi_parcheggi(parcheggi_data):
    print("Analizzando parcheggi...")

    # Zone geografiche di Rimini
    ZONE = {
        "Centro":    {"lat_min": 44.050, "lat_max": 44.075, "lon_min": 12.530, "lon_max": 12.580},
        "Nord":      {"lat_min": 44.075, "lat_max": 44.130, "lon_min": 12.490, "lon_max": 12.570},
        "Sud":       {"lat_min": 44.020, "lat_max": 44.050, "lon_min": 12.510, "lon_max": 12.600},
        "Ovest":     {"lat_min": 44.040, "lat_max": 44.090, "lon_min": 12.460, "lon_max": 12.530},
        "Costa":     {"lat_min": 44.030, "lat_max": 44.130, "lon_min": 12.555, "lon_max": 12.620},
    }

    tipi = {}
    accesso = {}
    per_zona = {z: 0 for z in ZONE}
    non_classificati = 0

    for feat in parcheggi_data['features']:
        props = feat['properties']
        geom = feat.get('geometry', {})

        # Tipo parcheggio
        parking = props.get('parking', props.get('amenity', 'unknown'))
        if parking == 'parking':
            parking = 'superficie'
        tipi[parking] = tipi.get(parking, 0) + 1

        # Accesso
        acc = props.get('access', 'unknown')
        if acc in ['', None]:
            acc = 'non specificato'
        accesso[acc] = accesso.get(acc, 0) + 1

        # Zona geografica
        coords = None
        if geom.get('type') == 'Point':
            coords = geom['coordinates']
        elif geom.get('type') == 'Polygon':
            ring = geom['coordinates'][0]
            coords = [
                sum(p[0] for p in ring) / len(ring),
                sum(p[1] for p in ring) / len(ring)
            ]

        if coords:
            lon, lat = coords[0], coords[1]
            assegnato = False
            for zona, bounds in ZONE.items():
                if (bounds['lat_min'] <= lat <= bounds['lat_max'] and
                    bounds['lon_min'] <= lon <= bounds['lon_max']):
                    per_zona[zona] += 1
                    assegnato = True
                    break
            if not assegnato:
                non_classificati += 1

    per_zona['Altro'] = non_classificati

    print(f"   Totale parcheggi: {sum(tipi.values())}")
    print(f"   Per zona: {per_zona}")

    return {
        "tipi": tipi,
        "accesso": accesso,
        "per_zona": per_zona,
    }

def main():
    print("Caricando dati...")
    strade_data    = carica_geojson(INPUT_STRADE)
    ciclabili_data = carica_geojson(INPUT_CICLABILI)
    parcheggi_data = carica_geojson(INPUT_PARCHEGGI)

    stats = {
        "strade":    analisi_strade(strade_data),
        "ciclabili": analisi_ciclabili(ciclabili_data),
        "parcheggi": analisi_parcheggi(parcheggi_data),
    }

    # Media nazionale per confronto (fonte: MIT - Ministero Infrastrutture 2023)
    stats["benchmark"] = {
        "media_nazionale_ciclabili_per_100km_strade": 8.5,
        "rimini_ciclabili_per_100km_strade": round(
            stats["ciclabili"]["totale_km"] /
            stats["strade"]["totale_km"] * 100, 1
        ),
        "media_europea_ciclabili_km_per_abitante": 0.15,
        "rimini_ciclabili_km_per_abitante": round(
            stats["ciclabili"]["totale_km"] / 150755, 4
        ),
    }

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(f"\n Salvato in: {OUTPUT_FILE}")
    print(f"\n BENCHMARK:")
    print(f"   Rimini ciclabili per 100km strade: {stats['benchmark']['rimini_ciclabili_per_100km_strade']} km")
    print(f"   Media nazionale: {stats['benchmark']['media_nazionale_ciclabili_per_100km_strade']} km")
    print(f"   Rimini ciclabili per abitante: {stats['benchmark']['rimini_ciclabili_km_per_abitante']} km")
    print(f"   Media europea: {stats['benchmark']['media_europea_ciclabili_km_per_abitante']} km")

if __name__ == "__main__":
    main()