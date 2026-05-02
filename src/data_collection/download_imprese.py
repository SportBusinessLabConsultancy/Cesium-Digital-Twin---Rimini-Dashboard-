"""
Script per scaricare le imprese di Rimini
"""

import requests
import json
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'imprese_rimini.geojson')
OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"

QUERY = """
[out:json][timeout:90];
relation["name"="Rimini"]["admin_level"="8"]["boundary"="administrative"];
map_to_area -> .rimini;
(
  node["office"](area.rimini);
  node["shop"](area.rimini);
  node["craft"](area.rimini);
  node["industrial"](area.rimini);
  way["office"](area.rimini);
  way["shop"](area.rimini);
);
out geom;
"""

def download_imprese():
    print("Scaricando imprese di Rimini...")
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
        tags = el.get('tags', {})
        office = tags.get('office', '')
        shop = tags.get('shop', '')
        craft = tags.get('craft', '')
        if office:
            tipo = f"ufficio_{office}"
        elif shop:
            tipo = f"negozio_{shop}"
        elif craft:
            tipo = f"artigianato_{craft}"
        else:
            tipo = 'altro'
        if el['type'] == 'node':
            feature = {
                "type": "Feature",
                "properties": {
                    "id": el.get('id'),
                    "tipo": tipo,
                    "name": tags.get('name', ''),
                    "phone": tags.get('phone', ''),
                    "website": tags.get('website', ''),
                    "opening_hours": tags.get('opening_hours', ''),
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
                    "tipo": tipo,
                    "name": tags.get('name', ''),
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coords]
                }
            }
            features.append(feature)
    geojson = {"type": "FeatureCollection", "features": features}
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    print(f" Salvato in: {OUTPUT_FILE}")
    print(f"   Numero di imprese: {len(features)}")

if __name__ == "__main__":
    download_imprese()