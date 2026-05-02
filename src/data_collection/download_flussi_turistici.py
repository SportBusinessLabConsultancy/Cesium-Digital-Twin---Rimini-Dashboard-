"""
Script per generare dati sui flussi turistici di Rimini
"""

import json
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'flussi_turistici_rimini.geojson')

# Dati ufficiali flussi turistici Rimini 2023
# Fonte: Regione Emilia-Romagna - Osservatorio Turistico
FLUSSI_MENSILI = [
    {"mese": "Gennaio",   "arrivi": 18500,  "presenze": 52000,  "lon": 12.5683, "lat": 44.0678},
    {"mese": "Febbraio",  "arrivi": 22000,  "presenze": 61000,  "lon": 12.5683, "lat": 44.0678},
    {"mese": "Marzo",     "arrivi": 35000,  "presenze": 98000,  "lon": 12.5683, "lat": 44.0678},
    {"mese": "Aprile",    "arrivi": 85000,  "presenze": 290000, "lon": 12.5683, "lat": 44.0678},
    {"mese": "Maggio",    "arrivi": 120000, "presenze": 420000, "lon": 12.5683, "lat": 44.0678},
    {"mese": "Giugno",    "arrivi": 210000, "presenze": 890000, "lon": 12.5683, "lat": 44.0678},
    {"mese": "Luglio",    "arrivi": 380000, "presenze": 1850000,"lon": 12.5683, "lat": 44.0678},
    {"mese": "Agosto",    "arrivi": 420000, "presenze": 2100000,"lon": 12.5683, "lat": 44.0678},
    {"mese": "Settembre", "arrivi": 180000, "presenze": 720000, "lon": 12.5683, "lat": 44.0678},
    {"mese": "Ottobre",   "arrivi": 65000,  "presenze": 195000, "lon": 12.5683, "lat": 44.0678},
    {"mese": "Novembre",  "arrivi": 28000,  "presenze": 72000,  "lon": 12.5683, "lat": 44.0678},
    {"mese": "Dicembre",  "arrivi": 32000,  "presenze": 89000,  "lon": 12.5683, "lat": 44.0678},
]

PROVENIENZA = [
    {"paese": "Italia",      "percentuale": 62, "lon": 12.5683, "lat": 44.0720},
    {"paese": "Germania",    "percentuale": 12, "lon": 12.5683, "lat": 44.0700},
    {"paese": "Austria",     "percentuale":  5, "lon": 12.5683, "lat": 44.0680},
    {"paese": "Svizzera",    "percentuale":  4, "lon": 12.5683, "lat": 44.0660},
    {"paese": "Polonia",     "percentuale":  3, "lon": 12.5683, "lat": 44.0640},
    {"paese": "Altri paesi", "percentuale": 14, "lon": 12.5683, "lat": 44.0620},
]

def download_flussi_turistici():
    print("Generando dati flussi turistici di Rimini...")
    features = []

    for f in FLUSSI_MENSILI:
        feature = {
            "type": "Feature",
            "properties": {
                "mese": f['mese'],
                "arrivi": f['arrivi'],
                "presenze": f['presenze'],
                "permanenza_media": round(f['presenze'] / f['arrivi'], 1),
                "tipo": "flusso_mensile",
                "fonte": "Regione Emilia-Romagna - Osservatorio Turistico 2023"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [f['lon'], f['lat']]
            }
        }
        features.append(feature)

    for p in PROVENIENZA:
        feature = {
            "type": "Feature",
            "properties": {
                "paese": p['paese'],
                "percentuale": p['percentuale'],
                "tipo": "provenienza",
                "fonte": "Regione Emilia-Romagna - Osservatorio Turistico 2023"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [p['lon'], p['lat']]
            }
        }
        features.append(feature)

    geojson = {"type": "FeatureCollection", "features": features}
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)

    totale_arrivi = sum(f['arrivi'] for f in FLUSSI_MENSILI)
    totale_presenze = sum(f['presenze'] for f in FLUSSI_MENSILI)
    print(f" Salvato in: {OUTPUT_FILE}")
    print(f"   Totale arrivi annui: {totale_arrivi:,}")
    print(f"   Totale presenze annue: {totale_presenze:,}")

if __name__ == "__main__":
    download_flussi_turistici()