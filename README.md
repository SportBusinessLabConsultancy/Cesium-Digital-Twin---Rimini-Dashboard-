# Rimini Dashboard

Dashboard interattiva per la visualizzazione e l'analisi dei dati territoriali, infrastrutturali e demografici del Comune di Rimini.

Sviluppato da **SBL Consultancy** nell'ambito dello STAGE 2026 SPORT LAB.

---

##  Requisiti di sistema

| Software | Versione minima | Download |
|---|---|---|
| Python | 3.10+ | https://www.python.org |
| Node.js *(opzionale, solo per PMTiles)* | 18+ | https://nodejs.org |
| Browser moderno | Chrome / Firefox / Edge | — |

---

##  Avvio rapido (5 minuti)

### 1. Clona o scarica la cartella

```bash
# Se hai git:
git clone <url-repository> rimini_dashboard
cd rimini_dashboard

# Oppure: scarica lo ZIP, estrai e apri la cartella
```

### 2. Crea l'ambiente virtuale Python

```bash
# Windows
python -m venv stage_env
stage_env\Scripts\activate

# macOS / Linux
python3 -m venv stage_env
source stage_env/bin/activate
```

### 3. Installa le dipendenze Python

```bash
pip install -r requirements.txt
```

### 4. Avvia il server locale

```bash
# Dalla ROOT del progetto (non dalla cartella web/)
python -m http.server 5500
```

### 5. Apri il browser

```
http://127.0.0.1:5500/web/index.html
```
La mappa dovrebbe caricarsi con i confini amministrativi di Rimini già visibili.

---

##  Struttura del progetto

```
rimini_dashboard/
│
├── data/
│   ├── raw/                    # File sorgente originali (GML, Shapefile)
│   │   └── H294_RIMINI_ple.gml # Catasto Agenzia delle Entrate
│   │
│   └── processed/              # GeoJSON e PMTiles pronti per la mappa
│       ├── catasto_rimini.pmtiles
│       ├── confini_rimini.geojson
│       ├── edifici_rimini.geojson
│       ├── quartieri_rimini.geojson
│       └── ... (tutti i layer)
│
├── src/
│   ├── data_collection/        # Script download dati da OSM / fonti esterne
│   │   ├── converti_catasto.py
│   │   ├── download_confini.py
│   │   ├── download_edifici.py
│   │   └── ... (tutti i download_*.py)
│   │
│   └── processing/             # Script di elaborazione e analisi
│       ├── analisi_territorio.py
│       ├── analisi_mobilita.py
│       ├── analisi_infrastrutture.py
│       └── converti_geojson_pmtiles.py
│
├── web/                        # Frontend della dashboard
│   ├── index.html              # Pagina principale
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── img/
│       └── logo_sbl.jpg
│
├── requirements.txt
└── README.md
```

---

## Layer disponibili

### Territorio
| Layer | File | Fonte |
|---|---|---|
| Confini amministrativi | `confini_rimini.geojson` | OSM |
| Particelle catastali | `catasto_rimini.pmtiles` | Agenzia delle Entrate |
| Edifici | `edifici_rimini.geojson` | OSM |
| Uso del suolo | `uso_suolo_rimini.geojson` | OSM |

### Infrastrutture
| Layer | File | Fonte |
|---|---|---|
| Rete stradale | `strade_rimini.geojson` | OSM |
| Piste ciclabili | `ciclabili_rimini.geojson` | OSM |
| Parcheggi | `parcheggi_rimini.geojson` | OSM |
| Illuminazione pubblica | `illuminazione_rimini.geojson` | OSM |
| Arredo urbano | `arredo_urbano_rimini.geojson` | OSM |

### Popolazione
| Layer | File | Fonte |
|---|---|---|
| Quartieri | `quartieri_rimini.geojson` | OSM + ISTAT 2023 |
| Zone toponomastiche | `zone_toponomastiche_rimini.geojson` | SIT Comune di Rimini |

### Mobilità
| Layer | File | Fonte |
|---|---|---|
| Trasporto pubblico | `trasporto_pubblico_rimini.geojson` | OSM |
| Sicurezza stradale | `incidenti_rimini.geojson` | OSM |

### Ambiente
| Layer | File | Fonte |
|---|---|---|
| Rumore urbano | `rumore_rimini.geojson` | OSM |
| Energia | `energia_rimini.geojson` | OSM |

### Servizi e POI
| Layer | File | Fonte |
|---|---|---|
| Scuole | `scuole_rimini.geojson` | OSM |
| Ospedali e sanità | `ospedali_rimini.geojson` | OSM |
| Monumenti | `monumenti_rimini.geojson` | OSM |
| Defibrillatori | `defibrillatori_rimini.geojson` | OSM |
| Edifici pubblici | `uffici_rimini.geojson` | OSM |

### Turismo & Eventi
| Layer | File | Fonte |
|---|---|---|
| Stabilimenti balneari | `balneari_rimini.geojson` | OSM |
| Strutture ricettive | `flussi_turistici_rimini.geojson` | OSM |
| Luoghi eventi | `eventi_rimini.geojson` | OSM |

---

##  Aggiornare i dati

Per aggiornare tutti i layer da OSM:

```bash
# Attiva l'ambiente virtuale prima
stage_env\Scripts\activate  # Windows
source stage_env/bin/activate  # macOS/Linux

# Scarica tutti i layer (esegui dalla root del progetto)
python src/data_collection/download_confini.py
python src/data_collection/download_edifici.py
python src/data_collection/download_quartieri.py
# ... (ripeti per ogni download_*.py)

# Rigenera il catasto
python src/data_collection/converti_catasto.py
python src/processing/converti_geojson_pmtiles.py data/processed/catasto_rimini.geojson --layer catasto_rimini --output data/processed/catasto_rimini.pmtiles --zmin 10 --zmax 16

# Ricalcola le statistiche per i grafici
python src/processing/analisi_territorio.py
python src/processing/analisi_mobilita.py
python src/processing/analisi_infrastrutture.py
```

---

##  Problemi comuni

### La mappa non si carica
- Assicurati di aprire `http://127.0.0.1:5500/web/index.html` e **non** il file direttamente dal filesystem (`file://...`). Il protocollo `pmtiles://` non funziona senza un server HTTP.
- Controlla che il server sia avviato dalla **root del progetto**, non dalla cartella `web/`.

### I layer non appaiono
- Verifica che i file `.geojson` esistano in `data/processed/`.
- Apri la console del browser (F12) e controlla eventuali errori di rete (404).
- Controlla che il server sia ancora in esecuzione nel terminale.

### Il catasto non appare
- Il file `catasto_rimini.pmtiles` deve esistere in `data/processed/`.
- Se manca, esegui `converti_catasto.py` e poi `converti_geojson_pmtiles.py`.
- Il catasto è visibile solo con il plugin PMTiles caricato (già incluso in `index.html`).

### Errore "CORS" nel browser
- Stai aprendo il file direttamente (`file://`). Usa sempre il server Python: `python -m http.server 5500`.

---



