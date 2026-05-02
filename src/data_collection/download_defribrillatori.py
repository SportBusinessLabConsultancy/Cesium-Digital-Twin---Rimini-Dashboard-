"""
Script per scaricare i defibrillatori di Rimini
"""

import requests
import json
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'defibrillatori_rimini.geojson')
OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"

QUERY = """
[out:json][timeout:90];
relation["name"="Rimini"]["admin_level"="8"]["boundary"="administrative"];
map_to_area -> .rimini;
(
  node["emergency"="defibrillator"](area.rimini);
);
out geom;
"""

def download_defibrillatori():
    print("Scaricando defibrillatori di Rimini...")
    response = requests.post(OVERPASS_URL, data=QUERY)
    if response.status_code != 200:
        print(f"Errore: {response.status_code}")
        return
    if not response.text.strip():
        print("Risposta vuota. Riprova.")
        return
    try:
        data = response.json()
    except Exception as e:
        print(f"Errore JSON: {e}")
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
            feature = {
                "type": "Feature",
                "properties": {
                    "id": el.get('id'),
                    "tipo": "defibrillatore",
                    "name": tags.get('name', ''),
                    "indoor": tags.get('indoor', ''),
                    "access": tags.get('access', ''),
                    "opening_hours": tags.get('opening_hours', ''),
                    "operator": tags.get('operator', ''),
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [el['lon'], el['lat']]
                }
            }
            features.append(feature)
    geojson = {"type": "FeatureCollection", "features": features}
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    print(f" Salvato in: {OUTPUT_FILE}")
    print(f"   Numero di defibrillatori: {len(features)}")

if __name__ == "__main__":
    download_defibrillatori()