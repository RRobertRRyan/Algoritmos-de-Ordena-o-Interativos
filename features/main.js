/* =====================================================
   main.js — Frontend que consome a API Flask (Python)
   ===================================================== */
'use strict';

// ── ESTADO GLOBAL ────────────────────────────────────
const State = {
  data:        [],
  algorithm:   'selection',
  field:       'gdp',
  sampleSize:  16,
  speed:       110,
  steps:       [],
  stepIdx:     0,
  playing:     false,
  done:        false,
  comparisons: 0,
  swaps:       0,
  startTime:   null,
  elapsed:     0,
  sortedSet:   new Set(),
  timer:       null,
  algMeta:     {},   // metadados vindos do Python
};

// ── UTILITÁRIOS ──────────────────────────────────────
const $ = id => document.getElementById(id);
const setEl = (id, val) => { const el = $(id); if (el) el.textContent = val; };

// ── FETCH DOS METADADOS ──────────────────────────────
async function loadAlgorithmMeta() {
  const res  = await fetch('/api/algorithms');
  const json = await res.json();
  State.algMeta = json;
  updateAlgorithmUI(State.algorithm);
}

// ── FETCH DE DADOS + STEPS (via Python) ──────────────
async function loadSteps() {
  showLoading(true);
  pauseAnim();

  const params = new URLSearchParams({
    algorithm:   State.algorithm,
    field:       State.field,
    sample_size: State.sampleSize,
  });

  try {
    const res  = await fetch(`/api/steps?${params}`);
    const json = await res.json();
    if (!json.ok) throw new Error(json.error);

    State.data     = json.data;
    State.steps    = json.steps;
    State.stepIdx  = 0;
    State.comparisons = 0;
    State.swaps       = 0;
    State.elapsed     = 0;
    State.done        = false;
    State.sortedSet   = new Set();
    State.startTime   = null;

    renderBars(State.data);
    renderCountries(State.data);
    setNarration(`Pronto — ${json.total} passos para ${json.algorithm}. Pressione Play ▶`);
    highlightPseudo(-1);
    $('sorted-banner')?.classList.remove('visible');
    updateStats();
    setButtons(false);
    updateHeapVisibility();

  } catch (e) {
    setNarration(`Erro: ${e.message}`);
    console.error(e);
  }

  showLoading(false);
}

// ── ANIMAÇÃO ─────────────────────────────────────────
function playAnim() {
  if (State.done || !State.steps.length) return;
  State.playing = true;
  if (!State.startTime) State.startTime = Date.now() - State.elapsed;
  setButtons(true);
  tick();
}

function pauseAnim() {
  State.playing = false;
  if (State.timer) clearTimeout(State.timer);
  if (State.startTime) State.elapsed = Date.now() - State.startTime;
  setButtons(false);
}

function stepOnce() {
  if (State.done) return;
  pauseAnim();
  applyStep();
}

function resetAnim() {
  pauseAnim();
  loadSteps();
}

function tick() {
  if (!State.playing || State.done) return;
  applyStep();
  if (!State.done) State.timer = setTimeout(tick, State.speed);
}

function applyStep() {
  if (State.stepIdx >= State.steps.length) { finish(); return; }

  const step = State.steps[State.stepIdx++];
  if (State.startTime) State.elapsed = Date.now() - State.startTime;
  else State.startTime = Date.now();

  // Métricas
  if (step.type === 'compare') State.comparisons++;
  if (step.type === 'swap' || step.type === 'set') State.swaps++;

  // Atualiza array se o passo trouxer dados
  if (step.arr) State.data = step.arr;

  // Sorted set
  if (step.type === 'sorted' && step.indices)
    step.indices.forEach(i => State.sortedSet.add(i));
  if (step.type === 'done')
    for (let i = 0; i < State.data.length; i++) State.sortedSet.add(i);

  // Renderiza
  renderBarsWithStep(State.data, step);
  renderCountriesHighlight(step);
  setNarration(step.msg || '');
  highlightPseudo((step.line || 1) - 1);
  updateStats();

  if (State.algorithm === 'heap' && step.arr)
    renderHeapTree(step.arr, step.i, step.j);

  if (step.type === 'done') finish();
}

function finish() {
  State.done = true; State.playing = false;
  if (State.timer) clearTimeout(State.timer);
  State.sortedSet.clear();
  for (let i = 0; i < State.data.length; i++) State.sortedSet.add(i);
  renderBars(State.data, true);
  $('sorted-banner')?.classList.add('visible');
  setButtons(false);
  updateStats();
}

// ── RENDERIZAÇÃO DAS BARRAS ───────────────────────────

// Returns flag image URL from flagcdn.com using lowercase ISO2
function flagUrl(id) {
  return `https://flagcdn.com/w40/${id.toLowerCase()}.png`;
}

// Format value to short label for bar top
function shortVal(val) {
  if (val >= 1e12) return (val/1e12).toFixed(1) + 'T';
  if (val >= 1e9)  return (val/1e9).toFixed(1)  + 'B';
  if (val >= 1e6)  return (val/1e6).toFixed(1)  + 'M';
  if (val >= 1e3)  return (val/1e3).toFixed(1)  + 'K';
  return val.toFixed(1);
}

function makeBar(d, cls, heightPct) {
  const wrap = document.createElement('div');
  wrap.className = 'bar-wrap';
  wrap.title = `${d.name} (${d.id}): ${d.label}`;

  // Value label above bar
  const valLabel = document.createElement('div');
  valLabel.className = 'bar-value';
  valLabel.textContent = shortVal(d.val);

  // Flag image
  const img = document.createElement('img');
  img.className = 'bar-flag-img';
  img.src = flagUrl(d.id);
  img.alt = d.id;
  img.loading = 'lazy';
  img.onerror = function() { this.style.display='none'; };

  // ISO code
  const iso = document.createElement('div');
  iso.className = 'bar-iso';
  iso.textContent = d.id;

  // Bar column
  const bar = document.createElement('div');
  bar.className = 'bar' + (cls ? ' ' + cls : '');
  bar.style.height = heightPct + '%';

  wrap.appendChild(valLabel);
  wrap.appendChild(img);
  wrap.appendChild(iso);
  wrap.appendChild(bar);
  return { wrap, bar, valLabel };
}

function renderBars(data, allSorted = false) {
  const container = $('bar-container');
  if (!container) return;
  const max = Math.max(...data.map(d => d.val));
  container.innerHTML = '';
  data.forEach((d, i) => {
    const cls = allSorted || State.sortedSet.has(i) ? 'sorted' : '';
    const pct = Math.max(2, (d.val / max) * 100);
    const { wrap } = makeBar(d, cls, pct);
    container.appendChild(wrap);
  });
}

function renderBarsWithStep(data, step) {
  const container = $('bar-container');
  if (!container) return;
  const wraps = container.querySelectorAll('.bar-wrap');
  if (wraps.length !== data.length) { renderBars(data); return; }
  const max = Math.max(...data.map(d => d.val));

  data.forEach((d, i) => {
    const wrap     = wraps[i];
    const bar      = wrap.querySelector('.bar');
    const valLabel = wrap.querySelector('.bar-value');
    const img      = wrap.querySelector('.bar-flag-img');
    const iso      = wrap.querySelector('.bar-iso');

    wrap.title = `${d.name} (${d.id}): ${d.label}`;
    const pct = Math.max(2, (d.val / max) * 100);
    bar.style.height = pct + '%';

    // Update flag if country changed (swap)
    if (img && img.alt !== d.id) {
      img.src = flagUrl(d.id);
      img.alt = d.id;
    }
    if (iso) iso.textContent = d.id;
    if (valLabel) valLabel.textContent = shortVal(d.val);

    // Color class
    bar.className = 'bar';
    if      (State.sortedSet.has(i))                                                          bar.className = 'bar sorted';
    else if (step.type === 'pivot'   && i === step.i)                                         bar.className = 'bar pivot';
    else if (step.type === 'heap'    && (i === step.i || i === step.j))                       bar.className = 'bar heap';
    else if (step.type === 'compare' && (i === step.i || i === step.j))                       bar.className = 'bar compare';
    else if ((step.type === 'swap' || step.type === 'set') && (i === step.i || i === step.j)) bar.className = 'bar swap';
  });
}

// ── PAÍSES ───────────────────────────────────────────
function renderCountries(data) {
  const container = $('countries-list');
  if (!container) return;
  container.innerHTML = data.map((d, i) =>
    `<div class="country-card" data-idx="${i}">
      <span class="country-rank">${i+1}</span>
      <img class="country-flag-img"
           src="https://flagcdn.com/w40/${d.id.toLowerCase()}.png"
           alt="${d.id}"
           onerror="this.style.display='none'"
           loading="lazy">
      <div class="country-info">
        <div class="country-name">${d.name}</div>
        <div class="country-id">${d.id}</div>
      </div>
      <span class="country-val">${d.label}</span>
    </div>`
  ).join('');

  // Atualiza label "ordenado por"
  const lbl = $('ordered-by-label');
  const field = $('field-select');
  if (lbl && field) lbl.textContent = field.options[field.selectedIndex]?.text || '';
}

function renderCountriesHighlight(step) {
  const cards = document.querySelectorAll('.country-card');

  // If data was updated (swap/set), re-render the whole grid to reflect new order
  if ((step.type === 'swap' || step.type === 'set') && step.arr) {
    renderCountries(State.data);
    return;
  }

  cards.forEach(c => c.classList.remove('highlight', 'swap-hl'));
  if (step.type === 'compare') {
    cards[step.i]?.classList.add('highlight');
    cards[step.j]?.classList.add('highlight');
  } else if (step.type === 'swap' || step.type === 'set') {
    cards[step.i]?.classList.add('swap-hl');
    if (step.j !== undefined) cards[step.j]?.classList.add('swap-hl');
  }
}

// ── PSEUDOCÓDIGO ─────────────────────────────────────
function highlightPseudo(lineIdx) {
  document.querySelectorAll('.pseudo-line').forEach((l, i) => {
    l.classList.toggle('active', i === lineIdx);
  });
}

// ── UI DO ALGORITMO (dados vindos do Python) ──────────
function updateAlgorithmUI(key) {
  const algo = State.algMeta[key];
  if (!algo) return;

  // Título
  const parts = algo.name.split(' ');
  const titleEl = $('viz-title');
  if (titleEl) titleEl.innerHTML = parts.slice(0,-1).join(' ') + ' <span>' + parts.slice(-1) + '</span>';

  // Pseudocódigo
  const pseudoEl = $('pseudo-block');
  if (pseudoEl) {
    pseudoEl.innerHTML = algo.pseudo.map((line, i) => {
      const indent = line.match(/^\s*/)[0].length;
      const code   = line.trimStart();
      return `<div class="pseudo-line" data-line="${i}">
        <span class="pseudo-num">${i+1}</span>
        <span class="pseudo-code" style="margin-left:${indent*6}px">${code}</span>
      </div>`;
    }).join('');
  }

  // Como funciona
  const howEl = $('how-text');
  if (howEl) howEl.innerHTML = algo.description.split('\n\n').map(p => `<p>${p.trim()}</p>`).join('');

  const dsEl = $('ds-info');
  if (dsEl) dsEl.textContent = algo.ds;

  // Complexidade
  const cx = algo.complexity;
  if (cx) {
    setEl('cx-best',      cx.best.val);  setEl('cx-best-why',  cx.best.why);
    setEl('cx-avg',       cx.avg.val);   setEl('cx-avg-why',   cx.avg.why);
    setEl('cx-worst',     cx.worst.val); setEl('cx-worst-why', cx.worst.why);
    setEl('cx-space',     cx.space.val); setEl('cx-space-why', cx.space.why);
  }

  updateHeapVisibility();
}

function updateHeapVisibility() {
  const wrap = $('heap-tree-wrap');
  if (wrap) wrap.style.display = State.algorithm === 'heap' ? 'block' : 'none';
}

// ── HEAP TREE SVG ─────────────────────────────────────
function renderHeapTree(arr, activeI, activeJ) {
  const svg = $('heap-svg');
  if (!svg) return;
  const n = Math.min(arr.length, 15);
  const W = 300, H = 100, nodeR = 10;
  const levels = Math.ceil(Math.log2(n + 1));
  const nodes = [];
  for (let i = 0; i < n; i++) {
    const lvl = Math.floor(Math.log2(i + 1));
    const pos = i - (Math.pow(2, lvl) - 1);
    const tot = Math.pow(2, lvl);
    const x   = (W / (tot + 1)) * (pos + 1);
    const y   = 14 + lvl * ((H - 20) / Math.max(levels - 1, 1));
    const raw = arr[i].val;
    const lbl = raw > 1e9 ? (raw / 1e9).toFixed(1) + 'B' : raw > 1e6 ? (raw / 1e6).toFixed(1) + 'M' : String(raw).slice(0,4);
    nodes.push({ x, y, lbl, i });
  }
  let edges = '', circles = '';
  nodes.forEach((nd, i) => {
    const lc = 2*i+1, rc = 2*i+2;
    if (nodes[lc]) edges += `<line x1="${nd.x}" y1="${nd.y}" x2="${nodes[lc].x}" y2="${nodes[lc].y}" stroke="#334155" stroke-width="1"/>`;
    if (nodes[rc]) edges += `<line x1="${nd.x}" y1="${nd.y}" x2="${nodes[rc].x}" y2="${nodes[rc].y}" stroke="#334155" stroke-width="1"/>`;
    const active = nd.i === activeI || nd.i === activeJ;
    circles += `<circle cx="${nd.x}" cy="${nd.y}" r="${nodeR}" fill="${active ? '#06b6d4' : '#1e3a5f'}" stroke="#3b82f6" stroke-width="1"/>
                <text x="${nd.x}" y="${nd.y+2}" text-anchor="middle" fill="white" font-size="5.5" font-family="JetBrains Mono,monospace">${nd.lbl}</text>`;
  });
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  svg.innerHTML = edges + circles;
}

// ── COMPARAÇÃO (chama Python) ─────────────────────────
async function runCompare(sampleSize) {
  showCompareView();
  $('compare-loading').style.display = 'inline';
  $('compare-tbody').innerHTML = '<tr><td colspan="7" style="text-align:center;color:var(--text-muted)">Executando no Python…</td></tr>';

  const n = sampleSize || State.sampleSize;
  const params = new URLSearchParams({ field: State.field, sample_size: n });

  try {
    const res  = await fetch(`/api/compare?${params}`);
    const json = await res.json();
    if (!json.ok) throw new Error(json.error);
    renderCompareTable(json.results);
    renderCompareChart(json.results);
  } catch (e) {
    $('compare-tbody').innerHTML = `<tr><td colspan="7" style="color:var(--accent-red)">Erro: ${e.message}</td></tr>`;
  }

  $('compare-loading').style.display = 'none';
}

function renderCompareTable(results) {
  const minCmp = Math.min(...results.map(r => r.comparisons));
  $('compare-tbody').innerHTML = results.map(r => {
    const best = r.comparisons === minCmp ? ' <span style="color:var(--accent-green);font-size:0.65rem">★ melhor</span>' : '';
    return `<tr>
      <td>${r.name}${best}</td>
      <td>${r.comparisons.toLocaleString()}</td>
      <td>${r.swaps.toLocaleString()}</td>
      <td>${r.time_ms.toFixed(3)}</td>
      <td style="color:var(--accent-cyan)">${r.complexity.best.val}</td>
      <td style="color:var(--accent-gold)">${r.complexity.avg.val}</td>
      <td style="color:var(--accent-red)">${r.complexity.worst.val}</td>
    </tr>`;
  }).join('');
}

function renderCompareChart(results) {
  const colors = ['#3b82f6','#10b981','#f59e0b','#8b5cf6','#ef4444','#06b6d4'];
  const maxCmp  = Math.max(...results.map(r => r.comparisons)) || 1;
  const maxSwap = Math.max(...results.map(r => r.swaps)) || 1;

  const section = (title, key, max) => `
    <div style="margin-bottom:1.5rem">
      <div style="font-family:var(--font-mono);font-size:0.65rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.75rem">${title}</div>
      ${results.map((r, i) => `
        <div class="cbar-row">
          <span class="cbar-label">${r.name}</span>
          <div class="cbar-track">
            <div class="cbar-fill" style="width:${(r[key]/max*100).toFixed(1)}%;background:${colors[i]}">
              <span class="cbar-val">${r[key].toLocaleString()}</span>
            </div>
          </div>
        </div>`).join('')}
    </div>`;

  $('compare-chart').innerHTML = `<div class="compare-bars">
    ${section('Comparações', 'comparisons', maxCmp)}
    ${section('Trocas / Movimentos', 'swaps', maxSwap)}
  </div>`;
}

// ── VIEWS ─────────────────────────────────────────────
function showMainView() {
  $('main-view').style.display    = 'block';
  $('compare-view').classList.remove('active');
  $('tab-main').classList.add('active');
  $('tab-compare').classList.remove('active');
}

function showCompareView() {
  $('main-view').style.display = 'none';
  $('compare-view').classList.add('active');
  $('tab-main').classList.remove('active');
  $('tab-compare').classList.add('active');
}

// ── HELPERS ───────────────────────────────────────────
function showLoading(v) {
  const el = $('loading-overlay');
  if (el) el.style.display = v ? 'flex' : 'none';
}

function setNarration(msg) {
  const el = $('narration');
  if (el) el.textContent = msg;
}

function updateStats() {
  setEl('stat-comparisons', State.comparisons);
  setEl('stat-swaps',       State.swaps);
  setEl('stat-elapsed',     (State.elapsed / 1000).toFixed(2) + 's');
  setEl('stat-steps',       `${State.stepIdx}/${State.steps.length}`);
}

function setButtons(playing) {
  const playBtn  = $('btn-play');
  const pauseBtn = $('btn-pause');
  const stepBtn  = $('btn-step');
  if (playBtn)  playBtn.disabled  = playing || State.done;
  if (pauseBtn) pauseBtn.disabled = !playing;
  if (stepBtn)  stepBtn.disabled  = playing || State.done;
}

// ── INIT ──────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  // Carrega metadados dos algoritmos do Python
  await loadAlgorithmMeta();

  // Carrega passos iniciais
  await loadSteps();

  // Botões de playback
  $('btn-play')?.addEventListener('click', playAnim);
  $('btn-pause')?.addEventListener('click', pauseAnim);
  $('btn-step')?.addEventListener('click', stepOnce);
  $('btn-reset')?.addEventListener('click', resetAnim);

  // Velocidade
  const slider   = $('speed-slider');
  const speedVal = $('speed-val');
  slider?.addEventListener('input', () => {
    State.speed = parseInt(slider.value);
    speedVal.textContent = State.speed + 'ms';
    if (State.playing) { pauseAnim(); playAnim(); }
  });

  // Algoritmo
  $('alg-select')?.addEventListener('change', e => {
    State.algorithm = e.target.value;
    updateAlgorithmUI(State.algorithm);
    loadSteps();
  });

  // Campo
  $('field-select')?.addEventListener('change', e => {
    State.field = e.target.value;
    loadSteps();
  });

  // Tamanho da amostra (select)
  $('sample-select')?.addEventListener('change', e => {
    State.sampleSize = parseInt(e.target.value);
    loadSteps();
  });

  // Botões de amostra rápida
  document.querySelectorAll('.btn-sample').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.btn-sample').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      State.sampleSize = parseInt(btn.dataset.n);
      loadSteps();
    });
  });

  // Comparar todos
  $('btn-compare-all')?.addEventListener('click', () => runCompare());
});
