"""
Script per scaricare dati sul rumore urbano di Rimini
"""

import requests
import json
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'rumore_rimini.geojson')
OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"

QUERY = """
[out:json][timeout:90];
relation["name"="Rimini"]["admin_level"="8"]["boundary"="administrative"];
map_to_area -> .rimini;
(
  node["amenity"="nightclub"](area.rimini);
  node["amenity"="bar"](area.rimini);
  node["amenity"="pub"](area.rimini);
  node["aeroway"="runway"](area.rimini);
  way["aeroway"="runway"](area.rimini);
  way["railway"="rail"](area.rimini);
  way["highway"="motorway"](area.rimini);
);
out geom;
"""

def download_rumore():
    print("Scaricando dati rumore urbano di Rimini...")
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
        amenity = tags.get('amenity', '')
        if amenity == 'nightclub':
            tipo = 'discoteca'
        elif amenity in ['bar', 'pub']:
            tipo = 'locale_notturno'
        elif tags.get('aeroway'):
            tipo = 'aeroporto'
        elif tags.get('railway') == 'rail':
            tipo = 'ferrovia'
        elif tags.get('highway') == 'motorway':
            tipo = 'autostrada'
        else:
            tipo = 'altro'
        if el['type'] == 'node':
            feature = {
                "type": "Feature",
                "properties": {"id": el.get('id'), "tipo": tipo, "name": tags.get('name', '')},
                "geometry": {"type": "Point", "coordinates": [el['lon'], el['lat']]}
            }
            features.append(feature)
        elif el['type'] == 'way' and 'geometry' in el:
            coords = [[pt['lon'], pt['lat']] for pt in el['geometry']]
            feature = {
                "type": "Feature",
                "properties": {"id": el.get('id'), "tipo": tipo, "name": tags.get('name', '')},
                "geometry": {"type": "LineString", "coordinates": coords}
            }
            features.append(feature)
    geojson = {"type": "FeatureCollection", "features": features}
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    print(f" Salvato in: {OUTPUT_FILE}")
    print(f"   Numero di elementi: {len(features)}")

if __name__ == "__main__":
    download_rumore()