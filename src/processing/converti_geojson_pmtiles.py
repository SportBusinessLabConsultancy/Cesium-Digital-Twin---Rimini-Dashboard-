"""
converti_geojson_pmtiles.py
─────────────────────────────────────────────────────────────────
Converte un file GeoJSON in PMTiles senza bisogno di tippecanoe.

DIPENDENZE (installa una volta sola):
    pip install pmtiles mapbox-vector-tile shapely pyproj

USO:
    python converti_geojson_pmtiles.py catasto_rimini.geojson
    python converti_geojson_pmtiles.py catasto_rimini.geojson --zmin 12 --zmax 18
"""

import json, math, sys, io, gzip, argparse, time
from pathlib import Path
from collections import defaultdict

try:
    import mapbox_vector_tile
    from shapely.geometry import shape
    from pmtiles.writer import Writer
    from pmtiles.tile import zxy_to_tileid, Compression, TileType
except ImportError as e:
    print(f"\n❌ Pacchetto mancante: {e}")
    print("Installa con:  pip install pmtiles mapbox-vector-tile shapely pyproj")
    sys.exit(1)

EXTENT = 4096

# ── Matematica tile ─────────────────────────────────────────────
def lon_lat_to_tile(lon, lat, zoom):
    n = 2 ** zoom
    x = int((lon + 180.0) / 360.0 * n)
    lat_r = math.radians(max(-85.05, min(85.05, lat)))
    y = int((1.0 - math.log(math.tan(lat_r) + 1.0 / math.cos(lat_r)) / math.pi) / 2.0 * n)
    return x, max(0, min(n - 1, y))

def tile_bounds_wgs84(x, y, z):
    """Ritorna (lon_min, lat_min, lon_max, lat_max) del tile."""
    n = 2 ** z
    lon_min = x / n * 360.0 - 180.0
    lon_max = (x + 1) / n * 360.0 - 180.0
    lat_max = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    lat_min = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n))))
    return lon_min, lat_min, lon_max, lat_max

def feature_bbox(geometry):
    """Bounding box veloce di una geometria GeoJSON."""
    def flatten(c):
        if not c: return []
        if isinstance(c[0], (int, float)): return [c]
        result = []
        for item in c:
            result.extend(flatten(item))
        return result
    pts = flatten(geometry.get('coordinates', []))
    if not pts: return None
    lons = [p[0] for p in pts]
    lats = [p[1] for p in pts]
    return min(lons), min(lats), max(lons), max(lats)

def bbox_tiles(bbox, zoom):
    """Tutti i tile che intersecano il bounding box."""
    lon_min, lat_min, lon_max, lat_max = bbox
    x_min, y_max = lon_lat_to_tile(lon_min, lat_min, zoom)
    x_max, y_min = lon_lat_to_tile(lon_max, lat_max, zoom)
    n = 2 ** zoom
    for x in range(max(0, x_min), min(n, x_max + 1)):
        for y in range(max(0, y_min), min(n, y_max + 1)):
            yield x, y

# ── Conversione principale ───────────────────────────────────────
def converti(input_path, zmin=12, zmax=18, layer_name=None, output_path=None):
    input_path = Path(input_path)
    if not input_path.exists():
        print(f" File non trovato: {input_path}"); sys.exit(1)

    if layer_name is None:
        layer_name = input_path.stem.replace('-', '_').replace(' ', '_')
    if output_path is None:
        output_path = str(input_path.with_suffix('.pmtiles'))

    size_mb = input_path.stat().st_size / 1024 / 1024
    print(f"\n{'='*55}")
    print(f"  GeoJSON → PMTiles")
    print(f"{'='*55}")
    print(f"  Input:   {input_path.name}  ({size_mb:.1f} MB)")
    print(f"  Output:  {Path(output_path).name}")
    print(f"  Layer:   {layer_name}")
    print(f"  Zoom:    {zmin} → {zmax}")

    t0 = time.time()

    # ── 1. Leggi GeoJSON ────────────────────────────────────────
    print(f"\n  [1/4] Caricamento GeoJSON...")
    with open(input_path, encoding='utf-8') as f:
        geojson = json.load(f)
    features = geojson.get('features', [])
    if not features:
        print(" Nessuna feature trovata"); sys.exit(1)
    print(f"       Feature: {len(features):,}")

    # ── 2. Pre-calcola bbox per ogni feature ────────────────────
    print(f"  [2/4] Calcolo bounding box...")
    feat_bboxes = []
    global_lons, global_lats = [], []
    for feat in features:
        geom = feat.get('geometry')
        bb = feature_bbox(geom) if geom else None
        feat_bboxes.append(bb)
        if bb:
            global_lons += [bb[0], bb[2]]
            global_lats += [bb[1], bb[3]]

    global_bbox = (min(global_lons), min(global_lats), max(global_lons), max(global_lats))
    print(f"       BBox: {global_bbox[0]:.4f},{global_bbox[1]:.4f} → {global_bbox[2]:.4f},{global_bbox[3]:.4f}")

    # ── 3. Assegna feature ai tile per ogni zoom ─────────────────
    print(f"  [3/4] Organizzazione per tile e zoom...")
    tile_feats = defaultdict(list)  # (z,x,y) → [idx, ...]

    for zoom in range(zmin, zmax + 1):
        # Campionamento agli zoom bassi per file molto grandi
        if size_mb > 30 and zoom <= 13:
            step = max(1, len(features) // 3000)
        elif size_mb > 30 and zoom <= 14:
            step = max(1, len(features) // 8000)
        else:
            step = 1

        count = 0
        for i in range(0, len(features), step):
            bb = feat_bboxes[i]
            if bb is None: continue
            for tx, ty in bbox_tiles(bb, zoom):
                tile_feats[(zoom, tx, ty)].append(i)
            count += 1

        n_tiles = len([k for k in tile_feats if k[0] == zoom])
        print(f"       Zoom {zoom:2d}: {n_tiles:5d} tile  ({count:,} feature, step={step})")

    total = len(tile_feats)
    print(f"\n       Tile totali da generare: {total:,}")

    # ── 4. Codifica MVT e scrivi PMTiles ─────────────────────────
    print(f"  [4/4] Scrittura PMTiles...")

    tile_data = {}  # tileid → bytes gzip
    errors = 0

    for idx, ((zoom, tx, ty), feat_indices) in enumerate(
        sorted(tile_feats.items(), key=lambda kv: zxy_to_tileid(kv[0][0], kv[0][1], kv[0][2]))
    ):
        tb = tile_bounds_wgs84(tx, ty, zoom)  # (lon_min, lat_min, lon_max, lat_max)

        mvt_features = []
        for fi in feat_indices:
            feat  = features[fi]
            geom  = feat.get('geometry')
            if not geom: continue
            try:
                shp = shape(geom)
                if shp.is_empty: continue
            except Exception:
                continue
            props = feat.get('properties') or {}
            clean = {k: str(v) for k, v in props.items() if v is not None}
            mvt_features.append({'geometry': shp, 'properties': clean})

        if not mvt_features: continue

        try:
            # Struttura corretta: lista con dict 'name' + 'features'
            mvt_bytes = mapbox_vector_tile.encode(
                [{'name': layer_name, 'features': mvt_features}],
                default_options={
                    'extents':         EXTENT,
                    'quantize_bounds': tb,   # scala lon/lat → 0-4096
                    'y_coord_down':    False,
                    'on_invalid_geometry': lambda s: None,
                }
            )
            buf = io.BytesIO()
            with gzip.GzipFile(fileobj=buf, mode='wb') as gz:
                gz.write(mvt_bytes)
            tile_data[zxy_to_tileid(zoom, tx, ty)] = buf.getvalue()
        except Exception as e:
            errors += 1

        if (idx + 1) % 200 == 0:
            elapsed = time.time() - t0
            print(f"       ... {idx+1:,}/{total:,} tile  ({elapsed:.0f}s)")

    if not tile_data:
        print(" Nessun tile generato. Controlla il file GeoJSON.")
        sys.exit(1)

    print(f"       Tile generati: {len(tile_data):,}  (errori skip: {errors})")
    print(f"       Scrittura file...")

    header = {
        'tile_type':        TileType.MVT,
        'tile_compression': Compression.GZIP,
        'min_zoom':         zmin,
        'max_zoom':         zmax,
        'min_lon_e7':       int(global_bbox[0] * 1e7),
        'min_lat_e7':       int(global_bbox[1] * 1e7),
        'max_lon_e7':       int(global_bbox[2] * 1e7),
        'max_lat_e7':       int(global_bbox[3] * 1e7),
        'center_lon_e7':    int(((global_bbox[0] + global_bbox[2]) / 2) * 1e7),
        'center_lat_e7':    int(((global_bbox[1] + global_bbox[3]) / 2) * 1e7),
        'center_zoom':      (zmin + zmax) // 2,
    }
    metadata = {
        'name':      layer_name,
        'format':    'pbf',
        'generator': 'converti_geojson_pmtiles.py',
    }

    with open(output_path, 'wb') as f:
        writer = Writer(f)
        for tileid in sorted(tile_data.keys()):
            writer.write_tile(tileid, tile_data[tileid])
        writer.finalize(header, metadata)

    elapsed = time.time() - t0
    out_mb  = Path(output_path).stat().st_size / 1024 / 1024
    ratio   = (1 - out_mb / size_mb) * 100 if size_mb > 0 else 0

    print(f"\n{'='*55}")
    print(f"   Completato in {elapsed:.1f}s")
    print(f"  {size_mb:.1f} MB  →  {out_mb:.1f} MB  ({ratio:.0f}% riduzione)")
    print(f"  Tile scritti: {len(tile_data):,}")
    print(f"  File: {output_path}")
    print(f"{'='*55}")
    print(f"\n  In test_maplibre.html imposta:")
    print(f"    const CATASTO_USE_PMTILES = true;")
    print(f"    source-layer: '{layer_name}'")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='GeoJSON → PMTiles')
    parser.add_argument('input',   help='File GeoJSON')
    parser.add_argument('--zmin',  type=int, default=12)
    parser.add_argument('--zmax',  type=int, default=18)
    parser.add_argument('--layer', default=None)
    parser.add_argument('--output',default=None)
    args = parser.parse_args()
    converti(args.input, args.zmin, args.zmax, args.layer, args.output)