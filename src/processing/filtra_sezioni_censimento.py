"""
filtra_sezioni_censimento.py
────────────────────────────────────────────────────────────
Rimuove dal file sezioni_censimento_rimini.geojson tutti i punti
che cadono FUORI dai confini amministrativi del Comune di Rimini.

USO:
    python filtra_sezioni_censimento.py

Richiede:
    pip install shapely
    data/processed/confini_rimini.geojson   (già presente)
    data/processed/sezioni_censimento_rimini.geojson
"""

import json
import os
from shapely.geometry import shape, Point, MultiPolygon
from shapely.ops import unary_union

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
PROCESSED   = os.path.join(BASE_DIR, '..', '..', 'data', 'processed')

CONFINI_FILE  = os.path.join(PROCESSED, 'confini_rimini.geojson')
SEZIONI_FILE  = os.path.join(PROCESSED, 'sezioni_censimento_rimini.geojson')
OUTPUT_FILE   = os.path.join(PROCESSED, 'sezioni_censimento_rimini.geojson')  # sovrascrive

def carica_confini(path):
    """
    Carica i confini del comune.
    Gestisce sia Polygon/MultiPolygon che LineString (come in confini_rimini.geojson).
    """
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    shapes = []
    lines  = []
    for feat in data.get('features', []):
        geom = feat.get('geometry')
        if not geom:
            continue
        gtype = geom['type']
        if gtype in ('Polygon', 'MultiPolygon'):
            shapes.append(shape(geom))
        elif gtype in ('LineString', 'MultiLineString'):
            lines.append(shape(geom))

    # Se il file contiene LineString (caso confini_rimini.geojson)
    # prova a costruire poligoni chiusi con polygonize
    if lines and not shapes:
        print("   ℹ Confini in formato LineString — converto in Polygon...")
        from shapely.ops import polygonize
        merged = unary_union(lines)
        polys  = list(polygonize(merged))
        if polys:
            shapes = polys
            print(f"    Poligoni ottenuti: {len(shapes)}")
        else:
            # Fallback: convex hull dell'unione delle linee
            shapes = [merged.convex_hull]
            print("   ⚠ Poligonizzazione fallita — uso convex hull")

    if not shapes:
        raise ValueError(f"Nessuna geometria valida in {path}")
    return unary_union(shapes)

def get_point(feature):
    """Restituisce un Point dalla geometria della feature."""
    geom = feature.get('geometry', {})
    gtype = geom.get('type', '')
    coords = geom.get('coordinates', [])
    if gtype == 'Point':
        return Point(coords[0], coords[1])
    elif gtype in ('Polygon', 'MultiPolygon'):
        # usa il centroide
        return shape(geom).centroid
    elif gtype == 'LineString':
        mid = len(coords) // 2
        return Point(coords[mid][0], coords[mid][1])
    return None

def main():
    print("=" * 50)
    print("  Filtro sezioni per confini comunali")
    print("=" * 50)

    # Carica confini
    print(f"\n Confini: {os.path.basename(CONFINI_FILE)}")
    confine = carica_confini(CONFINI_FILE)
    bbox = confine.bounds
    print(f"   Bounding box: {bbox[0]:.4f},{bbox[1]:.4f} → {bbox[2]:.4f},{bbox[3]:.4f}")

    # Carica sezioni
    print(f" Sezioni: {os.path.basename(SEZIONI_FILE)}")
    with open(SEZIONI_FILE, encoding='utf-8') as f:
        sezioni = json.load(f)
    features_orig = sezioni.get('features', [])
    print(f"   Totale originale: {len(features_orig)}")

    # Filtra
    inside  = []
    outside = []
    for feat in features_orig:
        pt = get_point(feat)
        if pt is None:
            outside.append(feat)
            continue
        # Check rapido bbox prima
        if not (bbox[0] <= pt.x <= bbox[2] and bbox[1] <= pt.y <= bbox[3]):
            outside.append(feat)
            continue
        # Check preciso punto-nel-poligono
        if confine.contains(pt):
            inside.append(feat)
        else:
            outside.append(feat)

    print(f"\n    Dentro i confini: {len(inside)}")
    print(f"    Fuori rimossi:    {len(outside)}")
    riduzione = (len(outside) / len(features_orig) * 100) if features_orig else 0
    print(f"   Riduzione: {riduzione:.1f}%")

    # Salva
    sezioni['features'] = inside
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(sezioni, f, ensure_ascii=False, indent=2)
    print(f"\n Salvato: {OUTPUT_FILE}")
    print(f"   Sezioni finali: {len(inside)}")

if __name__ == '__main__':
    main()