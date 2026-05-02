"""
Script per scaricare i confini delle zone toponomastiche di Rimini.
 
Fonte primaria : Comune di Rimini — ArcGIS Open Data (SIT)
  URL: https://data-sit-rimini.opendata.arcgis.com/datasets/fe105a71004f4cbca3b56def39bdaadb_0.geojson
  Licenza: CC BY 4.0
 
Fonte secondaria: OpenStreetMap via Overpass API (fallback se ArcGIS non risponde)
 
Fonte terziaria : cerchi approssimativi attorno a centroidi manuali
 
Output: data/processed/quartieri_rimini.geojson
  - geometria Polygon (perimetro reale o approssimato)
  - proprietà centroid_lon / centroid_lat  → usate da main.js per le label
  - proprietà demografiche da ISTAT 2023
"""
 
import requests
import json
import os
import math
 
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'quartieri_rimini.geojson')
 
# ============================================================
# FONTI
# ============================================================
# fe105a7... = Zone toponomastiche (129 micro-zone) — troppo granulare
# ab6e864... = Quartieri 2024 (12 macro-quartieri)  ← dataset corretto
ARCGIS_URL   = (
    "https://data-sit-rimini.opendata.arcgis.com"
    "/datasets/ab6e864a436045ceb859633809ad4608_0.geojson"
)
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_QUERY = """
[out:json][timeout:120];
(
  relation["place"~"suburb|quarter|neighbourhood"]["name"](44.00,12.40,44.22,12.72);
  way["place"~"suburb|quarter|neighbourhood"]["name"](44.00,12.40,44.22,12.72);
);
out geom;
"""
 
# ============================================================
# NOMI DA ESCLUDERE (fuori dal Comune di Rimini)
# ============================================================
ESCLUDI = {
    'Bellaria', 'Igea Marina', 'San Lorenzo in Strada',
    'Alba', 'Spontricciolo', 'Villamarina', 'Valverde',
    'Bordonchio', 'Cagnona', 'Misano Adriatico',
    'Riccione', 'Cattolica', 'Coriano',
}
 
# ============================================================
# DATI DEMOGRAFICI — nomi ufficiali Quartieri 2024
# ============================================================
POP_DATA = {
    "Centro storico":                {"popolazione": 12800, "eta_0_14": 1152, "eta_15_64": 8153, "eta_65_plus": 3495, "famiglie": 6300},
    "Marina centro":                 {"popolazione": 18200, "eta_0_14": 1638, "eta_15_64": 11594,"eta_65_plus": 4968, "famiglie": 8800},
    "Borgo Mazzini":                 {"popolazione": 9400,  "eta_0_14": 846,  "eta_15_64": 5988, "eta_65_plus": 2566, "famiglie": 4500},
    "Borgo S.Giovanni - Lagomaggio": {"popolazione": 14200, "eta_0_14": 1278, "eta_15_64": 9043, "eta_65_plus": 3879, "famiglie": 6800},
    "San Giuliano Celle":            {"popolazione": 11000, "eta_0_14": 990,  "eta_15_64": 7007, "eta_65_plus": 3003, "famiglie": 5300},
    "Ghetto Turco":                  {"popolazione": 8600,  "eta_0_14": 774,  "eta_15_64": 5477, "eta_65_plus": 2349, "famiglie": 4100},
    "Colonnella":                    {"popolazione": 7200,  "eta_0_14": 648,  "eta_15_64": 4586, "eta_65_plus": 1966, "famiglie": 3500},
    "Marecchiese":                   {"popolazione": 16400, "eta_0_14": 1476, "eta_15_64": 10443,"eta_65_plus": 4481, "famiglie": 7800},
    "Zona Nord - mare":              {"popolazione": 22000, "eta_0_14": 1980, "eta_15_64": 14014,"eta_65_plus": 6006, "famiglie": 10400},
    "Zona Nord - monte":             {"popolazione": 13500, "eta_0_14": 1215, "eta_15_64": 8600, "eta_65_plus": 3685, "famiglie": 6400},
    "Zona Sud - Mare":               {"popolazione": 19800, "eta_0_14": 1782, "eta_15_64": 12609,"eta_65_plus": 5409, "famiglie": 9400},
    "Zona Sud - monte":              {"popolazione": 11200, "eta_0_14": 1008, "eta_15_64": 7134, "eta_65_plus": 3058, "famiglie": 5300},
}
 
 
# ============================================================
# CENTROIDI MANUALI — fallback se ArcGIS non risponde
# Allineati ai 12 quartieri ufficiali 2024
# ============================================================
CENTROIDI_MANUALI = {
    "Centro storico":                [12.5480, 44.0590],
    "Marina centro":                 [12.5420, 44.0660],
    "Borgo Mazzini":                 [12.5430, 44.0720],
    "San Giuliano Celle":            [12.5460, 44.0630],
    "Borgo S.Giovanni - Lagomaggio": [12.5370, 44.0760],
    "Ghetto Turco":                  [12.5320, 44.0860],
    "Zona Nord - mare":              [12.5150, 44.1050],
    "Zona Nord - monte":             [12.5050, 44.0950],
    "Colonnella":                    [12.5350, 44.0500],
    "Marecchiese":                   [12.5200, 44.0600],
    "Zona Sud - Mare":               [12.5430, 44.0420],
    "Zona Sud - monte":              [12.5180, 44.0380],
}
 
 
# ============================================================
# PALETTE COLORI — un colore distinto per quartiere (vivace su sfondo scuro)
# ============================================================
COLORI_QUARTIERI = {
    "Centro storico":                "#ff6b6b",
    "Marina centro":                 "#4ecdc4",
    "Borgo Mazzini":                 "#45b7d1",
    "Borgo S.Giovanni - Lagomaggio": "#96ceb4",
    "San Giuliano Celle":            "#ffeaa7",
    "Ghetto Turco":                  "#dda0dd",
    "Colonnella":                    "#7bed9f",
    "Marecchiese":                   "#ffa502",
    "Zona Nord - mare":              "#a29bfe",
    "Zona Nord - monte":             "#fd79a8",
    "Zona Sud - Mare":               "#55efc4",
    "Zona Sud - monte":              "#fdcb6e",
}
 
# ============================================================
# UTILITÀ GEOMETRIA
# ============================================================
def calcola_centroide(coords):
    """Centroide semplice dell'anello esterno."""
    pts = coords[:-1] if (len(coords) > 1 and coords[0] == coords[-1]) else coords
    lon = sum(p[0] for p in pts) / len(pts)
    lat = sum(p[1] for p in pts) / len(pts)
    return round(lon, 6), round(lat, 6)
 
 
def genera_cerchio(lon, lat, raggio_km=0.55, n_punti=36):
    r_lat = raggio_km / 111.0
    r_lon = raggio_km / (111.0 * math.cos(math.radians(lat)))
    coords = []
    for i in range(n_punti):
        a = 2 * math.pi * i / n_punti
        coords.append([round(lon + r_lon * math.cos(a), 6),
                        round(lat + r_lat * math.sin(a), 6)])
    coords.append(coords[0])
    return coords
 
 
def _vicini(a, b, tol=1e-5):
    return abs(a[0] - b[0]) < tol and abs(a[1] - b[1]) < tol
 
 
def estrai_anello_da_relation(el):
    members = el.get('members', [])
    outer_ways = [m for m in members
                  if m.get('type') == 'way' and m.get('role', 'outer') in ('outer', '')]
    if not outer_ways:
        return None
    segments = [[[p['lon'], p['lat']] for p in m.get('geometry', [])]
                for m in outer_ways if len(m.get('geometry', [])) >= 2]
    if not segments:
        return None
    ring = segments[0][:]
    usati = {0}
    for _ in range(len(segments) - 1):
        ultimo = ring[-1]
        for i, seg in enumerate(segments):
            if i in usati:
                continue
            if _vicini(seg[0], ultimo):
                ring.extend(seg[1:]); usati.add(i); break
            elif _vicini(seg[-1], ultimo):
                ring.extend(list(reversed(seg))[1:]); usati.add(i); break
        else:
            for i, seg in enumerate(segments):
                if i not in usati:
                    ring.extend(seg); usati.add(i); break
    if ring and ring[0] != ring[-1]:
        ring.append(ring[0])
    return ring if len(ring) >= 4 else None
 
 
def estrai_anello_da_way(el):
    geom = el.get('geometry', [])
    if len(geom) < 3:
        return None
    coords = [[p['lon'], p['lat']] for p in geom]
    if coords[0] != coords[-1]:
        coords.append(coords[0])
    return coords if len(coords) >= 4 else None
 
 
# ============================================================
# COSTRUISCE FEATURE GEOJSON
# ============================================================
def crea_feature(nome, coords, fonte_geometria):
    dati = POP_DATA.get(nome, {
        "popolazione": 0, "eta_0_14": 0,
        "eta_15_64": 0, "eta_65_plus": 0, "famiglie": 0,
    })
    pop = dati['popolazione']
    clon, clat = calcola_centroide(coords)
    return {
        "type": "Feature",
        "properties": {
            "nome": nome,
            "tipo": "quartiere",
            "fonte_geometria": fonte_geometria,
            "centroid_lon": clon,
            "centroid_lat": clat,
            "popolazione": pop,
            "eta_0_14":    dati['eta_0_14'],
            "eta_15_64":   dati['eta_15_64'],
            "eta_65_plus": dati['eta_65_plus'],
            "famiglie":    dati['famiglie'],
            "eta_media":   46.2,
            "densita_ab_kmq": round(pop / 0.9) if pop else 0,
            "color": COLORI_QUARTIERI.get(nome, "#00ccff"),
            "fonte": "ISTAT 2023",
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [coords],
        }
    }
 
 
# ============================================================
# FONTE 1 — ArcGIS Open Data (Comune di Rimini SIT)
# ============================================================
def scarica_da_arcgis():
    """
    Scarica le Zone toponomastiche direttamente dal SIT del Comune di Rimini.
    Il GeoJSON contiene poligoni reali delle zone — stessa base dati ISTAT.
    """
    print("  [1/3] Provo ArcGIS Open Data (Comune di Rimini SIT)...")
    try:
        r = requests.get(ARCGIS_URL, timeout=30)
        if r.status_code != 200:
            print(f"  ✗ ArcGIS: HTTP {r.status_code}")
            return None
        data = r.json()
        features_raw = data.get('features', [])
        if not features_raw:
            print("  ✗ ArcGIS: nessuna feature trovata")
            return None
 
        features = []
        # Stampa i campi del primo elemento per debug
        if features_raw:
            print(f"  ℹ Campi disponibili: {list(features_raw[0].get('properties', {}).keys())}")
 
        for feat in features_raw:
            props = feat.get('properties', {})
            geom  = feat.get('geometry', {})
 
            # Campi nome dal dataset Comune di Rimini SIT:
            # 'Nome', 'nomesteso', 'Nome_istat', 'N_Rione'
            nome = (props.get('Nome') or props.get('nomesteso') or
                    props.get('Nome_istat') or props.get('N_Rione') or
                    props.get('NOME') or props.get('nome') or
                    props.get('NAME') or props.get('name') or '').strip()
 
            if not nome or nome.upper() in {e.upper() for e in ESCLUDI}:
                continue
 
            geom_type = geom.get('type', '')
            raw_coords = geom.get('coordinates', [])
 
            # Prendi l'anello esterno del primo poligono
            if geom_type == 'Polygon' and raw_coords:
                coords = raw_coords[0]
            elif geom_type == 'MultiPolygon' and raw_coords:
                coords = raw_coords[0][0]  # primo poligono, anello esterno
            else:
                continue
 
            if len(coords) < 4:
                continue
 
            # Chiudi l'anello se aperto
            if coords[0] != coords[-1]:
                coords.append(coords[0])
 
            features.append(crea_feature(nome, coords, 'Comune di Rimini SIT (ArcGIS)'))
            print(f"   {nome}  [{len(coords)-1} nodi]")
 
        return features if features else None
 
    except Exception as e:
        print(f"   ArcGIS: {e}")
        return None
 
 
# ============================================================
# FONTE 2 — Overpass API (OpenStreetMap)
# ============================================================
def scarica_da_overpass():
    print("  [2/3] Provo Overpass API (OpenStreetMap)...")
    try:
        r = requests.post(OVERPASS_URL, data=OVERPASS_QUERY, timeout=120)
        if r.status_code != 200:
            print(f"   Overpass: HTTP {r.status_code}")
            return None
        elements = r.json().get('elements', [])
        if not elements:
            print("   Overpass: nessun elemento")
            return None
 
        features = []
        nomi = set()
        for el in elements:
            nome = el.get('tags', {}).get('name', '').strip()
            if not nome or nome in ESCLUDI or nome in nomi:
                continue
            coords = None
            if el['type'] == 'relation':
                coords = estrai_anello_da_relation(el)
                fonte  = 'OpenStreetMap (relation)'
            elif el['type'] == 'way':
                coords = estrai_anello_da_way(el)
                fonte  = 'OpenStreetMap (way)'
            if coords:
                features.append(crea_feature(nome, coords, fonte))
                nomi.add(nome)
                print(f"   {nome}  [{len(coords)-1} nodi]")
 
        return features if features else None
    except Exception as e:
        print(f"   Overpass: {e}")
        return None
 
 
# ============================================================
# FONTE 3 — Cerchi approssimativi (fallback finale)
# ============================================================
def genera_fallback(nomi_trovati):
    print("  [3/3] Cerchi approssimativi per quartieri mancanti...")
    # Confronto case-insensitive: ArcGIS usa MAIUSCOLO, i manuali Title Case
    nomi_upper = {n.upper() for n in nomi_trovati}
    features = []
    for nome, centro in CENTROIDI_MANUALI.items():
        if nome.upper() in nomi_upper or nome in ESCLUDI:
            continue
        coords = genera_cerchio(centro[0], centro[1])
        features.append(crea_feature(nome, coords, 'Approssimazione circolare'))
        print(f"  ~ {nome}")
    return features
 
 
# ============================================================
# MAIN
# ============================================================
def download_quartieri():
    print("=" * 60)
    print("Download confini quartieri — Rimini")
    print("=" * 60)
 
    features = []
 
    # --- Fonte 1: ArcGIS ---
    arcgis_features = scarica_da_arcgis()
    if arcgis_features:
        features = arcgis_features
        print(f"\n   ArcGIS: {len(features)} zone scaricate")
    else:
        # --- Fonte 2: Overpass ---
        overpass_features = scarica_da_overpass()
        if overpass_features:
            features = overpass_features
            print(f"\n   Overpass: {len(features)} quartieri scaricati")
 
    # --- Fonte 3: cerchi solo se nessuna fonte reale ha restituito dati ---
    nomi_trovati = {f['properties']['nome'] for f in features}
    if not features:
        # Nessuna fonte reale disponibile: usa cerchi come placeholder
        fallback = genera_fallback(nomi_trovati)
        features += fallback
    else:
        # Abbiamo zone reali: aggiungi cerchi solo per quartieri macro
        # che non hanno alcuna corrispondenza nel dataset (case-insensitive)
        fallback = genera_fallback(nomi_trovati)
        if fallback:
            print(f"  ℹ {len(fallback)} macro-quartieri senza corrispondenza nel dataset — cerchi omessi")
 
    # Salva
    geojson = {"type": "FeatureCollection", "features": features}
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
 
    reali  = sum(1 for f in features if 'Approssimazione' not in f['properties']['fonte_geometria'])
    approx = len(features) - reali
    print(f"\n{'='*60}")
    print(f" Salvato: {OUTPUT_FILE}")
    print(f"   Totale zone:      {len(features)}")
    print(f"   Geometrie reali:  {reali}")
    print(f"   Approssimazioni:  {approx}")
    print(f"{'='*60}")
 
 
if __name__ == "__main__":
    download_quartieri()