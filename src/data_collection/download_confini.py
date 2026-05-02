"""
Script per scaricare i confini amministrativi di Rimini
"""

import requests
import json
import os


OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'confini_rimini.geojson')

OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"

QUERY = """
[out:json][timeout:60];
relation["name"="Rimini"]["admin_level"="8"]["boundary"="administrative"];
out geom;
"""

def download_confini():
    print("Scaricando confini amministrativi di Rimini...")

    response = requests.post(OVERPASS_URL, data=QUERY)

    if response.status_code != 200:
        print(f"Errore nella richiesta: {response.status_code}")
        return

    data = response.json()

    if not data['elements']:
        print("Nessun dato ricevuto.")
        return

    # Costruisci il GeoJSON
    relation = data['elements'][0]
    coordinates = []

    for member in relation['members']:
        if member['type'] == 'way' and 'geometry' in member:
            ring = [[pt['lon'], pt['lat']] for pt in member['geometry']]
            coordinates.append(ring)

    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "name": "Comune di Rimini",
                    "type": "administrative_boundary",
                    "admin_level": 8
                },
                "geometry": {
                    "type": "MultiLineString",
                    "coordinates": coordinates
                }
            }
        ]
    }

    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)

    print(f" Salvato in: {OUTPUT_FILE}")
    print(f"   Numero di segmenti: {len(coordinates)}")

if __name__ == "__main__":
    download_confini()