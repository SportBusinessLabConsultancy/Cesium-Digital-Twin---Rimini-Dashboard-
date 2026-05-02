"""
Script per scaricare i flussi di traffico di Rimini
"""

import requests
import json
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'traffico_rimini.geojson')

OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"

QUERY = """
[out:json][timeout:90];
relation["name"="Rimini"]["admin_level"="8"]["boundary"="administrative"];
map_to_area -> .rimini;
(
  way["highway"~"motorway|trunk|primary|secondary"]["maxspeed"](area.rimini);
  way["highway"~"motorway|trunk|primary|secondary"]["lanes"](area.rimini);
  way["highway"~"motorway|trunk|primary|secondary"]["oneway"="yes"](area.rimini);
);
out geom;
"""

def get_color_by_speed(maxspeed):
    try:
        speed = int(maxspeed)
        if speed <= 30:
            return "#00cc44"
        elif speed <= 50:
            return "#ffcc00"
        elif speed <= 70:
            return "#ff8800"
        else:
            return "#ff2200"
    except:
        return "#aaaaaa"

def download_traffico():
    print("Scaricando flussi di traffico di Rimini...")

    response = requests.post(OVERPASS_URL, data=QUERY)

    if response.status_code != 200:
        print(f"Errore nella richiesta: {response.status_code}")
        return

    if not response.text.strip():
        print("Risposta vuota dal server. Riprova tra qualche secondo.")
        return

    try:
        data = response.json()
    except Exception as e:
        print(f"Errore nel parsing JSON: {e}")
        print(f"Risposta ricevuta: {response.text[:200]}")
        return

    elements = data.get('elements', [])

    if not elements:
        print("Nessun dato ricevuto.")
        return
    print(f"Elementi ricevuti: {len(elements)}")

    features = []
    seen_ids = set()
    for el in elements:
        if el['type'] == 'way' and 'geometry' in el and el['id'] not in seen_ids:
            seen_ids.add(el['id'])
            coords = [[pt['lon'], pt['lat']] for pt in el['geometry']]
            tags = el.get('tags', {})
            maxspeed = tags.get('maxspeed', '')

            feature = {
                "type": "Feature",
                "properties": {
                    "id": el.get('id'),
                    "name": tags.get('name', ''),
                    "highway": tags.get('highway', ''),
                    "maxspeed": maxspeed,
                    "lanes": tags.get('lanes', ''),
                    "oneway": tags.get('oneway', ''),
                    "color": get_color_by_speed(maxspeed)
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
    print(f"   Numero di tratti: {len(features)}")

    # Riepilogo per velocità
    velocita = {}
    for f in features:
        v = f['properties']['maxspeed'] or 'non specificata'
        velocita[v] = velocita.get(v, 0) + 1
    print("\n Riepilogo per velocità massima:")
    for v, count in sorted(velocita.items(), key=lambda x: -x[1])[:10]:
        print(f"   {v} km/h: {count}")

if __name__ == "__main__":
    download_traffico()