"""
download_sanita.py — Strutture sanitarie di Rimini
Sostituisce download_ospedali.py
Output: data/processed/sanita_rimini.geojson
Tipi: ospedale, pronto_soccorso, clinica, farmacia, medico, dentista, ambulatorio, veterinario
"""
import requests, json, os
from collections import defaultdict

OUTPUT_DIR  = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'sanita_rimini.geojson')
OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"

QUERY = """
[out:json][timeout:90];
relation["name"="Rimini"]["admin_level"="8"]["boundary"="administrative"];
map_to_area -> .rimini;
(
  node["amenity"="hospital"](area.rimini);
  node["amenity"="clinic"](area.rimini);
  node["amenity"="pharmacy"](area.rimini);
  node["amenity"="doctors"](area.rimini);
  node["amenity"="dentist"](area.rimini);
  node["amenity"="veterinary"](area.rimini);
  node["amenity"="social_facility"](area.rimini);
  node["healthcare"="hospital"](area.rimini);
  node["healthcare"="clinic"](area.rimini);
  node["healthcare"="pharmacy"](area.rimini);
  node["healthcare"="doctor"](area.rimini);
  node["healthcare"="dentist"](area.rimini);
  node["emergency"="ambulance_station"](area.rimini);
  way["amenity"="hospital"](area.rimini);
  way["amenity"="clinic"](area.rimini);
  way["amenity"="pharmacy"](area.rimini);
  way["healthcare"="hospital"](area.rimini);
);
out center;
"""

def get_tipo(tags):
    amenity    = tags.get('amenity', '')
    healthcare = tags.get('healthcare', '')
    emergency  = tags.get('emergency', '')

    if amenity == 'hospital' or healthcare == 'hospital':
        return 'ospedale', 'Ospedale'
    elif emergency == 'ambulance_station':
        return 'pronto_soccorso', 'Pronto Soccorso / 118'
    elif amenity == 'clinic' or healthcare == 'clinic':
        return 'clinica', 'Clinica / Poliambulatorio'
    elif amenity == 'pharmacy' or healthcare == 'pharmacy':
        return 'farmacia', 'Farmacia'
    elif amenity == 'doctors' or healthcare == 'doctor':
        return 'medico', 'Medico di Base'
    elif amenity == 'dentist' or healthcare == 'dentist':
        return 'dentista', 'Dentista'
    elif amenity == 'veterinary':
        return 'veterinario', 'Veterinario'
    elif amenity == 'social_facility':
        return 'servizio_sociale', 'Servizio Sociale'
    return 'altro', 'Altro'

def get_coords(el):
    if el['type'] == 'node':
        return [el['lon'], el['lat']]
    elif el['type'] == 'way' and 'center' in el:
        return [el['center']['lon'], el['center']['lat']]
    return None

def download_sanita():
    print("Scaricando strutture sanitarie di Rimini...")
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
        if not coords:
            continue
        tipo_id, tipo_label = get_tipo(tags)
        key = name if name else f"_{round(coords[0],4)}_{round(coords[1],4)}"

        feat = {
            "type": "Feature",
            "properties": {
                "nome":       name or tipo_label,
                "tipo":       tipo_id,
                "tipo_label": tipo_label,
                "telefono":   tags.get('phone', tags.get('contact:phone', '')),
                "website":    tags.get('website', tags.get('contact:website', '')),
                "orari":      tags.get('opening_hours', ''),
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
    print(f"Strutture uniche: {len(features)}")
    for t, n in sorted(tipi.items(), key=lambda x: -x[1]):
        print(f"   {t}: {n}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump({"type":"FeatureCollection","features":features}, f, ensure_ascii=False, indent=2)
    print(f" Salvato: {OUTPUT_FILE}")

if __name__ == "__main__":
    download_sanita()