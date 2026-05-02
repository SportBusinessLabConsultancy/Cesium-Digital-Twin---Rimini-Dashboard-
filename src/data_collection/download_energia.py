"""
Script per scaricare dati sui consumi energetici di Rimini
"""

import requests
import json
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'energia_rimini.geojson')
OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"

QUERY = """
[out:json][timeout:90];
relation["name"="Rimini"]["admin_level"="8"]["boundary"="administrative"];
map_to_area -> .rimini;
(
  node["power"="plant"](area.rimini);
  way["power"="plant"](area.rimini);
  node["power"="substation"](area.rimini);
  way["power"="substation"](area.rimini);
  node["generator:source"="solar"](area.rimini);
  way["generator:source"="solar"](area.rimini);
  node["generator:source"="wind"](area.rimini);
  node["amenity"="charging_station"](area.rimini);
);
out geom;
"""

def download_energia():
    print("Scaricando dati consumi energetici di Rimini...")
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
    print(f"Elementi ricevuti: {len(elements)}")
    features = []
    for el in elements:
        tags = el.get('tags', {})
        power = tags.get('power', '')
        gen_source = tags.get('generator:source', '')
        if power == 'plant':
            tipo = 'centrale_elettrica'
        elif power == 'substation':
            tipo = 'cabina_elettrica'
        elif gen_source == 'solar':
            tipo = 'pannello_solare'
        elif gen_source == 'wind':
            tipo = 'turbina_eolica'
        elif tags.get('amenity') == 'charging_station':
            tipo = 'colonnina_ricarica'
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
            if coords[0] != coords[-1]:
                coords.append(coords[0])
            feature = {
                "type": "Feature",
                "properties": {"id": el.get('id'), "tipo": tipo, "name": tags.get('name', '')},
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
    download_energia()