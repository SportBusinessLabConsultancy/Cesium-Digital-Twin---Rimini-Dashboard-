"""
download_scuole.py — Scuole di Rimini
Fix: un solo punto per istituto (deduplica per nome + out center per ways)
"""
import requests, json, os
from collections import defaultdict

OUTPUT_DIR  = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'scuole_rimini.geojson')
OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"

QUERY = """
[out:json][timeout:90];
relation["name"="Rimini"]["admin_level"="8"]["boundary"="administrative"];
map_to_area -> .rimini;
(
  node["amenity"="school"](area.rimini);
  node["amenity"="kindergarten"](area.rimini);
  node["amenity"="university"](area.rimini);
  node["amenity"="college"](area.rimini);
  way["amenity"="school"](area.rimini);
  way["amenity"="kindergarten"](area.rimini);
  way["amenity"="university"](area.rimini);
  way["amenity"="college"](area.rimini);
);
out center;
"""

TIPO_MAP = {
    'school':       ('scuola',             'Scuola'),
    'kindergarten': ('asilo',              'Asilo/Nido'),
    'university':   ('universita',         'Università'),
    'college':      ('istituto_superiore', 'Istituto Superiore'),
}

def get_coords(el):
    if el['type'] == 'node':
        return [el['lon'], el['lat']]
    elif el['type'] == 'way' and 'center' in el:
        return [el['center']['lon'], el['center']['lat']]
    return None

def download_scuole():
    print("Scaricando scuole di Rimini...")
    resp = requests.post(OVERPASS_URL, data=QUERY)
    if resp.status_code != 200 or not resp.text.strip():
        print(f"Errore: {resp.status_code}"); return
    elements = resp.json().get('elements', [])
    print(f"Elementi OSM: {len(elements)}")

    by_name = {}
    unnamed_count = 0
    for el in elements:
        tags   = el.get('tags', {})
        name   = tags.get('name', '').strip()
        coords = get_coords(el)
        if not coords:
            continue
        amenity = tags.get('amenity', '')
        tipo_id, tipo_label = TIPO_MAP.get(amenity, ('altro', 'Altro'))

        if not name:
            # istituti senza nome: usa coordinate come chiave per evitare doppioni
            key = f"unnamed_{round(coords[0],4)}_{round(coords[1],4)}"
            unnamed_count += 1
        else:
            key = name

        feat = {
            "type": "Feature",
            "properties": {
                "nome":     name or "Istituto senza nome",
                "tipo":     tipo_id,
                "tipo_label": tipo_label,
                "operator": tags.get('operator', ''),
                "website":  tags.get('website', ''),
                "fonte":    "OpenStreetMap 2026"
            },
            "geometry": {"type": "Point", "coordinates": coords}
        }
        if key not in by_name or el['type'] == 'way':
            by_name[key] = feat

    features = list(by_name.values())
    tipi = defaultdict(int)
    for f in features:
        tipi[f['properties']['tipo_label']] += 1
    print(f"Istituti unici: {len(features)}")
    for t, n in sorted(tipi.items(), key=lambda x: -x[1]):
        print(f"   {t}: {n}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump({"type":"FeatureCollection","features":features}, f, ensure_ascii=False, indent=2)
    print(f" Salvato: {OUTPUT_FILE}")

if __name__ == "__main__":
    download_scuole()