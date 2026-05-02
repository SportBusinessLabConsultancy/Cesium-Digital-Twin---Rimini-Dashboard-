"""
Script per scaricare gli uffici pubblici di Rimini
"""

import requests
import json
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'uffici_rimini.geojson')
OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"

QUERY = """
[out:json][timeout:90];
relation["name"="Rimini"]["admin_level"="8"]["boundary"="administrative"];
map_to_area -> .rimini;
(
  node["amenity"="townhall"](area.rimini);
  node["amenity"="post_office"](area.rimini);
  node["amenity"="police"](area.rimini);
  node["amenity"="fire_station"](area.rimini);
  node["amenity"="courthouse"](area.rimini);
  node["office"="government"](area.rimini);
  node["office"="tax"](area.rimini);
  way["amenity"="townhall"](area.rimini);
  way["amenity"="police"](area.rimini);
  way["amenity"="fire_station"](area.rimini);
);
out geom;
"""

def download_uffici():
    print("Scaricando uffici pubblici di Rimini...")
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
        office = tags.get('office', '')
        if amenity == 'townhall':
            tipo = 'municipio'
        elif amenity == 'post_office':
            tipo = 'ufficio_postale'
        elif amenity == 'police':
            tipo = 'polizia'
        elif amenity == 'fire_station':
            tipo = 'vigili_del_fuoco'
        elif amenity == 'courthouse':
            tipo = 'tribunale'
        elif office in ['government', 'tax']:
            tipo = 'ufficio_governativo'
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
    print(f"   Numero di uffici pubblici: {len(features)}")
    tipi = {}
    for f in features:
        t = f['properties']['tipo']
        tipi[t] = tipi.get(t, 0) + 1
    print("\n Riepilogo per tipo:")
    for tipo, count in sorted(tipi.items(), key=lambda x: -x[1]):
        print(f"   {tipo}: {count}")

if __name__ == "__main__":
    download_uffici()