"""
download_monumenti.py — Monumenti e attrazioni culturali di Rimini
Con deduplicazione e categorie per sub-flag
Output: data/processed/monumenti_rimini.geojson
"""
import requests, json, os
from collections import defaultdict

OUTPUT_DIR  = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'monumenti_rimini.geojson')
OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"

QUERY = """
[out:json][timeout:90];
relation["name"="Rimini"]["admin_level"="8"]["boundary"="administrative"];
map_to_area -> .rimini;
(
  node["tourism"="attraction"](area.rimini);
  node["tourism"="museum"](area.rimini);
  node["tourism"="artwork"](area.rimini);
  node["tourism"="viewpoint"](area.rimini);
  node["historic"="monument"](area.rimini);
  node["historic"="memorial"](area.rimini);
  node["historic"="ruins"](area.rimini);
  node["historic"="castle"](area.rimini);
  node["historic"="archaeological_site"](area.rimini);
  node["historic"="city_gate"](area.rimini);
  node["amenity"="theatre"](area.rimini);
  node["amenity"="library"](area.rimini);
  way["tourism"="attraction"](area.rimini);
  way["tourism"="museum"](area.rimini);
  way["historic"="monument"](area.rimini);
  way["historic"="castle"](area.rimini);
  way["historic"="ruins"](area.rimini);
  way["historic"="archaeological_site"](area.rimini);
  way["amenity"="theatre"](area.rimini);
);
out center;
"""

def get_tipo(tags):
    tourism  = tags.get('tourism', '')
    historic = tags.get('historic', '')
    amenity  = tags.get('amenity', '')
    if tourism == 'museum':
        return 'museo', 'Museo'
    elif tourism == 'artwork':
        return 'opera_arte', "Opera d'arte"
    elif tourism == 'viewpoint':
        return 'panoramico', 'Punto panoramico'
    elif historic == 'castle':
        return 'castello', 'Castello / Rocca'
    elif historic in ('ruins', 'archaeological_site'):
        return 'sito_archeologico', 'Sito archeologico'
    elif historic in ('monument', 'memorial'):
        return 'monumento', 'Monumento / Memoriale'
    elif historic == 'city_gate':
        return 'porta_citta', 'Porta della città'
    elif amenity == 'theatre':
        return 'teatro', 'Teatro'
    elif amenity == 'library':
        return 'biblioteca', 'Biblioteca'
    elif tourism == 'attraction':
        return 'attrazione', 'Attrazione turistica'
    return 'altro', 'Altro'

def get_coords(el):
    if el['type'] == 'node':
        return [el['lon'], el['lat']]
    elif el['type'] == 'way' and 'center' in el:
        return [el['center']['lon'], el['center']['lat']]
    return None

def download_monumenti():
    print("Scaricando monumenti e attrazioni di Rimini...")
    resp = requests.post(OVERPASS_URL, data=QUERY)
    if resp.status_code != 200 or not resp.text.strip():
        print(f"Errore: {resp.status_code}"); return
    elements = resp.json().get('elements', [])
    print(f"Elementi OSM: {len(elements)}")

    by_key = {}
    for el in elements:
        tags   = el.get('tags', {})
        name   = tags.get('name', '').strip()
        coords = get_coords(el)
        if not coords or not name:
            continue
        tipo_id, tipo_label = get_tipo(tags)
        key = name

        feat = {
            "type": "Feature",
            "properties": {
                "nome":       name,
                "tipo":       tipo_id,
                "tipo_label": tipo_label,
                "descrizione": tags.get('description', ''),
                "wikipedia":  tags.get('wikipedia', ''),
                "website":    tags.get('website', ''),
                "fonte":      "OpenStreetMap 2026"
            },
            "geometry": {"type": "Point", "coordinates": coords}
        }
        if key not in by_key or el['type'] == 'way':
            by_key[key] = feat

    features = list(by_key.values())
    tipi = defaultdict(int)
    for f in features:
        tipi[f['properties']['tipo_label']] += 1
    print(f"Monumenti unici: {len(features)}")
    for t, n in sorted(tipi.items(), key=lambda x: -x[1]):
        print(f"   {t}: {n}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump({"type":"FeatureCollection","features":features}, f, ensure_ascii=False, indent=2)
    print(f" Salvato: {OUTPUT_FILE}")

if __name__ == "__main__":
    download_monumenti()