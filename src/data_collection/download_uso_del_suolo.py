"""
Script per scaricare l'uso del suolo di Rimini
Fonte: OpenStreetMap tramite Overpass API
Output: data/processed/uso_suolo_rimini.geojson
"""

import requests
import json
import os

# ============================================================
# CONFIGURAZIONE
# ============================================================
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'uso_suolo_rimini.geojson')

OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"

QUERY = """
[out:json][timeout:90];
relation["name"="Rimini"]["admin_level"="8"]["boundary"="administrative"];
map_to_area -> .rimini;
(
  way["landuse"](area.rimini);
  relation["landuse"](area.rimini);
);
out geom;
"""

# ============================================================
# COLORI PER TIPO DI USO DEL SUOLO
# ============================================================
COLORI_LANDUSE = {
    "residential":              "#f5e6a3",  # giallo chiaro — zone residenziali
    "commercial":               "#f5a623",  # arancione — zone commerciali
    "retail":                   "#e8604c",  # rosso chiaro — negozi
    "industrial":               "#9b9b9b",  # grigio — zone industriali
    "farmland":                 "#c8b87a",  # beige/marrone — terreni agricoli
    "meadow":                   "#a8d58a",  # verde medio — prati
    "grass":                    "#b8e6a0",  # verde chiaro — aree erbose
    "forest":                   "#3a7a3a",  # verde scuro — boschi
    "park":                     "#60c070",  # verde parco
    "garden":                   "#70d080",  # verde giardino
    "allotments":               "#b8d890",  # verde orti
    "orchard":                  "#d4e870",  # verde-giallo frutteti
    "cemetery":                 "#4a7a4a",  # verde scuro cimiteri
    "religious":                "#7ab8d8",  # azzurro — zone religiose
    "construction":             "#c8843c",  # marrone — cantieri
    "brownfield":               "#a06030",  # marrone scuro — aree dismesse
    "greenfield":               "#d0e8a0",  # verde pallido — aree verdi non sviluppate
    "military":                 "#8b4513",  # marrone militare
    "industrial":               "#808080",  # grigio industriale
    "depot":                    "#a0a0a0",  # grigio chiaro — depositi
    "greenhouse_horticulture":  "#d8f0a0",  # verde molto chiaro — serre
    "basin":                    "#4a90d9",  # blu — bacini idrici
    "reservoir":                "#5a9ae8",  # blu chiaro — serbatoi
    "railway":                  "#606060",  # grigio scuro — ferroviario
    "quarry":                   "#b0a090",  # grigio beige — cave
    "education":                "#7090e0",  # blu — istruzione
    "flowerbed":                "#f0a0c0",  # rosa — aiuole
    "plant_nursery":            "#90c870",  # verde vivai
    "recreation_ground":        "#80d880",  # verde ricreativo
    "other":                    "#d0d0d0",  # grigio chiaro — altro
}

def get_color(landuse_type):
    return COLORI_LANDUSE.get(landuse_type, COLORI_LANDUSE["other"])

def download_uso_suolo():
    print("Scaricando uso del suolo di Rimini...")

    response = requests.post(OVERPASS_URL, data=QUERY)

    if response.status_code != 200:
        print(f"Errore nella richiesta: {response.status_code}")
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
        if el['type'] == 'way' and 'geometry' in el:
            coords = [[pt['lon'], pt['lat']] for pt in el['geometry']]
            if coords[0] != coords[-1]:
                coords.append(coords[0])

            landuse = el.get('tags', {}).get('landuse', 'other')
            color = get_color(landuse)
            name = el.get('tags', {}).get('name', '')

            feature = {
                "type": "Feature",
                "properties": {
                    "id": el.get('id'),
                    "landuse": landuse,
                    "name": name,
                    "color": color,
                    "description": get_description(landuse)
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coords]
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
    print(f"   Numero di zone: {len(features)}")

    # Riepilogo per tipo
    tipi = {}
    for f in features:
        t = f['properties']['landuse']
        tipi[t] = tipi.get(t, 0) + 1
    print("\n Riepilogo per tipo:")
    for tipo, count in sorted(tipi.items(), key=lambda x: -x[1]):
        colore = get_color(tipo)
        print(f"   {tipo}: {count} → {colore}")

def get_description(landuse_type):
    DESCRIZIONI = {
        "residential":             "Zona residenziale",
        "commercial":              "Zona commerciale",
        "retail":                  "Zona negozi/vendita",
        "industrial":              "Zona industriale",
        "farmland":                "Terreno agricolo",
        "meadow":                  "Prato/pascolo",
        "grass":                   "Area erbosa",
        "forest":                  "Bosco/foresta",
        "park":                    "Parco pubblico",
        "garden":                  "Giardino",
        "allotments":              "Orti urbani",
        "orchard":                 "Frutteto",
        "cemetery":                "Cimitero",
        "religious":               "Area religiosa",
        "construction":            "Cantiere",
        "brownfield":              "Area dismessa",
        "greenfield":              "Area verde non sviluppata",
        "military":                "Zona militare",
        "depot":                   "Deposito",
        "greenhouse_horticulture": "Serra orticola",
        "basin":                   "Bacino idrico",
        "reservoir":               "Serbatoio",
        "railway":                 "Area ferroviaria",
        "quarry":                  "Cava",
        "education":               "Area scolastica",
        "flowerbed":               "Aiuola",
        "plant_nursery":           "Vivaio",
        "recreation_ground":       "Area ricreativa",
    }
    return DESCRIZIONI.get(landuse_type, "Altro")

if __name__ == "__main__":
    download_uso_suolo()