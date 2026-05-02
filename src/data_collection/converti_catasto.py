"""
Script per convertire i file GML catastali in GeoJSON
Fonte: Agenzia delle Entrate — Download massivo
Input:  data/raw/H294_RIMINI_ple.gml
Output: data/processed/catasto_rimini.geojson

Geometria: Polygon — permette il click su tutta l'area in MapLibre.
"""

import json
import os
import math
from xml.etree import ElementTree as ET

# ============================================================
# CONFIGURAZIONE
# ============================================================
INPUT_MAP   = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw', 'H294_RIMINI_ple.gml')
OUTPUT_DIR  = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'catasto_rimini.geojson')


def parse_poslist(text):
    """
    Converte stringa posList GML in coordinate GeoJSON.
    Formato EPSG:6706: coppie lat lon → invertiamo in lon lat per GeoJSON.
    """
    vals = text.strip().split()
    coords = []
    for i in range(0, len(vals) - 1, 2):
        try:
            lat = float(vals[i])
            lon = float(vals[i + 1])
            coords.append([lon, lat])
        except ValueError:
            continue
    return coords


def calcola_area_mq(ring):
    """
    Calcola l'area approssimativa in m² usando la formula di Shoelace
    con conversione gradi → metri (approssimazione locale).
    """
    if len(ring) < 3:
        return 0.0
    n = len(ring)
    area_gradi = 0.0
    for i in range(n):
        j = (i + 1) % n
        area_gradi += ring[i][0] * ring[j][1]
        area_gradi -= ring[j][0] * ring[i][1]
    area_gradi = abs(area_gradi) / 2.0
    lat_centro = sum(c[1] for c in ring) / n
    m_per_deg_lat = 111320.0
    m_per_deg_lon = 111320.0 * math.cos(math.radians(lat_centro))
    return round(area_gradi * m_per_deg_lat * m_per_deg_lon, 1)


def calcola_centroide(ring):
    """Calcola il centroide approssimativo di un anello di coordinate."""
    if not ring:
        return None
    lon = sum(c[0] for c in ring) / len(ring)
    lat = sum(c[1] for c in ring) / len(ring)
    return [round(lon, 6), round(lat, 6)]


def converti_catasto():
    print("Convertendo file GML catastale in GeoJSON...")

    if not os.path.exists(INPUT_MAP):
        print(f"❌ File non trovato: {INPUT_MAP}")
        return

    tree = ET.parse(INPUT_MAP)
    root = tree.getroot()

    features = []
    n_parcelle = 0
    n_zone     = 0

    for elem in root.iter():
        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag

        if tag not in ['CadastralZoning', 'CadastralParcel']:
            continue

        gml_id = elem.get('{http://www.opengis.net/gml/3.2}id', '')

        # Attributi dal GML (namespace INSPIRE)
        ns            = '{urn:x-inspire:specification:gmlas:CadastralParcels:3.0}'
        label         = elem.findtext(f'{ns}label') or ''
        area_value    = elem.findtext(f'{ns}areaValue') or ''
        rif_catastale = elem.findtext(f'{ns}nationalCadastralReference') or ''

        # Raccolta anelli poligonali
        rings = []
        for poslist in elem.iter('{http://www.opengis.net/gml/3.2}posList'):
            if poslist.text:
                coords = parse_poslist(poslist.text)
                if len(coords) >= 3:
                    if coords[0] != coords[-1]:
                        coords.append(coords[0])
                    rings.append(coords)

        if not rings:
            continue

        # Anello esterno = il più lungo; gli altri sono buchi (cortili, ecc.)
        rings.sort(key=lambda r: len(r), reverse=True)
        exterior = rings[0]
        holes    = rings[1:]

        area_mq   = calcola_area_mq(exterior)
        centroide = calcola_centroide(exterior)
        tipo_lbl  = 'Particella catastale' if tag == 'CadastralParcel' else 'Zona catastale'

        if tag == 'CadastralParcel':
            n_parcelle += 1
        else:
            n_zone += 1

        feature = {
            "type": "Feature",
            "properties": {
                "id":                gml_id,
                "tipo":              tipo_lbl,
                "label":             label,
                "riferimento":       rif_catastale,
                "area_mq":           area_mq,
                "area_ufficiale_mq": float(area_value) if area_value else None,
                "centroide_lon":     centroide[0] if centroide else None,
                "centroide_lat":     centroide[1] if centroide else None,
                "fonte":             "Agenzia delle Entrate - Download massivo 2026",
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [exterior] + holes
            }
        }
        features.append(feature)

    print(f"   Particelle trovate: {n_parcelle}")
    print(f"   Zone catastali:     {n_zone}")
    print(f"   Totale features:    {len(features)}")

    if not features:
        print(" Nessuna feature trovata nel GML.")
        return

    geojson = {"type": "FeatureCollection", "features": features}

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)

    print(f" Salvato: {OUTPUT_FILE}")
    print("   ➡  Ora esegui converti_geojson_pmtiles.py per aggiornare il PMTiles.")


if __name__ == "__main__":
    converti_catasto()