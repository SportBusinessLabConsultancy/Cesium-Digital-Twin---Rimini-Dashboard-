"""
Script per scaricare i parcheggi di Rimini
"""

import requests
import json
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'parcheggi_rimini.geojson')

OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"

QUERY = """
[out:json][timeout:90];
relation["name"="Rimini"]["admin_level"="8"]["boundary"="administrative"];
map_to_area -> .rimini;
(
  way["amenity"="parking"](area.rimini);
  node["amenity"="parking"](area.rimini);
  relation["amenity"="parking"](area.rimini);
);
out geom;
"""

def download_parcheggi():
    print("Scaricando parcheggi di Rimini...")

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
                    "name": el.get('tags', {}).get('name', ''),
                    "access": el.get('tags', {}).get('access', ''),
                    "fee": el.get('tags', {}).get('fee', ''),
                    "capacity": el.get('tags', {}).get('capacity', ''),
                    "parking": el.get('tags', {}).get('parking', ''),
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [el['lon'], el['lat']]
                }
            }
            features.append(feature)

        elif el['type'] == 'way' and 'geometry' in el:
            coords = [[pt['lon'], pt['lat']] for pt in el['geometry']]
            if coords[0] != coords[-1]:
                coords.append(coords[0])

            feature = {
                "type": "Feature",
                "properties": {
                    "id": el.get('id'),
                    "name": el.get('tags', {}).get('name', ''),
                    "access": el.get('tags', {}).get('access', ''),
                    "fee": el.get('tags', {}).get('fee', ''),
                    "capacity": el.get('tags', {}).get('capacity', ''),
                    "parking": el.get('tags', {}).get('parking', ''),
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coords]
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
    print(f"   Numero di parcheggi: {len(features)}")

if __name__ == "__main__":
    download_parcheggi()