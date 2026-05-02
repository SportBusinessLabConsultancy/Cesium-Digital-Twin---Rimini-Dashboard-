"""
Script per scaricare la rete stradale di Rimini
"""

import requests
import json
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'strade_rimini.geojson')

OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"

QUERY = """
[out:json][timeout:90];
relation["name"="Rimini"]["admin_level"="8"]["boundary"="administrative"];
map_to_area -> .rimini;
(
  way["highway"~"motorway|trunk|primary|secondary|tertiary|residential|service|unclassified"](area.rimini);
);
out geom;
"""

COLORI_HIGHWAY = {
    "motorway": "#e892a2",
    "trunk": "#f9b29c",
    "primary": "#fcd6a4",
    "secondary": "#f7fabf",
    "tertiary": "#ffffff",
    "residential": "#cccccc",
    "service": "#aaaaaa",
    "unclassified": "#bbbbbb"
}

def download_strade():
    print("Scaricando rete stradale di Rimini...")

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
        if el['type'] == 'way' and 'geometry' in el:
            coords = [[pt['lon'], pt['lat']] for pt in el['geometry']]
            highway = el.get('tags', {}).get('highway', 'unclassified')

            feature = {
                "type": "Feature",
                "properties": {
                    "id": el.get('id'),
                    "highway": highway,
                    "name": el.get('tags', {}).get('name', ''),
                    "maxspeed": el.get('tags', {}).get('maxspeed', ''),
                    "oneway": el.get('tags', {}).get('oneway', ''),
                    "color": COLORI_HIGHWAY.get(highway, "#cccccc")
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
    print(f"   Numero di strade: {len(features)}")

    # Riepilogo per tipo
    tipi = {}
    for f in features:
        t = f['properties']['highway']
        tipi[t] = tipi.get(t, 0) + 1
    print("\n Riepilogo per tipo:")
    for tipo, count in sorted(tipi.items(), key=lambda x: -x[1]):
        print(f"   {tipo}: {count}")

if __name__ == "__main__":
    download_strade()