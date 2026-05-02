"""
Script per scaricare l'arredo urbano di Rimini
"""

import requests
import json
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'arredo_urbano_rimini.geojson')

OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"

QUERY = """
[out:json][timeout:90];
relation["name"="Rimini"]["admin_level"="8"]["boundary"="administrative"];
map_to_area -> .rimini;
(
  node["amenity"="bench"](area.rimini);
  node["amenity"="waste_basket"](area.rimini);
  node["amenity"="drinking_water"](area.rimini);
  node["amenity"="fountain"](area.rimini);
  node["historic"="monument"](area.rimini);
  node["tourism"="artwork"](area.rimini);
  node["amenity"="bicycle_parking"](area.rimini);
);
out geom;
"""

def download_arredo_urbano():
    print("Scaricando arredo urbano di Rimini...")

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
        if el['type'] == 'node':
            tags = el.get('tags', {})
            # Determina il tipo di arredo
            if tags.get('amenity') == 'bench':
                tipo = 'panchina'
            elif tags.get('amenity') == 'waste_basket':
                tipo = 'cestino'
            elif tags.get('amenity') == 'drinking_water':
                tipo = 'fontanella'
            elif tags.get('amenity') == 'fountain':
                tipo = 'fontana'
            elif tags.get('historic') == 'monument':
                tipo = 'monumento'
            elif tags.get('tourism') == 'artwork':
                tipo = 'opera_arte'
            elif tags.get('amenity') == 'bicycle_parking':
                tipo = 'rastrelliera_bici'
            else:
                tipo = 'altro'

            feature = {
                "type": "Feature",
                "properties": {
                    "id": el.get('id'),
                    "tipo": tipo,
                    "name": tags.get('name', ''),
                    "material": tags.get('material', ''),
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [el['lon'], el['lat']]
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
    print(f"   Numero di elementi arredo urbano: {len(features)}")

    # Riepilogo per tipo
    tipi = {}
    for f in features:
        t = f['properties']['tipo']
        tipi[t] = tipi.get(t, 0) + 1
    print("\n Riepilogo per tipo:")
    for tipo, count in sorted(tipi.items(), key=lambda x: -x[1]):
        print(f"   {tipo}: {count}")

if __name__ == "__main__":
    download_arredo_urbano()