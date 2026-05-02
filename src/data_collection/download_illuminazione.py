"""
Script per scaricare l'illuminazione pubblica di Rimini
"""

import requests
import json
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'illuminazione_rimini.geojson')

OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"

QUERY = """
[out:json][timeout:90];
relation["name"="Rimini"]["admin_level"="8"]["boundary"="administrative"];
map_to_area -> .rimini;
(
  node["highway"="street_lamp"](area.rimini);
);
out geom;
"""

def download_illuminazione():
    print("Scaricando illuminazione pubblica di Rimini...")

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
            feature = {
                "type": "Feature",
                "properties": {
                    "id": el.get('id'),
                    "lamp_type": el.get('tags', {}).get('lamp_type', ''),
                    "light_source": el.get('tags', {}).get('light_source', ''),
                    "support": el.get('tags', {}).get('support', ''),
                    "lit": el.get('tags', {}).get('lit', ''),
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
    print(f"   Numero di lampioni: {len(features)}")

if __name__ == "__main__":
    download_illuminazione()