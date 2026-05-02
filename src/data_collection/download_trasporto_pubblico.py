"""
Script per scaricare il trasporto pubblico di Rimini
"""

import requests
import json
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'trasporto_pubblico_rimini.geojson')

OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"

QUERY = """
[out:json][timeout:90];
relation["name"="Rimini"]["admin_level"="8"]["boundary"="administrative"];
map_to_area -> .rimini;
(
  node["highway"="bus_stop"](area.rimini);
  node["amenity"="bus_station"](area.rimini);
  node["railway"="station"](area.rimini);
  node["railway"="halt"](area.rimini);
  node["amenity"="ferry_terminal"](area.rimini);
  node["aeroway"="terminal"](area.rimini);
);
out geom;
"""

def download_trasporto_pubblico():
    print("Scaricando trasporto pubblico di Rimini...")

    response = requests.post(OVERPASS_URL, data=QUERY)

    if response.status_code != 200:
        print(f"Errore nella richiesta: {response.status_code}")
        return

    if not response.text.strip():
        print("Risposta vuota dal server. Riprova tra qualche secondo.")
        return

    try:
        data = response.json()
    except Exception as e:
        print(f"Errore nel parsing JSON: {e}")
        return

    elements = data.get('elements', [])

    if not elements:
        print("Nessun dato ricevuto.")
        return

    print(f"Elementi ricevuti: {len(elements)}")

    features = []
    for el in elements:
        if el['type'] == 'node':
            tags = el.get('tags', {})

            if tags.get('highway') == 'bus_stop':
                tipo = 'fermata_bus'
            elif tags.get('amenity') == 'bus_station':
                tipo = 'stazione_bus'
            elif tags.get('railway') in ['station', 'halt']:
                tipo = 'stazione_ferroviaria'
            elif tags.get('amenity') == 'ferry_terminal':
                tipo = 'terminal_traghetti'
            elif tags.get('aeroway') == 'terminal':
                tipo = 'aeroporto'
            else:
                tipo = 'altro'

            feature = {
                "type": "Feature",
                "properties": {
                    "id": el.get('id'),
                    "tipo": tipo,
                    "name": tags.get('name', ''),
                    "ref": tags.get('ref', ''),
                    "operator": tags.get('operator', ''),
                    "network": tags.get('network', ''),
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
    download_trasporto_pubblico()