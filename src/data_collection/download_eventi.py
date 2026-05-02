"""
download_eventi.py — Luoghi eventi di Rimini
Fix: un solo punto per venue (deduplica per nome + centroide per ways)
"""
import requests, json, os
from collections import defaultdict

OUTPUT_DIR  = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'eventi_rimini.geojson')
OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"

# out center; → restituisce il centroide delle ways, non i nodi perimetrali
QUERY = """
[out:json][timeout:90];
relation["name"="Rimini"]["admin_level"="8"]["boundary"="administrative"];
map_to_area -> .rimini;
(
  node["amenity"="theatre"](area.rimini);
  node["amenity"="cinema"](area.rimini);
  node["amenity"="conference_centre"](area.rimini);
  node["leisure"="stadium"](area.rimini);
  node["leisure"="arena"](area.rimini);
  node["leisure"="sports_hall"](area.rimini);
  node["amenity"="arts_centre"](area.rimini);
  way["amenity"="theatre"](area.rimini);
  way["amenity"="cinema"](area.rimini);
  way["amenity"="conference_centre"](area.rimini);
  way["leisure"="stadium"](area.rimini);
  way["leisure"="arena"](area.rimini);
  way["amenity"="arts_centre"](area.rimini);
);
out center;
"""

TIPO_MAP = {
    'theatre':           'teatro',
    'cinema':            'cinema',
    'conference_centre': 'centro_congressi',
    'stadium':           'stadio',
    'arena':             'arena',
    'sports_hall':       'palazzetto',
    'arts_centre':       'centro_arte',
}

def get_coords(el):
    if el['type'] == 'node':
        return [el['lon'], el['lat']]
    elif el['type'] == 'way' and 'center' in el:
        return [el['center']['lon'], el['center']['lat']]
    return None

def download_eventi():
    print("Scaricando luoghi eventi di Rimini...")
    resp = requests.post(OVERPASS_URL, data=QUERY)
    if resp.status_code != 200 or not resp.text.strip():
        print(f"Errore: {resp.status_code}"); return
    elements = resp.json().get('elements', [])
    print(f"Elementi OSM: {len(elements)}")

    # Deduplica per nome: tieni il centroide più accurato (way > node)
    by_name = {}  # name → feature
    for el in elements:
        tags  = el.get('tags', {})
        name  = tags.get('name', '').strip()
        if not name:
            continue
        coords = get_coords(el)
        if not coords:
            continue
        amenity = tags.get('amenity', '')
        leisure = tags.get('leisure', '')
        tipo = TIPO_MAP.get(amenity) or TIPO_MAP.get(leisure) or 'altro'
        feat = {
            "type": "Feature",
            "properties": {
                "nome": name, "tipo": tipo,
                "capacity": tags.get('capacity', ''),
                "website":  tags.get('website', tags.get('contact:website', '')),
                "fonte": "OpenStreetMap 2026"
            },
            "geometry": {"type": "Point", "coordinates": coords}
        }
        # Preferisce la way (center) sul node
        if name not in by_name or el['type'] == 'way':
            by_name[name] = feat

    features = list(by_name.values())
    tipi = defaultdict(int)
    for f in features:
        tipi[f['properties']['tipo']] += 1
    print(f"Venue unici: {len(features)}")
    for t, n in sorted(tipi.items(), key=lambda x: -x[1]):
        print(f"   {t}: {n}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump({"type":"FeatureCollection","features":features}, f, ensure_ascii=False, indent=2)
    print(f" Salvato: {OUTPUT_FILE}")

if __name__ == "__main__":
    download_eventi()