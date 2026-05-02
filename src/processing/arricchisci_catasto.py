"""
arricchisci_catasto.py
======================
Spatial join tra le particelle catastali (Polygon) e gli edifici OSM.
Per ogni particella calcola statistiche sugli edifici che vi ricadono:
  - n_edifici       : numero di edifici
  - altezza_media_m : altezza media (da tag 'height' OSM, oppure stimata da 'levels')
  - altezza_max_m   : altezza massima
  - piani_medi      : numero medio di piani
  - tipo_edificio   : tipo prevalente (da tag 'building')

Strategia efficiente per 72k particelle:
  - STRtree sui poligoni catastali
  - Per ogni edificio trova la particella che lo contiene (O(log n))
  - Aggrega i risultati per particella

Input:  data/processed/catasto_rimini.geojson   (output di converti_catasto.py)
        data/processed/edifici_rimini.geojson   (output di download_edifici.py)
Output: data/processed/catasto_rimini.geojson   (sovrascrive con le nuove colonne)

Dipendenze: shapely  →  pip install shapely
"""

import json
import os
from collections import defaultdict

BASE_DIR     = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
CATASTO_FILE = os.path.join(BASE_DIR, 'catasto_rimini.geojson')
EDIFICI_FILE = os.path.join(BASE_DIR, 'edifici_rimini.geojson')


# ── PARSING TAG OSM ───────────────────────────────────────────
def parse_altezza(val):
    if not val:
        return None
    val = str(val).strip().lower().replace(' m','').replace('m','').replace(',','.').strip()
    try:
        h = float(val)
        return round(h, 1) if 0 < h < 999 else None
    except ValueError:
        return None


def parse_piani(val):
    if not val:
        return None
    try:
        p = int(str(val).strip().split('.')[0])
        return p if 0 < p < 100 else None
    except (ValueError, IndexError):
        return None


def stima_altezza_da_piani(piani):
    return round(piani * 3.0 + 1.0, 1) if piani else None


def centroide_approx(geometry):
    """Centroide rapido senza shapely (pre-filtro)."""
    gtype  = geometry.get('type', '')
    coords = geometry.get('coordinates', [])
    try:
        if gtype == 'Point':
            return coords[0], coords[1]
        elif gtype == 'Polygon' and coords:
            ring = coords[0]
            return sum(c[0] for c in ring)/len(ring), sum(c[1] for c in ring)/len(ring)
        elif gtype == 'MultiPolygon' and coords:
            ring = max(coords, key=lambda p: len(p[0]) if p else 0)[0]
            return sum(c[0] for c in ring)/len(ring), sum(c[1] for c in ring)/len(ring)
    except Exception:
        pass
    return None, None


# ── MAIN ──────────────────────────────────────────────────────
def arricchisci_catasto():
    print("=" * 55)
    print("  arricchisci_catasto.py — Spatial Join OSM")
    print("=" * 55)

    for f in [CATASTO_FILE, EDIFICI_FILE]:
        if not os.path.exists(f):
            print(f" File non trovato: {f}")
            return

    try:
        from shapely.geometry import shape as shp_shape, Point
        from shapely.strtree import STRtree
        print(" shapely ok")
    except ImportError:
        print(" shapely non trovato — esegui: pip install shapely")
        return

    # --- Carica GeoJSON ---
    print("\n[1/4] Caricamento file...")
    with open(CATASTO_FILE, encoding='utf-8') as f:
        catasto = json.load(f)
    with open(EDIFICI_FILE, encoding='utf-8') as f:
        edifici_data = json.load(f)

    n_cat  = len(catasto['features'])
    n_edif = len(edifici_data['features'])
    print(f"   Particelle catastali : {n_cat:,}")
    print(f"   Edifici OSM          : {n_edif:,}")

    # --- Costruisce STRtree sulle particelle catastali ---
    print("\n[2/4] Costruzione indice spaziale...")
    shapes       = []   # shapely Polygon per ogni feature valida
    valid_idx    = []   # indice nella lista features[] originale

    for i, feat in enumerate(catasto['features']):
        geom = feat.get('geometry')
        if not geom or geom.get('type') != 'Polygon':
            continue
        try:
            poly = shp_shape(geom)
            if not poly.is_valid:
                poly = poly.buffer(0)
            shapes.append(poly)
            valid_idx.append(i)
        except Exception:
            continue

    tree = STRtree(shapes)
    print(f"   Indice su {len(shapes):,} particelle valide")

    # --- Associa ogni edificio alla sua particella ---
    print("\n[3/4] Spatial join edifici → particelle...")
    parcel_buildings = defaultdict(list)  # indice_features → [edifici]
    n_ok = 0
    n_skip = 0

    for idx_e, feat in enumerate(edifici_data['features']):
        if idx_e % 5000 == 0:
            print(f"   ... {idx_e:,} / {n_edif:,}", end='\r')

        geom = feat.get('geometry')
        if not geom:
            n_skip += 1
            continue

        props = feat.get('properties', {})

        # Altezza: tag 'height' oppure stima da 'levels' / 'building:levels'
        altezza = parse_altezza(props.get('height'))
        piani   = parse_piani(props.get('building:levels') or props.get('levels'))
        if altezza is None and piani is not None:
            altezza = stima_altezza_da_piani(piani)

        tipo = props.get('building', 'yes')

        # Centroide approssimativo per la query STRtree
        lon, lat = centroide_approx(geom)
        if lon is None:
            n_skip += 1
            continue

        pt = Point(lon, lat)
        for cand in tree.query(pt):
            if shapes[cand].contains(pt):
                parcel_buildings[valid_idx[cand]].append({
                    'altezza': altezza,
                    'piani':   piani,
                    'tipo':    tipo,
                })
                n_ok += 1
                break

    print(f"\n   Edifici associati     : {n_ok:,}")
    print(f"   Edifici non trovati   : {n_skip:,}")
    print(f"   Particelle con edifici: {len(parcel_buildings):,}")

    # --- Calcola statistiche per ogni particella ---
    print("\n[4/4] Aggregazione statistiche...")
    for i, feat in enumerate(catasto['features']):
        lista = parcel_buildings.get(i, [])
        n = len(lista)

        if n == 0:
            feat['properties'].update({
                'n_edifici':      0,
                'altezza_media_m': None,
                'altezza_max_m':   None,
                'piani_medi':      None,
                'tipo_edificio':   None,
            })
            continue

        altezze = [e['altezza'] for e in lista if e['altezza'] is not None]
        piani_l = [e['piani']   for e in lista if e['piani']   is not None]

        alt_media = round(sum(altezze)/len(altezze), 1) if altezze else None
        alt_max   = round(max(altezze), 1)               if altezze else None
        piani_med = round(sum(piani_l)/len(piani_l))     if piani_l else None

        tipi_tutti = [e['tipo'] for e in lista]
        tipi_spec  = [t for t in tipi_tutti if t and t != 'yes']
        tipo_prev  = max(set(tipi_spec), key=tipi_spec.count) if tipi_spec else 'residenziale'

        feat['properties'].update({
            'n_edifici':      n,
            'altezza_media_m': alt_media,
            'altezza_max_m':   alt_max,
            'piani_medi':      piani_med,
            'tipo_edificio':   tipo_prev,
        })

    # --- Salva ---
    with open(CATASTO_FILE, 'w', encoding='utf-8') as f:
        json.dump(catasto, f, ensure_ascii=False, indent=2)

    print(f" Salvato: {CATASTO_FILE}")

    # --- Riepilogo ---
    con_altezza = sum(1 for f in catasto['features'] if f['properties'].get('altezza_media_m'))
    con_edifici = sum(1 for f in catasto['features'] if f['properties'].get('n_edifici', 0) > 0)
    print(f"\n Copertura:")
    print(f"   Con edifici  : {con_edifici:,} / {n_cat:,}  ({con_edifici/n_cat*100:.1f}%)")
    print(f"   Con altezza  : {con_altezza:,} / {n_cat:,}  ({con_altezza/n_cat*100:.1f}%)")
    print(f"\n➡  Rigenera il PMTiles:")
    print(f"   python src/processing/converti_geojson_pmtiles.py \\")
    print(f"     data/processed/catasto_rimini.geojson \\")
    print(f"     --layer catasto_rimini \\")
    print(f"     --output data/processed/catasto_rimini.pmtiles \\")
    print(f"     --zmin 10 --zmax 16")


if __name__ == "__main__":
    arricchisci_catasto()