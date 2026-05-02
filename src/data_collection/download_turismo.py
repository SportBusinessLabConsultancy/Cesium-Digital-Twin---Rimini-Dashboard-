"""
Script per scaricare strutture ricettive e turismo di Rimini
"""

import requests
import json
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'turismo_rimini.geojson')
OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"

QUERY = """
[out:json][timeout:90];
relation["name"="Rimini"]["admin_level"="8"]["boundary"="administrative"];
map_to_area -> .rimini;
(
  node["tourism"="hotel"](area.rimini);
  node["tourism"="hostel"](area.rimini);
  node["tourism"="guest_house"](area.rimini);
  node["tourism"="motel"](area.rimini);
  node["tourism"="camp_site"](area.rimini);
  node["tourism"="attraction"](area.rimini);
  node["tourism"="museum"](area.rimini);
  node["tourism"="viewpoint"](area.rimini);
  way["tourism"="hotel"](area.rimini);
  way["tourism"="hostel"](area.rimini);
  way["tourism"="guest_house"](area.rimini);
);
out geom;
"""

def download_turismo():
    print("Scaricando strutture turistiche di Rimini...")
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
        tourism = tags.get('tourism', '')
        if tourism == 'hotel':
            tipo = 'hotel'
        elif tourism == 'hostel':
            tipo = 'ostello'
        elif tourism == 'guest_house':
            tipo = 'bed_and_breakfast'
        elif tourism == 'motel':
            tipo = 'motel'
        elif tourism == 'camp_site':
            tipo = 'campeggio'
        elif tourism == 'attraction':
            tipo = 'attrazione'
        elif tourism == 'museum':
            tipo = 'museo'
        elif tourism == 'viewpoint':
            tipo = 'punto_panoramico'
        else:
            tipo = 'altro'
        if el['type'] == 'node':
            feature = {
                "type": "Feature",
                "properties": {
                    "id": el.get('id'),
                    "tipo": tipo,
                    "name": tags.get('name', ''),
                    "stars": tags.get('stars', ''),
                    "rooms": tags.get('rooms', ''),
                    "website": tags.get('website', ''),
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
                    "stars": tags.get('stars', ''),
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
    print(f"   Numero di strutture: {len(features)}")
    tipi = {}
    for f in features:
        t = f['properties']['tipo']
        tipi[t] = tipi.get(t, 0) + 1
    print("\n Riepilogo per tipo:")
    for tipo, count in sorted(tipi.items(), key=lambda x: -x[1]):
        print(f"   {tipo}: {count}")

if __name__ == "__main__":
    download_turismo()