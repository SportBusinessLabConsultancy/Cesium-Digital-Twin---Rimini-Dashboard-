// ============================================================
// PMTILES
// ============================================================
if (window.pmtiles) {
  const protocol = new pmtiles.Protocol();
  maplibregl.addProtocol('pmtiles', protocol.tile);
}

const DATA_BASE = 'data/';
const CATASTO_USE_PMTILES = true;

const FILE_MAP = {
  'confini':          'confini_rimini.geojson',
  'catasto':          CATASTO_USE_PMTILES ? null : 'catasto_rimini.geojson',
  'edifici':          'edifici_rimini.geojson',
  'uso-suolo':        'uso_suolo_rimini.geojson',
  'strade':           'strade_rimini.geojson',
  'ciclabili':        'ciclabili_rimini.geojson',
  'parcheggi':        'parcheggi_rimini.geojson',
  'illuminazione':    'illuminazione_rimini.geojson',
  'arredo-urbano':    'arredo_urbano_rimini.geojson',
  'quartieri':        'quartieri_rimini.geojson',
  'zone-topo':        'zone_toponomastiche_rimini.geojson',
  'tpl':              'trasporto_pubblico_rimini.geojson',
  'incidenti':        'incidenti_rimini.geojson',
  'rumore':           'rumore_rimini.geojson',
  'energia':          'energia_rimini.geojson',
  'scuole':           'scuole_rimini.geojson',
  'ospedali':         'ospedali_rimini.geojson',
  'monumenti':        'monumenti_rimini.geojson',
  'defibrillatori':   'defibrillatori_rimini.geojson',
  'edifici-pubblici': 'uffici_rimini.geojson',
  'balneari':         'balneari_rimini.geojson',
  'ricettive':        'flussi_turistici_rimini.geojson',
  'eventi':           'eventi_rimini.geojson',
};

const LAYER_CONFIG = {
  'confini':          { type: 'line',      color: '#e94560', width: 2.5, opacity: 1.0 },
  'catasto':          { type: 'line',      color: '#ccff00', width: 0.8, opacity: 0.9 },
  'edifici':          { type: 'fill',      color: '#f5a623', opacity: 0.35, outline: '#f5a623' },
  'uso-suolo':        { type: 'uso-suolo', color: '#66bb66', opacity: 0.55 },
  'strade':           { type: 'line',      color: '#dddddd', width: 1.0, opacity: 0.7 },
  'ciclabili':        { type: 'line',      color: '#00ff88', width: 1.8, opacity: 1.0 },
  'parcheggi':        { type: 'circle',    color: '#4a90d9', radius: 4,  opacity: 0.85 },
  'illuminazione':    { type: 'circle',    color: '#ffff44', radius: 3,  opacity: 0.65 },
  'arredo-urbano':    { type: 'circle',    color: '#ff8c00', radius: 5,  opacity: 0.85 },
  'quartieri':        { type: 'quartieri', color: '#00ccff', opacity: 0.22 },
  'zone-topo':        { type: 'fill',      color: '#00e5ff', opacity: 0.04, outline: '#00e5ff', outlineWidth: 1.5 },
  'tpl':              { type: 'circle',    color: '#aa44ff', radius: 5,  opacity: 0.9 },
  'incidenti':        { type: 'circle',    color: '#ff4444', radius: 5,  opacity: 0.9 },
  'rumore':           { type: 'mixed',     color: '#ff44aa', radius: 5,  width: 2.5, opacity: 0.85 },
  'energia':          { type: 'mixed',     color: '#ffee00', radius: 5,  opacity: 0.85 },
  'scuole':           { type: 'circle',    color: '#4488ff', radius: 6,  opacity: 0.9 },
  'ospedali':         { type: 'circle',    color: '#ff4444', radius: 6,  opacity: 0.9 },
  'monumenti':        { type: 'circle',    color: '#ffd700', radius: 7,  opacity: 0.95 },
  'defibrillatori':   { type: 'circle',    color: '#ff0000', radius: 5,  opacity: 0.9 },
  'edifici-pubblici': { type: 'circle',    color: '#4a90d9', radius: 6,  opacity: 0.9 },
  'balneari':         { type: 'circle',    color: '#00e5ff', radius: 4,  opacity: 0.8 },
  'ricettive':        { type: 'circle',    color: '#44ddff', radius: 5,  opacity: 0.85 },
  'eventi':           { type: 'circle',    color: '#cc44ff', radius: 6,  opacity: 0.9 },
};

// ============================================================
// SUB MODE COLORS
// ============================================================
const SUB_MODE_COLORS = {
  'strade': {
    field: 'highway',
    colors: { motorway:'#e892a2', trunk:'#fda29b', primary:'#fcd6a4', secondary:'#f7fabf', tertiary:'#ffffff', residential:'#cccccc', service:'#aaaaaa', unclassified:'#bbbbbb' }
  },
  'uso-suolo': { field: 'landuse', colors: {} }, // usa campo 'color' del GeoJSON
  'arredo-urbano': {
    field: 'tipo',
    colors: { panchina:'#8b6914', cestino:'#888888', fontanella:'#4a90d9', fontana:'#00aaff', opera_arte:'#cc44ff', rastrelliera_bici:'#00ff88' }
  },
  'rumore': {
    field: 'tipo',
    colors: { discoteca:'#ff44aa', locale_notturno:'#aa44ff', aeroporto:'#ff6600', ferrovia:'#888888', autostrada:'#aaaaaa' }
  },
  'energia': {
    field: 'tipo',
    colors: { colonnina_ricarica:'#00ff88', pannello_solare:'#ffee00', turbina_eolica:'#00ccff', cabina_elettrica:'#ff9900', centrale_elettrica:'#ff4400' }
  },
  'ospedali': {
    field: 'tipo',
    colors: { ospedale:'#ff4444', clinica:'#ff8888', farmacia:'#00cc44', medico:'#ff9900' }
    // rimosso: altro
  },
  'monumenti': {
    field: 'tipo',
    colors: { monumento:'#ffd700', castello:'#8b4513', chiesa:'#7ab8d8' }
    // rimossi: statua, museo, rovine, memoriale
  },
  'edifici-pubblici': {
    field: 'tipo',
    colors: { municipio:'#e94560', ufficio_postale:'#f5a623', polizia:'#4488ff', vigili_del_fuoco:'#ff6600', ufficio_governativo:'#00ccff' }
    // rimosso: tribunale
  },
  'eventi': {
    field: 'tipo',
    colors: { teatro:'#cc44ff', cinema:'#ff6600', centro_congressi:'#4a90d9', stadio:'#00ff88', palazzetto:'#00ccff', centro_arte:'#ff44aa' }
    // rimosso: arena
  },
};

const LAYERS_WITH_SUBFLAGS = new Set(Object.keys(SUB_MODE_COLORS));

const MIXED_GEO_FILTERS = {
  pt: ['==', ['geometry-type'], 'Point'],
  ln: ['any', ['==', ['geometry-type'], 'LineString'], ['==', ['geometry-type'], 'MultiLineString']],
  pg: ['any', ['==', ['geometry-type'], 'Polygon'],   ['==', ['geometry-type'], 'MultiPolygon']],
};

// Palette colori per i quartieri — assegnati dinamicamente ai nomi reali del GeoJSON
const QUARTIERI_PALETTE = [
  '#e94560','#f5a623','#4a90d9','#00ff88','#aa44ff','#ffee00',
  '#4488ff','#ff9966','#66cc88','#ff6600','#ff66cc','#44ddff',
  '#8844ff','#c8922a','#ff44aa','#ff5500','#00bfff','#cc44ff',
  '#60c070','#ffaa00','#00e5ff','#ff0055','#44ff88','#ff8800',
];

// Viene popolato dinamicamente quando il layer quartieri viene caricato
let quartieriColorExpr = null;

function buildDynamicQuartieriColors(features) {
  // Raccoglie tutti i nomi univoci presenti nel file
  const names = [...new Set(
    features.map(f => f.properties?.nome || f.properties?.name || '').filter(n => n)
  )];
  console.log('Quartieri trovati:', names);
  const expr = ['match', ['coalesce', ['get', 'nome'], ['get', 'name'], '']];
  names.forEach((name, i) => {
    expr.push(name, QUARTIERI_PALETTE[i % QUARTIERI_PALETTE.length]);
  });
  expr.push('#c8922a'); // fallback
  return expr;
}

const LAYER_TO_CHART = {
  'quartieri':      'chart-popolazione',
  'zone-topo':      'chart-popolazione',
  'uso-suolo':      'chart-suolo',
  'edifici':        'chart-edifici',
  'strade':         'chart-strade-km',
  'ciclabili':      'chart-confronto-strade',
  'parcheggi':      'chart-parcheggi-tipo',
  'incidenti':      'chart-sicurezza',
  'tpl':            'chart-tpl-tipi',
  'ricettive':      'chart-turismo',
  'arredo-urbano':  'chart-arredo-polar',
  'scuole':         'chart-servizi-zona',
  'ospedali':       'chart-servizi-zona',
  'monumenti':      'chart-servizi-zona',
  'energia':        'chart-radar-sostenibilita',
  'rumore':         'chart-rumore-zona',
};

// ============================================================
// INIT MAPPA
// ============================================================
const map = new maplibregl.Map({
  container: 'map',
  style: {
    version: 8,
    sources: { 'carto-dark': { type: 'raster',
      tiles: ['https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png','https://b.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png','https://c.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png'],
      tileSize: 256, attribution: '© OpenStreetMap © CartoDB',
    }},
    layers: [{ id: 'carto-bg', type: 'raster', source: 'carto-dark' }]
  },
  center: [12.5683, 44.0678], zoom: 11, antialias: true,
});
map.addControl(new maplibregl.NavigationControl(), 'bottom-right');
map.addControl(new maplibregl.ScaleControl({ unit: 'metric' }), 'bottom-right');

const loadedSources = new Set();
const activeLayers  = new Set();
let totalFeatures   = 0;
let catastoWanted   = false;

let frames = 0, lastFpsTime = performance.now();
function countFrame() {
  frames++;
  const now = performance.now();
  if (now - lastFpsTime > 1000) {
    const fps = Math.round(frames * 1000 / (now - lastFpsTime));
    const el = document.getElementById('perf-fps');
    if (el) { el.textContent = fps + ' FPS'; el.className = fps >= 55 ? '' : fps >= 30 ? 'mid' : 'slow'; }
    frames = 0; lastFpsTime = now;
  }
  requestAnimationFrame(countFrame);
}
requestAnimationFrame(countFrame);

function deduplicateByName(geojson) {
  const seen = new Set();
  geojson.features = geojson.features.filter(f => {
    const key = f.properties?.name || f.properties?.nome || f.properties?.id;
    if (!key) return true;
    if (seen.has(key)) return false;
    seen.add(key); return true;
  });
  return geojson;
}

function getMapLayerIds(id) {
  if (id === 'quartieri') return ['layer-quartieri','layer-quartieri-outline','layer-quartieri-labels'];
  if (id === 'zone-topo') return ['layer-zone-topo','layer-zone-topo-outline','layer-zone-topo-labels'];
  if (id === 'catasto')   return ['layer-catasto-fill','layer-catasto'];
  const cfg = LAYER_CONFIG[id]; if (!cfg) return [];
  switch (cfg.type) {
    case 'line': case 'circle': return [`layer-${id}`];
    case 'fill': case 'uso-suolo': return [`layer-${id}`,`layer-${id}-outline`];
    case 'mixed': return [`layer-${id}-pt`,`layer-${id}-ln`,`layer-${id}-pg`];
    default: return [`layer-${id}`];
  }
}

function setLayerVisibility(id, visible) {
  const v = visible ? 'visible' : 'none';
  getMapLayerIds(id).forEach(lid => { if (map.getLayer(lid)) map.setLayoutProperty(lid, 'visibility', v); });
}

function getColorPropName(id, lid) {
  if (lid.endsWith('-pt')) return 'circle-color';
  if (lid.endsWith('-ln')) return 'line-color';
  if (lid.endsWith('-pg')) return 'fill-color';
  const cfg = LAYER_CONFIG[id]; if (!cfg) return null;
  if (cfg.type === 'circle') return 'circle-color';
  if (cfg.type === 'line') return 'line-color';
  if (cfg.type === 'fill' || cfg.type === 'uso-suolo') return 'fill-color';
  return null;
}

function switchToMainMode(id) {
  const cfg = LAYER_CONFIG[id];
  getMapLayerIds(id).forEach(lid => {
    if (!map.getLayer(lid)) return;
    let filter = null;
    if (cfg?.type === 'mixed') { const s = lid.replace(`layer-${id}-`,''); filter = MIXED_GEO_FILTERS[s] || null; }
    map.setFilter(lid, filter);
    const prop = getColorPropName(id, lid);
    if (prop) map.setPaintProperty(lid, prop, cfg.color);
  });
  if (cfg?.type === 'uso-suolo') {
    const oid = `layer-${id}-outline`;
    if (map.getLayer(oid)) { map.setPaintProperty(oid,'line-color',cfg.color); map.setFilter(oid,null); }
  }
}

function switchToSubMode(id, activeVals) {
  const cfg = LAYER_CONFIG[id];
  const subMode = SUB_MODE_COLORS[id]; if (!subMode) return;
  const { field } = subMode;
  const tipoFilter = activeVals.length > 0 ? ['in', ['get', field], ['literal', activeVals]] : null;
  let colorExpr;
  if (id === 'uso-suolo') {
    colorExpr = ['coalesce', ['get', 'color'], cfg.color];
  } else {
    const me = ['match', ['get', field]];
    for (const [v, c] of Object.entries(subMode.colors)) me.push(v, c);
    me.push(cfg.color); colorExpr = me;
  }
  getMapLayerIds(id).forEach(lid => {
    if (!map.getLayer(lid)) return;
    let filter = tipoFilter;
    if (cfg?.type === 'mixed') { const s = lid.replace(`layer-${id}-`,''); const g = MIXED_GEO_FILTERS[s]; filter = g && tipoFilter ? ['all',g,tipoFilter] : (g||tipoFilter); }
    map.setFilter(lid, filter);
    const prop = getColorPropName(id, lid);
    if (prop) map.setPaintProperty(lid, prop, colorExpr);
  });
  if (cfg?.type === 'uso-suolo') {
    const oid = `layer-${id}-outline`;
    if (map.getLayer(oid)) { map.setPaintProperty(oid,'line-color',colorExpr); map.setFilter(oid,tipoFilter); }
  }
}

async function loadLayer(id) {
  const filename = FILE_MAP[id]; if (!filename) return;
  const t0 = performance.now();
  showLoadIndicator(id);
  try {
    if (!loadedSources.has(id)) {
      const resp = await fetch(DATA_BASE + filename);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      let geojson = await resp.json();
      if (id === 'scuole' || id === 'ospedali') deduplicateByName(geojson);
      totalFeatures += geojson.features?.length || 0;
      const pf = document.getElementById('perf-features'); if (pf) pf.textContent = totalFeatures.toLocaleString();
      map.addSource(id, { type: 'geojson', data: geojson });
      loadedSources.add(id);
      // Costruisce i colori dinamici per i quartieri dai nomi reali del file
      if (id === 'quartieri') {
        quartieriColorExpr = buildDynamicQuartieriColors(geojson.features);
      }
      const elapsed = Math.round(performance.now() - t0);
      const pt = document.getElementById('perf-time');
      if (pt) { pt.textContent = elapsed+'ms'; pt.className = elapsed<800?'':elapsed<2000?'mid':'slow'; }
    }
    addMapLayer(id);
    activeLayers.add(id);
    const pl = document.getElementById('perf-layers'); if (pl) pl.textContent = activeLayers.size;
  } catch(e) { console.error(`❌ ${id}:`,e); } finally { hideLoadIndicator(); }
}

function addMapLayer(id) {
  const cfg = LAYER_CONFIG[id]; if (!cfg) return;
  const firstId = getMapLayerIds(id)[0];
  if (firstId && map.getLayer(firstId)) { setLayerVisibility(id, true); return; }
  const layerId = `layer-${id}`, color = cfg.color;

  if (id === 'quartieri') {
    const colorExpr = quartieriColorExpr || ['literal', '#c8922a'];
    map.addLayer({ id:'layer-quartieri', type:'fill', source:id, paint:{'fill-color':colorExpr,'fill-opacity':0.30} }, getLayerInsertBefore());
    map.addLayer({ id:'layer-quartieri-outline', type:'line', source:id, paint:{'line-color':'#ffffff','line-width':1.8,'line-opacity':0.7} });
    map.addLayer({ id:'layer-quartieri-labels', type:'symbol', source:id,
      layout:{'text-field':['coalesce',['get','nome'],['get','name'],''],'text-size':11,'text-font':['Open Sans Bold','Arial Unicode MS Bold'],'text-max-width':8},
      paint:{'text-color':'#fff','text-halo-color':'#000','text-halo-width':1.5}
    });
    map.on('click','layer-quartieri',e=>showPopup(e,id));
    map.on('mouseenter','layer-quartieri',()=>map.getCanvas().style.cursor='pointer');
    map.on('mouseleave','layer-quartieri',()=>map.getCanvas().style.cursor='');
    return;
  }

  if (id === 'zone-topo') {
    // Palette 12 colori che ciclano su tutte le 130 zone
    const zc = ['match', ['get', '_ci'],
      0,'#e94560',  1,'#f5a623',  2,'#4a90d9',  3,'#00ff88',
      4,'#aa44ff',  5,'#00ccff',  6,'#ff6600',  7,'#ff44aa',
      8,'#ffee00',  9,'#4488ff',  10,'#66cc88', 11,'#c8922a',
      '#00e5ff'  // default
    ];
    map.addLayer({ id:'layer-zone-topo', type:'fill', source:id,
      paint:{'fill-color': zc, 'fill-opacity': 0.18}
    }, getLayerInsertBefore());
    map.addLayer({ id:'layer-zone-topo-outline', type:'line', source:id,
      paint:{'line-color': zc, 'line-width': 1.2, 'line-opacity': 1.0}
    });
    map.addLayer({ id:'layer-zone-topo-labels', type:'symbol', source:id,
      layout:{
        'text-field':['coalesce',['get','nome_zona'],['get','nome'],''],
        'text-size': 9,
        'text-font':['Open Sans Regular','Arial Unicode MS Regular'],
        'text-max-width': 8,
        'text-allow-overlap': false,
      },
      paint:{'text-color':'#ffffff','text-halo-color':'#000000','text-halo-width':1.5}
    });
    map.on('click','layer-zone-topo', e=>showPopup(e,id));
    map.on('mouseenter','layer-zone-topo', ()=>map.getCanvas().style.cursor='pointer');
    map.on('mouseleave','layer-zone-topo', ()=>map.getCanvas().style.cursor='');
    return;
  }

  if (cfg.type === 'uso-suolo') {
    map.addLayer({ id:layerId, type:'fill', source:id, paint:{'fill-color':color,'fill-opacity':0.55} }, getLayerInsertBefore());
    map.addLayer({ id:`${layerId}-outline`, type:'line', source:id, paint:{'line-color':color,'line-width':0.5,'line-opacity':0.7} });
    map.on('click',layerId,e=>showPopup(e,id)); map.on('mouseenter',layerId,()=>map.getCanvas().style.cursor='pointer'); map.on('mouseleave',layerId,()=>map.getCanvas().style.cursor='');
    return;
  }
  if (cfg.type === 'fill') {
    map.addLayer({ id:layerId, type:'fill', source:id, paint:{'fill-color':color,'fill-opacity':cfg.opacity} }, getLayerInsertBefore());
    map.addLayer({ id:`${layerId}-outline`, type:'line', source:id, paint:{'line-color':cfg.outline||color,'line-width':cfg.outlineWidth||1,'line-opacity':Math.min((cfg.opacity||0.3)*2,1)} });
    map.on('click',layerId,e=>showPopup(e,id)); map.on('mouseenter',layerId,()=>map.getCanvas().style.cursor='pointer'); map.on('mouseleave',layerId,()=>map.getCanvas().style.cursor='');
    return;
  }
  if (cfg.type === 'line') {
    map.addLayer({ id:layerId, type:'line', source:id, paint:{'line-color':color,'line-width':cfg.width||1,'line-opacity':cfg.opacity||1} });
    map.on('click',layerId,e=>showPopup(e,id)); map.on('mouseenter',layerId,()=>map.getCanvas().style.cursor='pointer'); map.on('mouseleave',layerId,()=>map.getCanvas().style.cursor='');
    return;
  }
  if (cfg.type === 'circle') {
    map.addLayer({ id:layerId, type:'circle', source:id, paint:{'circle-color':color,'circle-radius':cfg.radius||5,'circle-opacity':cfg.opacity||0.9,'circle-stroke-color':'#ffffff','circle-stroke-width':0.8,'circle-stroke-opacity':0.5} });
    map.on('click',layerId,e=>showPopup(e,id)); map.on('mouseenter',layerId,()=>map.getCanvas().style.cursor='pointer'); map.on('mouseleave',layerId,()=>map.getCanvas().style.cursor='');
    return;
  }
  if (cfg.type === 'mixed') {
    map.addLayer({ id:`${layerId}-pt`, type:'circle', source:id, filter:MIXED_GEO_FILTERS.pt, paint:{'circle-color':color,'circle-radius':cfg.radius||5,'circle-opacity':cfg.opacity||0.85,'circle-stroke-color':'#ffffff','circle-stroke-width':0.8,'circle-stroke-opacity':0.5} });
    map.addLayer({ id:`${layerId}-ln`, type:'line',   source:id, filter:MIXED_GEO_FILTERS.ln, paint:{'line-color':color,'line-width':cfg.width||2.5,'line-opacity':cfg.opacity||0.85} });
    map.addLayer({ id:`${layerId}-pg`, type:'fill',   source:id, filter:MIXED_GEO_FILTERS.pg, paint:{'fill-color':color,'fill-opacity':(cfg.opacity||0.85)*0.4} }, getLayerInsertBefore());
    [`${layerId}-pt`,`${layerId}-ln`,`${layerId}-pg`].forEach(lid=>{
      map.on('click',lid,e=>showPopup(e,id)); map.on('mouseenter',lid,()=>map.getCanvas().style.cursor='pointer'); map.on('mouseleave',lid,()=>map.getCanvas().style.cursor='');
    });
  }
}

function getLayerInsertBefore() {
  if (map.getLayer('layer-strade'))  return 'layer-strade';
  if (map.getLayer('layer-confini')) return 'layer-confini';
  return undefined;
}

function removeLayer(id) {
  getMapLayerIds(id).forEach(lid => { if (map.getLayer(lid)) map.setLayoutProperty(lid,'visibility','none'); });
  activeLayers.delete(id);
  const pl = document.getElementById('perf-layers'); if (pl) pl.textContent = activeLayers.size;
}

// ── CATASTO ───────────────────────────────────────────────────
const CATASTO_MIN_ZOOM = 14;
function loadCatastoSource() {
  if (CATASTO_USE_PMTILES && window.pmtiles) {
    if (!map.getSource('catasto')) map.addSource('catasto',{type:'vector',url:`pmtiles://${DATA_BASE}catasto_rimini.pmtiles`});

    if (!map.getLayer('layer-catasto-fill')) {
      // Fill quasi-trasparente: rende TUTTA l'area della particella cliccabile
      map.addLayer({
        id:'layer-catasto-fill', type:'fill',
        source:'catasto', 'source-layer':'catasto_rimini',
        paint:{ 'fill-color':'#ccff00', 'fill-opacity':0.03 }
      });
      // Contorno giallo-verde visibile
      map.addLayer({
        id:'layer-catasto', type:'line',
        source:'catasto', 'source-layer':'catasto_rimini',
        paint:{ 'line-color':'#ccff00', 'line-width':0.8, 'line-opacity':0.9 }
      });
      // Click registrato sul fill → tutta l'area risponde
      map.on('click','layer-catasto-fill', e=>showPopup(e,'catasto'));
      map.on('mouseenter','layer-catasto-fill', ()=>map.getCanvas().style.cursor='pointer');
      map.on('mouseleave','layer-catasto-fill', ()=>map.getCanvas().style.cursor='');
    } else {
      map.setLayoutProperty('layer-catasto-fill','visibility','visible');
      map.setLayoutProperty('layer-catasto','visibility','visible');
    }
    loadedSources.add('catasto'); activeLayers.add('catasto');
    const pl=document.getElementById('perf-layers'); if(pl) pl.textContent=activeLayers.size;
    const hint=document.getElementById('catasto-lod-hint'); if(hint) hint.style.display='none';
    const pt=document.getElementById('perf-time'); if(pt){pt.textContent='~instant';pt.className='';}
  } else { updateCatastoLOD(); }
}
function updateCatastoLOD() {
  if (!catastoWanted) return;
  const hint=document.getElementById('catasto-lod-hint');
  const zoom=map.getZoom();
  if (zoom>=CATASTO_MIN_ZOOM) { if(hint) hint.style.display='none'; if(!loadedSources.has('catasto')) loadLayer('catasto'); else if(map.getLayer('layer-catasto')) map.setLayoutProperty('layer-catasto','visibility','visible'); }
  else { if(hint) hint.style.display='inline'; if(map.getLayer('layer-catasto')) map.setLayoutProperty('layer-catasto','visibility','none'); }
}
map.on('zoomend',()=>{ if(catastoWanted&&!CATASTO_USE_PMTILES) updateCatastoLOD(); });

// ── TOGGLE LAYER ──────────────────────────────────────────────
async function toggleLayer(id, visible) {
  if (id === 'catasto') { catastoWanted=visible; if(visible) loadCatastoSource(); else removeLayer('catasto'); return; }
  if (LAYERS_WITH_SUBFLAGS.has(id)) {
    if (visible) {
      document.querySelectorAll(`.sub-${id}`).forEach(cb=>cb.checked=false);
      const sp=document.getElementById(`sub-${id}`);
      if (sp?.classList.contains('open')) { sp.classList.remove('open'); const b=sp.previousElementSibling?.querySelector('.sub-toggle'); if(b) b.classList.remove('open'); }
      if (!loadedSources.has(id)) { await loadLayer(id); } else { setLayerVisibility(id,true); switchToMainMode(id); }
      activeLayers.add(id);
      const pl=document.getElementById('perf-layers'); if(pl) pl.textContent=activeLayers.size;
      openChartsIfNeeded(id);
    } else {
      document.querySelectorAll(`.sub-${id}`).forEach(cb=>cb.checked=false);
      removeLayer(id);
    }
    return;
  }
  if (visible) { loadLayer(id); openChartsIfNeeded(id); } else { removeLayer(id); }
}

function toggleSub(subId, btn) {
  const sub=document.getElementById(subId); if(!sub) return;
  const wasOpen=sub.classList.contains('open');
  sub.classList.toggle('open'); btn.classList.toggle('open');
  const layerId=subId.replace('sub-','');
  const mainCb=document.getElementById(`cb-${layerId}`);
  if (!wasOpen) { if(mainCb) mainCb.checked=false; removeLayer(layerId); }
  else { document.querySelectorAll(`.sub-${layerId}`).forEach(cb=>cb.checked=false); removeLayer(layerId); }
}

async function applySubFilter(layerId) {
  const allSubs=Array.from(document.querySelectorAll(`.sub-${layerId}`));
  const checked=allSubs.filter(c=>c.checked);
  const activeVals=checked.map(c=>c.dataset.val);
  const parentCb=document.getElementById(`cb-${layerId}`); if(parentCb) parentCb.checked=false;
  if (activeVals.length===0) { removeLayer(layerId); return; }
  if (!loadedSources.has(layerId)) { await loadLayer(layerId); switchToSubMode(layerId,activeVals); }
  else { setLayerVisibility(layerId,true); switchToSubMode(layerId,activeVals); }
  if (!activeLayers.has(layerId)) { activeLayers.add(layerId); const pl=document.getElementById('perf-layers'); if(pl) pl.textContent=activeLayers.size; }
}

// ── POPUP ─────────────────────────────────────────────────────
const popup=new maplibregl.Popup({closeButton:true,closeOnClick:false,maxWidth:'280px'});
function showPopup(e,id) { const p=e.features[0]?.properties||{}; popup.setLngLat(e.lngLat).setHTML(buildPopupHTML(id,p)).addTo(map); }
function buildPopupHTML(id,p) {
  const icons={'confini':'','catasto':'','quartieri':'','zone-topo':'','edifici':'','uso-suolo':'','strade':'','ciclabili':'','parcheggi':'','illuminazione':'','arredo-urbano':'','tpl':'','incidenti':'','rumore':'','energia':'','scuole':'','ospedali':'','monumenti':'','defibrillatori':'','edifici-pubblici':'','balneari':'','ricettive':'','eventi':''};

  // ── POPUP CATASTO ─────────────────────────────────────────
  if (id === 'catasto') {

    // Filtra solo le proprietà effettivamente presenti nel PMTiles
    const entries = Object.entries(p).filter(([, v]) => v != null && v !== '' && v !== 0 && v !== '0');

    if (entries.length === 0) {
      return `<div class="popup-title">🗺 Particella catastale</div>
        <div style="color:#888;font-size:11px;line-height:1.6;padding:4px 0">
          Il PMTiles non contiene proprietà.<br/>
          Rigenera con <code style="color:#ccff00">converti_catasto.py</code><br/>
          poi con <code style="color:#ccff00">converti_geojson_pmtiles.py</code>.
        </div>`;
    }

    // Etichette leggibili per ogni campo noto
    const LABEL_MAP = {
      tipo:              'Tipo',
      label:             'Particella',
      riferimento:       'Riferimento',
      area_mq:           'Area (calc.)',
      area_ufficiale_mq: 'Area (uff.)',
      id:                'ID catasto',
      // campi da nascondere (non utili nel popup)
      centroide_lon: null, centroide_lat: null,
      fonte: null, n_edifici: null,
      altezza_media_m: null, altezza_max_m: null,
      piani_medi: null, tipo_edificio: null,
    };

    let rows = '';
    for (const [k, v] of entries) {
      if (LABEL_MAP[k] === null) continue;

      const lbl = LABEL_MAP[k]
        || k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());

      let display = v;
      if ((k === 'area_mq' || k === 'area_ufficiale_mq') && parseFloat(v) > 0) {
        const mq = parseFloat(v);
        display = mq >= 10000
          ? `${(mq / 10000).toFixed(2)} ha`
          : `${Math.round(mq).toLocaleString('it-IT')} m²`;
      }

      const style = k === 'label'      ? 'color:#ccff00'
                  : k.includes('area') ? 'color:#f5a623'
                  : k === 'id'         ? 'font-size:9px;word-break:break-all;color:#888'
                  : '';

      rows += `<div class="popup-row">
        <span class="popup-key">${lbl}</span>
        <span class="popup-val" style="${style}">${display}</span>
      </div>`;
    }

    // Normalizza il tipo (es. "particella_catastale" → "Particella Catastale")
    const titoloTipo = (p.tipo || 'Particella catastale')
      .replace(/_/g, ' ')
      .replace(/\b\w/g, c => c.toUpperCase());

    return `<div class="popup-title">🗺 ${titoloTipo}</div>
      ${rows}
      <div style="margin-top:8px;padding-top:6px;border-top:1px solid #1e3a5f22;font-size:9px;color:#555">
        Fonte: Agenzia delle Entrate 2026
      </div>`;
  }

  const icon=icons[id]||'', title=p.nome||p.nome_zona||p.name||p.label||p.ref||id;
  const skip=['id','fonte','color','osm_id','osm_type','wikidata'];
  let rows='';
  for (const [k,v] of Object.entries(p)) {
    if(skip.includes(k)||!v||v==='N/D') continue;
    const lbl=k.replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase());
    rows+=`<div class="popup-row"><span class="popup-key">${lbl}</span><span class="popup-val">${v}</span></div>`;
    if(rows.split('popup-row').length>9) break;
  }
  return `<div class="popup-title">${icon} ${title}</div>${rows||'<div style="color:#666;font-size:11px">Nessun dato aggiuntivo</div>'}<div style="margin-top:7px;font-size:9px;color:#444;text-align:right">MapLibre GL JS</div>`;
}

// ── PANNELLO GRAFICI ──────────────────────────────────────────
function openChartsIfNeeded(id) {
  if(!LAYER_TO_CHART[id]) return;
  const panel=document.getElementById('charts-panel'), btn=document.getElementById('toggle-charts');
  if(panel&&!panel.classList.contains('open')) { panel.classList.add('open'); if(btn) btn.style.right='370px'; setTimeout(()=>resizeAllCharts(),350); }
  const target=document.getElementById(LAYER_TO_CHART[id]);
  if(target) setTimeout(()=>target.scrollIntoView({behavior:'smooth',block:'center'}),400);
}
function toggleCharts() {
  const panel=document.getElementById('charts-panel'), btn=document.getElementById('toggle-charts');
  panel.classList.toggle('open');
  btn.style.right=panel.classList.contains('open')?'370px':'0';
  setTimeout(()=>resizeAllCharts(),350);
}
function resizeAllCharts() {
  [chartPop,chartTurismo,chartSuolo,chartEdifici,chartStradeKm,chartConfrontoStrade,chartBenchmark,
   chartParcheggioTipo,chartParcheggioZona,chartTrafficoVelocita,chartTrafficoCorsie,
   chartSicurezza,chartTplTipi,chartTplOperatori,
   chartRadarSostenibilita,chartArredoPolar,chartBubbleDemog,chartSoggiornoMedio,chartServiziZona,
   chartRumoreZona,chartEnergiaBenchmark
  ].forEach(c=>c&&c.resize());
}
function showLoadIndicator(id) { const el=document.getElementById('load-indicator'); if(!el) return; document.getElementById('load-name').textContent='Caricamento: '+id; document.getElementById('load-time').textContent='Attendere...'; el.style.display='block'; }
function hideLoadIndicator() { const el=document.getElementById('load-indicator'); if(el) el.style.display='none'; }

map.on('load',()=>{ loadLayer('confini'); const cb=document.getElementById('cb-confini'); if(cb) cb.checked=true; });

// ============================================================
// CHART.JS
// ============================================================
const chartScript=document.createElement('script');
chartScript.src='https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js';
chartScript.onload=()=>initCharts();
document.head.appendChild(chartScript);

let chartPop=null,chartTurismo=null,chartSuolo=null,chartEdifici=null;
let chartStradeKm=null,chartConfrontoStrade=null,chartBenchmark=null;
let chartParcheggioTipo=null,chartParcheggioZona=null;
let chartTrafficoVelocita=null,chartTrafficoCorsie=null;
let chartSicurezza=null,chartTplTipi=null,chartTplOperatori=null;
// 5 nuovi grafici
let chartRadarSostenibilita=null,chartArredoPolar=null,chartBubbleDemog=null;
let chartSoggiornoMedio=null,chartServiziZona=null;
let chartRumoreZona=null,chartEnergiaBenchmark=null;
let popType='bar',turismoType='arrivi';

// ── DATI GRAFICI ESISTENTI ────────────────────────────────────
const POP_QUARTIERI = {
  labels:['Marina Centro','Viserba','San Giuliano','Miramare','Centro Storico','Borgo S.G.','Rivabella','Bellariva','Torre Pedrera','San Giovanni','Spadarolo','Covignano','Grotta Rossa','Viserbella','Vergiano','Corpolò','Padulli','Marebello','Rivazzurra','San Giuliano Mare','Gaiofana'],
  eta0_14:  [1080,990,828,882,765,702,648,450,522,432,378,369,306,585,279,252,216,315,288,405,189],
  eta15_64: [7644,7007,5860,6243,5414,4969,4586,3185,3695,3058,2675,2612,2166,4141,1974,1784,1529,2230,2038,2867,1338],
  eta65plus:[3276,3003,2512,2675,2321,2130,1966,1365,1583,1310,1147,1119,928,1775,847,764,655,955,874,1229,573],
};
const TURISMO_DATA = {
  mesi:['Gen','Feb','Mar','Apr','Mag','Giu','Lug','Ago','Set','Ott','Nov','Dic'],
  arrivi:  [18500,22000,35000,85000,120000,210000,380000,420000,180000,65000,28000,32000],
  presenze:[52000,61000,98000,290000,420000,890000,1850000,2100000,720000,195000,72000,89000],
};
const SUOLO_SUPERFICI = { labels:['Agricolo','Residenziale','Prati/Erbose','Industriale','Commerciale','Prati/Pascoli','Retail','Cantieri','Cava','Aree Verdi'],values:[742.6,555.2,280.3,238.9,130.2,76.1,50.7,44.9,16.6,16.6],colors:['#c8b87a','#f5e6a3','#b8e6a0','#808080','#f5a623','#a8d58a','#e8604c','#c8843c','#b0a090','#d0e8a0'] };
const EDIFICI_TIPI = { labels:['Generico','Appartamenti','Industriale','Servizi','Tetto','Hotel','Agricolo','Commerciale','Scuola','Chiesa','Villetta','Casa','Retail','Residenziale','Cantiere'],values:[22208,670,443,127,124,117,105,100,73,56,40,36,32,26,21],colors:['#f5a623','#4488ff','#808080','#aa44ff','#aaaaaa','#00ccff','#c8b87a','#ff5500','#4488ff','#7ab8d8','#ff9966','#ff66cc','#e8604c','#f5e6a3','#c8843c'] };
const STRADE_KM = { labels:['Residenziale','Servizio','Terziaria','Non class.','Primaria','Secondaria','Autostrada'],values:[568.6,230.2,129.9,63.2,61.7,41.8,33.5],colors:['#cccccc','#aaaaaa','#ffffff','#bbbbbb','#fcd6a4','#f7fabf','#e892a2'] };
const CONFRONTO_STRADE_CICLABILI={labels:['Rete stradale','Piste ciclabili'],values:[1145.3,122.3],colors:['#ffffff','#00ff88']};
const BENCHMARK_CICLABILI={labels:['Rimini','Media nazionale'],values:[10.7,8.5],colors:['#00ff88','#4a90d9']};
const PARCHEGGI_TIPO={labels:['Superficie','Strada','Non spec.','Sotterraneo','Multipiano','Corsia'],values:[278,273,253,18,4,1],colors:['#4a90d9','#aa44ff','#aaaaaa','#00ccff','#ff6600','#ffee00']};
const PARCHEGGI_ZONA={labels:['Sud','Centro','Costa','Nord','Altro','Ovest'],values:[228,168,155,144,79,53],colors:['#e94560','#f5a623','#00ccff','#4488ff','#aaaaaa','#66bb66']};
const TRAFFICO_VELOCITA={labels:['30','40','50','70','80','90','110','130','N/S'],values:[21,57,491,67,1,22,1,76,207],colors:['#00ff88','#66ff44','#ffee00','#ff9900','#ff6600','#ff4400','#ff2200','#cc0000','#aaaaaa']};
const TRAFFICO_CORSIE={labels:['1','2','3','4','8','N/S'],values:[217,398,87,3,1,237],colors:['#4488ff','#00ccff','#aa44ff','#ff6600','#ff2200','#aaaaaa']};
const SICUREZZA_TIPI={labels:['Semaforo','Attraversamento','Autovelox'],values:[74,50,7],colors:['#ff6600','#ffee00','#ff2200']};
const TPL_TIPI={labels:['Fermata bus','Stazione ferroviaria','Stazione bus','Terminal'],values:[408,5,3,2],colors:['#aa44ff','#4488ff','#00ccff','#00ff88']};
const TPL_OPERATORI={labels:['Non spec.','Start Romagna','RFI','Bonelli Bus','Amrimini'],values:[217,193,5,2,1],colors:['#aaaaaa','#aa44ff','#4488ff','#00ccff','#00ff88']};

// ── DATI 5 NUOVI GRAFICI ──────────────────────────────────────

// 1. RADAR — Profilo Sostenibilità Urbana (scala 0-10)
const RADAR_SOSTENIBILITA = {
  labels: ['Verde pubblico', 'Mobilità ciclabile', 'Copertura TPL', 'Parcheggi/1000ab', 'Sicurezza stradale', 'Energia verde'],
  rimini:        [5.8, 7.1, 6.4, 5.2, 6.8, 4.5],
  media_italia:  [4.2, 5.6, 5.8, 6.1, 5.3, 3.8],
};

// 2. POLAR AREA — Arredo Urbano per tipo (conteggi stimati)
const ARREDO_POLAR = {
  labels: ['Panchine', 'Cestini', 'Fontanelle', 'Fontane', "Opere d'arte", 'Rastrelliere bici'],
  values: [2840, 1920, 185, 42, 88, 310],
  colors: ['#8b6914cc','#888888cc','#4a90d9cc','#00aaffcc','#cc44ffcc','#00ff88cc'],
};

// 3. BUBBLE — Composizione demografica per quartiere
// x = % over65, y = % under14, r = pop/700 (scala visiva)
const BUBBLE_DEMO = [
  { label:'Marina Centro', x:28.2, y:8.7,  r:18, color:'#e94560' },
  { label:'Viserba',       x:26.1, y:9.5,  r:16, color:'#f5a623' },
  { label:'Miramare',      x:29.1, y:8.2,  r:15, color:'#4a90d9' },
  { label:'Centro Storico',x:27.8, y:8.9,  r:13, color:'#aa44ff' },
  { label:'San Giuliano',  x:26.9, y:9.1,  r:14, color:'#00ccff' },
  { label:'Borgo S.G.',    x:25.7, y:9.8,  r:12, color:'#ff6600' },
  { label:'Torre Pedrera', x:24.1, y:10.4, r:9,  color:'#4488ff' },
  { label:'Viserbella',    x:24.5, y:10.1, r:10, color:'#ffee00' },
  { label:'Bellariva',     x:30.2, y:7.9,  r:8,  color:'#ff44aa' },
  { label:'Covignano',     x:25.3, y:10.2, r:6,  color:'#c8922a' },
  { label:'Corpolò',       x:21.8, y:11.3, r:5,  color:'#66cc88' },
  { label:'Gaiofana',      x:20.5, y:11.8, r:4,  color:'#44ddff' },
  { label:'Rivazzurra',    x:31.0, y:7.5,  r:6,  color:'#8844ff' },
  { label:'Grotta Rossa',  x:23.8, y:10.6, r:6,  color:'#ff9966' },
];

// 4. BAR — Durata media soggiorno turistico (presenze/arrivi = giorni)
const SOGGIORNO_MEDIO = {
  mesi:   ['Gen','Feb','Mar','Apr','Mag','Giu','Lug','Ago','Set','Ott','Nov','Dic'],
  giorni: [2.8, 2.8, 2.8, 3.4, 3.5, 4.2, 4.9, 5.0, 4.0, 3.0, 2.6, 2.8],
  // Colori stagionali: inverno=blu, primavera=verde, estate=arancio/giallo, autunno=viola
  colors: ['#4488ff','#4488ff','#66cc88','#66cc88','#66cc88','#f5a623','#ff8800','#ff8800','#f5a623','#aa44ff','#4488ff','#4488ff'],
};

// 5. GROUPED BAR — Servizi essenziali per zona geografica
const SERVIZI_ZONA = {
  zone: ['Costa Nord', 'Centro Storico', 'Costa Sud', 'Entroterra'],
  datasets: [
    { label: ' Scuole',           data: [5, 11, 7, 6],  color: '#4488ff' },
    { label: ' Strutture sanitarie', data: [8, 16, 10, 9], color: '#ff4444' },
    { label: 'Monumenti/Chiese',  data: [3, 18, 5, 7],  color: '#ffd700' },
    { label: ' Edifici pubblici',  data: [4, 9, 5, 5],   color: '#4a90d9' },
  ]
};

// ── INIT ─────────────────────────────────────────────────────
function initCharts() {
  Chart.defaults.color='#a8b2d8'; Chart.defaults.font.family='Segoe UI';
  buildChartPopolazione(); buildChartTurismo(); buildChartSuolo(); buildChartEdifici();
  buildChartStradeKm(); buildChartConfrontoStrade(); buildChartBenchmark();
  buildChartParcheggioTipo(); buildChartParcheggioZona();
  buildChartTrafficoVelocita(); buildChartTrafficoCorsie();
  buildChartSicurezza(); buildChartTplTipi(); buildChartTplOperatori();
  // 5 grafici cross-layer
  buildChartRadarSostenibilita();
  buildChartArredoPolar();
  buildChartBubbleDemog();
  buildChartSoggiornoMedio();
  buildChartServiziZona();
  // 2 nuovi: rumore ed energia
  buildChartRumoreZona();
  buildChartEnergiaBenchmark();
}

const G={color:'#1e3a5f'};

// ── GRAFICI ESISTENTI (compatti) ──────────────────────────────
function buildChartPopolazione() {
  if(chartPop) chartPop.destroy();
  const ctx=document.getElementById('chart-popolazione').getContext('2d');
  if(popType==='bar') {
    chartPop=new Chart(ctx,{type:'bar',data:{labels:POP_QUARTIERI.labels,datasets:[{label:'0-14',data:POP_QUARTIERI.eta0_14,backgroundColor:'#ff9966'},{label:'15-64',data:POP_QUARTIERI.eta15_64,backgroundColor:'#66cc88'},{label:'65+',data:POP_QUARTIERI.eta65plus,backgroundColor:'#aa88ff'}]},options:{indexAxis:'y',responsive:true,plugins:{legend:{position:'bottom',labels:{boxWidth:10,font:{size:9}}}},scales:{x:{stacked:true,grid:G},y:{stacked:true,grid:G,ticks:{font:{size:8}}}}}});
  } else {
    const tot=POP_QUARTIERI.labels.map((_,i)=>POP_QUARTIERI.eta0_14[i]+POP_QUARTIERI.eta15_64[i]+POP_QUARTIERI.eta65plus[i]);
    chartPop=new Chart(ctx,{type:'pie',data:{labels:POP_QUARTIERI.labels,datasets:[{data:tot,backgroundColor:['#e94560','#f5a623','#00ff88','#4a90d9','#aa44ff','#ff6600','#00ccff','#ff44aa','#ffee00','#4488ff','#ff9966','#ff66cc','#60c070','#c8922a','#1e3a5f','#8844ff','#44ddff','#ff5500','#00bfff','#cc44ff','#ff0000']}]},options:{responsive:true,plugins:{legend:{position:'right',labels:{boxWidth:8,font:{size:7}}}}}});
  }
}
function buildChartTurismo() {
  if(chartTurismo) chartTurismo.destroy();
  const ctx=document.getElementById('chart-turismo').getContext('2d');
  const d=turismoType==='arrivi'?TURISMO_DATA.arrivi:TURISMO_DATA.presenze, col=turismoType==='arrivi'?'#c8922a':'#00ccff';
  chartTurismo=new Chart(ctx,{type:'line',data:{labels:TURISMO_DATA.mesi,datasets:[{label:turismoType,data:d,borderColor:col,backgroundColor:col+'33',fill:true,tension:0.4,pointBackgroundColor:col,pointRadius:4}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{x:{grid:G},y:{grid:G,ticks:{callback:v=>v>=1000000?(v/1000000).toFixed(1)+'M':v>=1000?(v/1000).toFixed(0)+'K':v}}}}});
}
function buildChartSuolo() {
  if(chartSuolo) chartSuolo.destroy();
  const ctx=document.getElementById('chart-suolo').getContext('2d');
  chartSuolo=new Chart(ctx,{type:'bar',data:{labels:SUOLO_SUPERFICI.labels,datasets:[{label:'ha',data:SUOLO_SUPERFICI.values,backgroundColor:SUOLO_SUPERFICI.colors,borderColor:'#0d1b2a',borderWidth:1}]},options:{indexAxis:'y',responsive:true,plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>` ${c.parsed.x} ha`}}},scales:{x:{grid:G,ticks:{callback:v=>v+' ha'}},y:{grid:G,ticks:{font:{size:9}}}}}});
}
function buildChartEdifici() {
  if(chartEdifici) chartEdifici.destroy();
  const ctx=document.getElementById('chart-edifici').getContext('2d');
  chartEdifici=new Chart(ctx,{type:'doughnut',data:{labels:EDIFICI_TIPI.labels,datasets:[{data:EDIFICI_TIPI.values,backgroundColor:EDIFICI_TIPI.colors,borderColor:'#0d1b2a',borderWidth:2}]},options:{responsive:true,plugins:{legend:{position:'right',labels:{boxWidth:10,font:{size:8}}},tooltip:{callbacks:{label:c=>` ${c.label}: ${c.parsed.toLocaleString()}`}}}}});
}
function buildChartStradeKm() {
  if(chartStradeKm) chartStradeKm.destroy();
  const ctx=document.getElementById('chart-strade-km').getContext('2d');
  chartStradeKm=new Chart(ctx,{type:'bar',data:{labels:STRADE_KM.labels,datasets:[{label:'km',data:STRADE_KM.values,backgroundColor:STRADE_KM.colors,borderColor:'#0d1b2a',borderWidth:1}]},options:{indexAxis:'y',responsive:true,plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>` ${c.parsed.x} km`}}},scales:{x:{grid:G,ticks:{callback:v=>v+' km'}},y:{grid:G,ticks:{font:{size:9}}}}}});
}
function buildChartConfrontoStrade() {
  if(chartConfrontoStrade) chartConfrontoStrade.destroy();
  const ctx=document.getElementById('chart-confronto-strade').getContext('2d');
  chartConfrontoStrade=new Chart(ctx,{type:'bar',data:{labels:CONFRONTO_STRADE_CICLABILI.labels,datasets:[{label:'km',data:CONFRONTO_STRADE_CICLABILI.values,backgroundColor:CONFRONTO_STRADE_CICLABILI.colors,borderColor:'#0d1b2a',borderWidth:1}]},options:{responsive:true,plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>` ${c.parsed.y} km`}}},scales:{x:{grid:G},y:{grid:G,ticks:{callback:v=>v+' km'}}}}});
}
function buildChartBenchmark() {
  if(chartBenchmark) chartBenchmark.destroy();
  const ctx=document.getElementById('chart-benchmark').getContext('2d');
  chartBenchmark=new Chart(ctx,{type:'bar',data:{labels:BENCHMARK_CICLABILI.labels,datasets:[{label:'km/100km',data:BENCHMARK_CICLABILI.values,backgroundColor:BENCHMARK_CICLABILI.colors,borderColor:'#0d1b2a',borderWidth:1}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{x:{grid:G},y:{grid:G,ticks:{callback:v=>v+' km'},suggestedMax:15}}}});
}
function buildChartParcheggioTipo() {
  if(chartParcheggioTipo) chartParcheggioTipo.destroy();
  const ctx=document.getElementById('chart-parcheggi-tipo').getContext('2d');
  chartParcheggioTipo=new Chart(ctx,{type:'doughnut',data:{labels:PARCHEGGI_TIPO.labels,datasets:[{data:PARCHEGGI_TIPO.values,backgroundColor:PARCHEGGI_TIPO.colors,borderColor:'#0d1b2a',borderWidth:2}]},options:{responsive:true,plugins:{legend:{position:'right',labels:{boxWidth:10,font:{size:9}}}}}});
}
function buildChartParcheggioZona() {
  if(chartParcheggioZona) chartParcheggioZona.destroy();
  const ctx=document.getElementById('chart-parcheggi-zona').getContext('2d');
  chartParcheggioZona=new Chart(ctx,{type:'bar',data:{labels:PARCHEGGI_ZONA.labels,datasets:[{label:'parcheggi',data:PARCHEGGI_ZONA.values,backgroundColor:PARCHEGGI_ZONA.colors,borderColor:'#0d1b2a',borderWidth:1}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{x:{grid:G},y:{grid:G}}}});
}
function buildChartTrafficoVelocita() {
  if(chartTrafficoVelocita) chartTrafficoVelocita.destroy();
  const ctx=document.getElementById('chart-traffico-velocita').getContext('2d');
  chartTrafficoVelocita=new Chart(ctx,{type:'bar',data:{labels:TRAFFICO_VELOCITA.labels,datasets:[{label:'tratti',data:TRAFFICO_VELOCITA.values,backgroundColor:TRAFFICO_VELOCITA.colors,borderColor:'#0d1b2a',borderWidth:1}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{x:{grid:G,ticks:{font:{size:9}}},y:{grid:G}}}});
}
function buildChartTrafficoCorsie() {
  if(chartTrafficoCorsie) chartTrafficoCorsie.destroy();
  const ctx=document.getElementById('chart-traffico-corsie').getContext('2d');
  chartTrafficoCorsie=new Chart(ctx,{type:'doughnut',data:{labels:TRAFFICO_CORSIE.labels,datasets:[{data:TRAFFICO_CORSIE.values,backgroundColor:TRAFFICO_CORSIE.colors,borderColor:'#0d1b2a',borderWidth:2}]},options:{responsive:true,plugins:{legend:{position:'right',labels:{boxWidth:10,font:{size:9}}}}}});
}
function buildChartSicurezza() {
  if(chartSicurezza) chartSicurezza.destroy();
  const ctx=document.getElementById('chart-sicurezza').getContext('2d');
  chartSicurezza=new Chart(ctx,{type:'bar',data:{labels:SICUREZZA_TIPI.labels,datasets:[{label:'elementi',data:SICUREZZA_TIPI.values,backgroundColor:SICUREZZA_TIPI.colors,borderColor:'#0d1b2a',borderWidth:1}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{x:{grid:G,ticks:{font:{size:9}}},y:{grid:G}}}});
}
function buildChartTplTipi() {
  if(chartTplTipi) chartTplTipi.destroy();
  const ctx=document.getElementById('chart-tpl-tipi').getContext('2d');
  chartTplTipi=new Chart(ctx,{type:'doughnut',data:{labels:TPL_TIPI.labels,datasets:[{data:TPL_TIPI.values,backgroundColor:TPL_TIPI.colors,borderColor:'#0d1b2a',borderWidth:2}]},options:{responsive:true,plugins:{legend:{position:'right',labels:{boxWidth:10,font:{size:9}}}}}});
}
function buildChartTplOperatori() {
  if(chartTplOperatori) chartTplOperatori.destroy();
  const ctx=document.getElementById('chart-tpl-operatori').getContext('2d');
  chartTplOperatori=new Chart(ctx,{type:'bar',data:{labels:TPL_OPERATORI.labels,datasets:[{label:'fermate',data:TPL_OPERATORI.values,backgroundColor:TPL_OPERATORI.colors,borderColor:'#0d1b2a',borderWidth:1}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{x:{grid:G,ticks:{font:{size:9}}},y:{grid:G}}}});
}

// ── 5 NUOVI GRAFICI ───────────────────────────────────────────

// 1. RADAR — Profilo Sostenibilità Urbana
function buildChartRadarSostenibilita() {
  if(chartRadarSostenibilita) chartRadarSostenibilita.destroy();
  const ctx=document.getElementById('chart-radar-sostenibilita').getContext('2d');
  chartRadarSostenibilita=new Chart(ctx,{
    type:'radar',
    data:{
      labels: RADAR_SOSTENIBILITA.labels,
      datasets:[
        { label:'Rimini',         data:RADAR_SOSTENIBILITA.rimini,       borderColor:'#e94560', backgroundColor:'#e9456033', pointBackgroundColor:'#e94560', pointRadius:4, borderWidth:2 },
        { label:'Media italiana', data:RADAR_SOSTENIBILITA.media_italia, borderColor:'#4a90d9', backgroundColor:'#4a90d933', pointBackgroundColor:'#4a90d9', pointRadius:3, borderWidth:1.5, borderDash:[5,3] },
      ]
    },
    options:{
      responsive:true,
      plugins:{ legend:{ position:'bottom', labels:{ boxWidth:12, font:{size:10} } } },
      scales:{
        r:{
          suggestedMin:0, suggestedMax:10,
          grid:{ color:'#1e3a5f' },
          angleLines:{ color:'#1e3a5f44' },
          pointLabels:{ font:{size:9}, color:'#a8b2d8' },
          ticks:{ stepSize:2, color:'#666', backdropColor:'transparent', font:{size:8} }
        }
      }
    }
  });
}

// 2. POLAR AREA — Distribuzione Arredo Urbano
function buildChartArredoPolar() {
  if(chartArredoPolar) chartArredoPolar.destroy();
  const ctx=document.getElementById('chart-arredo-polar').getContext('2d');
  chartArredoPolar=new Chart(ctx,{
    type:'polarArea',
    data:{
      labels: ARREDO_POLAR.labels,
      datasets:[{ data:ARREDO_POLAR.values, backgroundColor:ARREDO_POLAR.colors, borderColor:ARREDO_POLAR.colors.map(c=>c.replace('cc','ff')), borderWidth:1 }]
    },
    options:{
      responsive:true,
      plugins:{
        legend:{ position:'right', labels:{ boxWidth:12, font:{size:9} } },
        tooltip:{ callbacks:{ label:c=>` ${c.label}: ${c.parsed.r.toLocaleString()} elementi` } }
      },
      scales:{
        r:{
          grid:{ color:'#1e3a5f' },
          ticks:{ color:'#666', backdropColor:'transparent', font:{size:8} }
        }
      }
    }
  });
}

// 3. BUBBLE — Composizione demografica per quartiere
function buildChartBubbleDemog() {
  if(chartBubbleDemog) chartBubbleDemog.destroy();
  const ctx=document.getElementById('chart-bubble-demo').getContext('2d');
  chartBubbleDemog=new Chart(ctx,{
    type:'bubble',
    data:{
      datasets: BUBBLE_DEMO.map(q=>({
        label: q.label,
        data: [{ x:q.x, y:q.y, r:q.r }],
        backgroundColor: q.color+'99',
        borderColor: q.color,
        borderWidth: 1.5,
      }))
    },
    options:{
      responsive:true,
      plugins:{
        legend:{ display:false },
        tooltip:{
          callbacks:{
            label: ctx => {
              const d=ctx.raw;
              return [`${ctx.dataset.label}`, `Anziani (65+): ${d.x}%`, `Giovani (0-14): ${d.y}%`];
            }
          }
        }
      },
      scales:{
        x:{ title:{ display:true, text:'% Anziani (65+)', color:'#888', font:{size:9} }, min:18, max:34, grid:G, ticks:{ color:'#666', callback:v=>v+'%' } },
        y:{ title:{ display:true, text:'% Giovani (0-14)', color:'#888', font:{size:9} }, min:7, max:13,  grid:G, ticks:{ color:'#666', callback:v=>v+'%' } },
      }
    }
  });
}

// 4. BAR — Durata media soggiorno turistico
function buildChartSoggiornoMedio() {
  if(chartSoggiornoMedio) chartSoggiornoMedio.destroy();
  const ctx=document.getElementById('chart-soggiorno-medio').getContext('2d');
  chartSoggiornoMedio=new Chart(ctx,{
    type:'bar',
    data:{
      labels: SOGGIORNO_MEDIO.mesi,
      datasets:[{
        label: 'Giorni medi',
        data: SOGGIORNO_MEDIO.giorni,
        backgroundColor: SOGGIORNO_MEDIO.colors,
        borderColor: SOGGIORNO_MEDIO.colors.map(c=>c),
        borderWidth: 1,
        borderRadius: 4,
      }]
    },
    options:{
      responsive:true,
      plugins:{
        legend:{ display:false },
        tooltip:{ callbacks:{ label:c=>` ${c.parsed.y} giorni` } },
        annotation:{}
      },
      scales:{
        x:{ grid:G },
        y:{
          grid:G,
          min:0, suggestedMax:6,
          ticks:{ callback:v=>v+'gg' },
          title:{ display:true, text:'giorni medi', color:'#888', font:{size:9} }
        }
      }
    }
  });
}

// 5. GROUPED BAR — Servizi essenziali per zona
function buildChartServiziZona() {
  if(chartServiziZona) chartServiziZona.destroy();
  const ctx=document.getElementById('chart-servizi-zona').getContext('2d');
  chartServiziZona=new Chart(ctx,{
    type:'bar',
    data:{
      labels: SERVIZI_ZONA.zone,
      datasets: SERVIZI_ZONA.datasets.map(ds=>({
        label: ds.label,
        data: ds.data,
        backgroundColor: ds.color+'bb',
        borderColor: ds.color,
        borderWidth: 1,
        borderRadius: 3,
      }))
    },
    options:{
      responsive:true,
      plugins:{
        legend:{ position:'bottom', labels:{ boxWidth:12, font:{size:9} } },
        tooltip:{ callbacks:{ label:c=>` ${c.dataset.label.replace(/^[^\s]+\s/,'')}: ${c.parsed.y}` } }
      },
      scales:{
        x:{ grid:G },
        y:{
          grid:G,
          ticks:{ stepSize:5 },
          title:{ display:true, text:'Numero strutture', color:'#888', font:{size:9} }
        }
      }
    }
  });
}

// ── DATI GRAFICO RUMORE ───────────────────────────────────────
// Stima distribuzione fonti di rumore per zona geografica
const RUMORE_ZONE = {
  zone: ['Costa Nord', 'Centro Storico', 'Costa Sud', 'Entroterra'],
  vita_notturna:  [8, 15, 12, 2],   // discoteche + locali notturni
  infrastrutture: [1, 2, 1, 5],     // ferrovia + autostrada
  aeroporto:      [0, 0, 0, 3],     // impatto aeroporto (solo entroterra/sud)
};

// Indice di pressione acustica stimata per zona (0-10)
const PRESSIONE_ACUSTICA = {
  zone: ['Costa Nord', 'Centro Storico', 'Costa Sud', 'Entroterra'],
  estate: [8.2, 9.1, 8.7, 4.5],
  inverno:[3.1, 6.4, 2.8, 3.2],
};

// ── DATI GRAFICO ENERGIA ──────────────────────────────────────
// Confronto Rimini vs media nazionale (valori per 100.000 abitanti)
const ENERGIA_BENCHMARK = {
  labels: ['Colonnine EV', 'Pannelli solari', 'Turbine eoliche', 'Cabine elettriche', 'Centrali rinnovabili'],
  rimini:    [18.2, 11.3, 1.2, 28.5, 0.8],
  nazionale: [15.4,  9.8, 3.1, 24.2, 1.4],
  colori:    ['#00ff88','#ffee00','#00ccff','#ff9900','#ff4400'],
};

// ── BUILD GRAFICO 6: RUMORE PER ZONA ─────────────────────────
function buildChartRumoreZona() {
  if(chartRumoreZona) chartRumoreZona.destroy();
  const ctx = document.getElementById('chart-rumore-zona').getContext('2d');
  chartRumoreZona = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: RUMORE_ZONE.zone,
      datasets: [
        {
          label: ' Vita notturna',
          data: RUMORE_ZONE.vita_notturna,
          backgroundColor: '#ff44aa99',
          borderColor: '#ff44aa',
          borderWidth: 1, borderRadius: 3,
        },
        {
          label: ' Infrastrutture',
          data: RUMORE_ZONE.infrastrutture,
          backgroundColor: '#88888899',
          borderColor: '#aaaaaa',
          borderWidth: 1, borderRadius: 3,
        },
        {
          label: ' Aeroporto',
          data: RUMORE_ZONE.aeroporto,
          backgroundColor: '#ff660099',
          borderColor: '#ff6600',
          borderWidth: 1, borderRadius: 3,
        },
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 9 } } },
        tooltip: { callbacks: { label: c => ` ${c.dataset.label}: ${c.parsed.y} sorgenti` } },
      },
      scales: {
        x: { grid: G },
        y: {
          grid: G, stacked: false,
          title: { display: true, text: 'N° sorgenti rumore', color: '#888', font: { size: 9 } },
          ticks: { stepSize: 5 },
        }
      }
    }
  });
}

// ── BUILD GRAFICO 7: ENERGIA BENCHMARK ───────────────────────
function buildChartEnergiaBenchmark() {
  if(chartEnergiaBenchmark) chartEnergiaBenchmark.destroy();
  const ctx = document.getElementById('chart-energia-benchmark').getContext('2d');
  chartEnergiaBenchmark = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ENERGIA_BENCHMARK.labels,
      datasets: [
        {
          label: 'Rimini',
          data: ENERGIA_BENCHMARK.rimini,
          backgroundColor: ENERGIA_BENCHMARK.colori.map(c => c + '99'),
          borderColor: ENERGIA_BENCHMARK.colori,
          borderWidth: 2, borderRadius: 4,
        },
        {
          label: 'Media nazionale',
          data: ENERGIA_BENCHMARK.nazionale,
          backgroundColor: '#4a90d944',
          borderColor: '#4a90d9',
          borderWidth: 1.5, borderRadius: 4,
          borderDash: [4, 3],
          type: 'line',
          tension: 0.3,
          pointBackgroundColor: '#4a90d9',
          pointRadius: 4,
          fill: false,
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 9 } } },
        tooltip: {
          callbacks: {
            label: c => ` ${c.dataset.label}: ${c.parsed.y} per 100k ab.`
          }
        },
      },
      scales: {
        x: { grid: G, ticks: { font: { size: 8 } } },
        y: {
          grid: G,
          title: { display: true, text: 'Impianti per 100.000 ab.', color: '#888', font: { size: 9 } },
          suggestedMax: 35,
        }
      }
    }
  });
}

// ── SWITCH GRAFICI ────────────────────────────────────────────
function switchPop(type) {
  popType=type;
  document.querySelectorAll('.chart-tabs .tab-btn').forEach((b,i)=>{b.classList.toggle('active',(type==='bar'&&i===0)||(type==='pie'&&i===1));});
  buildChartPopolazione();
}
function switchTurismo(type) { turismoType=type; buildChartTurismo(); }