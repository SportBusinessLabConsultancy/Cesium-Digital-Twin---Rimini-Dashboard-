"""
Script per scaricare le piste ciclabili di Rimini
"""

import requests
import json
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'ciclabili_rimini.geojson')

OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"

QUERY = """
[out:json][timeout:90];
relation["name"="Rimini"]["admin_level"="8"]["boundary"="administrative"];
map_to_area -> .rimini;
(
  way["highway"="cycleway"](area.rimini);
  way["bicycle"="designated"](area.rimini);
  way["cycleway"~"lane|track|opposite_lane|opposite_track"](area.rimini);
);
out geom;
"""

def download_ciclabili():
    print("Scaricando piste ciclabili di Rimini...")

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
        if el['type'] == 'way' and 'geometry' in el:
            coords = [[pt['lon'], pt['lat']] for pt in el['geometry']]

            feature = {
                "type": "Feature",
                "properties": {
                    "id": el.get('id'),
                    "highway": el.get('tags', {}).get('highway', ''),
                    "cycleway": el.get('tags', {}).get('cycleway', ''),
                    "name": el.get('tags', {}).get('name', ''),
                    "surface": el.get('tags', {}).get('surface', ''),
                    "lit": el.get('tags', {}).get('lit', ''),
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": coords
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
    print(f"   Numero di tratti ciclabili: {len(features)}")

if __name__ == "__main__":
    download_ciclabili()