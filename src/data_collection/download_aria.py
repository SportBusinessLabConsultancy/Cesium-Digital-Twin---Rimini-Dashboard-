"""
Script per scaricare i dati sulla qualità dell'aria di Rimini
"""

import requests
import json
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'aria_rimini.geojson')
OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"

QUERY = """
[out:json][timeout:90];
relation["name"="Rimini"]["admin_level"="8"]["boundary"="administrative"];
map_to_area -> .rimini;
(
  node["man_made"="monitoring_station"](area.rimini);
  node["man_made"="chimney"](area.rimini);
  node["industrial"="factory"](area.rimini);
  way["industrial"="factory"](area.rimini);
  node["amenity"="fuel"](area.rimini);
);
out geom;
"""

def download_aria():
    print("Scaricando dati qualità dell'aria di Rimini...")
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
        if el['type'] == 'node':
            if tags.get('man_made') == 'monitoring_station':
                tipo = 'stazione_monitoraggio'
            elif tags.get('man_made') == 'chimney':
                tipo = 'camino'
            elif tags.get('industrial') == 'factory' or tags.get('amenity') == 'fuel':
                tipo = 'fonte_emissione'
            else:
                tipo = 'altro'
            feature = {
                "type": "Feature",
                "properties": {"id": el.get('id'), "tipo": tipo, "name": tags.get('name', '')},
                "geometry": {"type": "Point", "coordinates": [el['lon'], el['lat']]}
            }
            features.append(feature)
        elif el['type'] == 'way' and 'geometry' in el:
            coords = [[pt['lon'], pt['lat']] for pt in el['geometry']]
            if coords[0] != coords[-1]:
                coords.append(coords[0])
            feature = {
                "type": "Feature",
                "properties": {"id": el.get('id'), "tipo": "area_industriale", "name": tags.get('name', '')},
                "geometry": {"type": "Polygon", "coordinates": [coords]}
            }
            features.append(feature)
    geojson = {"type": "FeatureCollection", "features": features}
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    print(f" Salvato in: {OUTPUT_FILE}")
    print(f"   Numero di elementi: {len(features)}")

if __name__ == "__main__":
    download_aria()