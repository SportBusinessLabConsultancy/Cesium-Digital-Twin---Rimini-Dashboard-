"""
Script per scaricare gli incidenti stradali di Rimini
"""

import requests
import json
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'incidenti_rimini.geojson')

OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"

QUERY = """
[out:json][timeout:90];
relation["name"="Rimini"]["admin_level"="8"]["boundary"="administrative"];
map_to_area -> .rimini;
(
  node["accident"](area.rimini);
  node["highway"="speed_camera"](area.rimini);
  node["highway"="traffic_signals"](area.rimini);
  node["crossing"="traffic_signals"](area.rimini);
);
out geom;
"""

def download_incidenti():
    print("Scaricando dati traffico e incidenti di Rimini...")

    response = requests.post(OVERPASS_URL, data=QUERY)

    if response.status_code != 200:
        print(f"Errore nella richiesta: {response.status_code}")
        return

    data = response.json()
    elements = data.get('elements', [])

    if not elements:
        print("Nessun dato ricevuto.")
        return

    print(f"Elementi ricevuti: {len(elements)}")

    features = []
    for el in elements:
        if el['type'] == 'node':
            tags = el.get('tags', {})

            if tags.get('accident'):
                tipo = 'incidente'
            elif tags.get('highway') == 'speed_camera':
                tipo = 'autovelox'
            elif tags.get('highway') == 'traffic_signals':
                tipo = 'semaforo'
            elif tags.get('crossing') == 'traffic_signals':
                tipo = 'attraversamento_semaforico'
            else:
                tipo = 'altro'

            feature = {
                "type": "Feature",
                "properties": {
                    "id": el.get('id'),
                    "tipo": tipo,
                    "name": tags.get('name', ''),
                    "ref": tags.get('ref', ''),
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [el['lon'], el['lat']]
                }
            }
            features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)

    print(f" Salvato in: {OUTPUT_FILE}")
    print(f"   Numero di elementi: {len(features)}")

    # Riepilogo per tipo
    tipi = {}
    for f in features:
        t = f['properties']['tipo']
        tipi[t] = tipi.get(t, 0) + 1
    print("\n Riepilogo per tipo:")
    for tipo, count in sorted(tipi.items(), key=lambda x: -x[1]):
        print(f"   {tipo}: {count}")

if __name__ == "__main__":
    download_incidenti()