"""
Script per scaricare le Zone Toponomastiche di Rimini
Fonte: Comune di Rimini — Ufficio SIT (ArcGIS Open Data)
URL:   https://data-sit-rimini.opendata.arcgis.com/datasets/fe105a71004f4cbca3b56def39bdaadb_0
Output: data/processed/zone_toponomastiche_rimini.geojson

Le zone toponomastiche sono le suddivisioni ufficiali del territorio
usate dal Comune — più dettagliate dei quartieri OSM.
Queste corrispondono ai nomi che vedi nei dati SIT (es. "Marecchiese").
"""

import requests
import json
import os

OUTPUT_DIR  = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'zone_toponomastiche_rimini.geojson')

# URL GeoJSON diretto dall'ArcGIS Open Data del SIT Rimini
SIT_URL = (
    "https://data-sit-rimini.opendata.arcgis.com/api/download/v1/items/"
    "fe105a71004f4cbca3b56def39bdaadb/geojson?layers=0"
)
# URL alternativo (formato GeoJSON diretto)
SIT_URL_ALT = (
    "https://opendata.arcgis.com/datasets/fe105a71004f4cbca3b56def39bdaadb_0.geojson"
)

def download_zone_toponomastiche():
    print("Scaricando Zone Toponomastiche dal SIT Rimini...")

    geojson = None
    for url in [SIT_URL, SIT_URL_ALT]:
        try:
            print(f"  Provo: {url[:60]}...")
            resp = requests.get(url, timeout=60)
            if resp.status_code == 200:
                geojson = resp.json()
                if geojson.get('features'):
                    print(f"   OK: {len(geojson['features'])} zone trovate")
                    break
        except Exception as e:
            print(f"   {e}")

    if not geojson or not geojson.get('features'):
        print("⚠ Download fallito — generazione dati di fallback")
        geojson = genera_fallback()

    # Normalizza i nomi dei campi
    # Il SIT usa vari nomi per il campo nome: 'NOME', 'Nome', 'ZONATOPO', ecc.
    for feat in geojson.get('features', []):
        props = feat.get('properties', {})
        # Cerca il nome della zona in vari campi possibili
        nome = (props.get('NOME') or props.get('Nome') or props.get('nome') or
                props.get('ZONATOPO') or props.get('ZONA') or props.get('DESCRIZIONE') or '')
        props['nome_zona'] = nome.strip().title() if nome else 'Zona sconosciuta'

    # Stampa riepilogo nomi trovati
    nomi = sorted(set(
        f['properties']['nome_zona']
        for f in geojson['features']
        if f['properties']['nome_zona'] != 'Zona sconosciuta'
    ))
    print(f"\n Zone trovate ({len(nomi)}):")
    for n in nomi:
        print(f"   - {n}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    print(f"\n Salvato: {OUTPUT_FILE}")


def genera_fallback():
    """
    Zone toponomastiche principali di Rimini come fallback.
    Basate sui dati SIT Rimini — nomi ufficiali del Comune.
    Geometrie semplificate (centroidi) — sostituire con poligoni reali.
    """
    zone_ufficiali = [
        # (nome_ufficiale, lon, lat)
        ("Rimini Centro Storico",    12.5480, 44.0590),
        ("Marina Centro",            12.5700, 44.0650),
        ("Marecchiese",              12.4870, 44.0080),
        ("San Giuliano",             12.5620, 44.0620),
        ("Viserba",                  12.5380, 44.0890),
        ("Viserbella",               12.5100, 44.1010),
        ("Torre Pedrera",            12.5050, 44.1140),
        ("Miramare",                 12.5520, 44.0390),
        ("Rivabella",                12.5430, 44.0520),
        ("Bellariva",                12.5600, 44.0440),
        ("Marebello",                12.5580, 44.0360),
        ("Rivazzurra",               12.5560, 44.0290),
        ("Corpolò",                  12.5100, 44.0490),
        ("Vergiano",                 12.5030, 44.0830),
        ("Sant'Andrea in Besanigo",  12.5800, 44.0200),
        ("Padulli",                  12.5150, 44.0570),
        ("San Martino dei Mulini",   12.5000, 44.0680),
        ("Gaiofana",                 12.5250, 44.0230),
        ("Borgo San Giovanni",       12.5380, 44.0730),
        ("San Giovanni in Marignano",12.4500, 43.9500),  # fuori comune, solo esempio
    ]
    features = []
    for nome, lon, lat in zone_ufficiali:
        features.append({
            "type": "Feature",
            "properties": {
                "nome_zona": nome,
                "fonte": "Comune di Rimini SIT - fallback",
            },
            "geometry": {"type": "Point", "coordinates": [lon, lat]}
        })
    return {"type": "FeatureCollection", "features": features}


if __name__ == "__main__":
    download_zone_toponomastiche()