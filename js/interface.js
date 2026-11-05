// js/interface.js — P03 (rotas, camadas, modos, painel de marcador)
import {
  getRoutes, selectRoute, clearRouteSelection, showAllRoutes, hideAllRoutes, getActiveRouteId
} from './routes.js';
import { setMarkersVisible, setObstaclesVisible, setHazardsVisible } from './markers.js';

const LAYERS = {
  architecture:  { label: 'Arquitetura',   default: true },
  routes:        { label: 'Rotas',         default: false },
  markers:       { label: 'Marcadores',    default: true },
  obstacles:     { label: 'Obstáculos',    default: true },
  hazards:       { label: 'Perigos',       default: true }
};

let analysisMode = false;
let onTeleport = null;

export function setProgress(p) {
  const fill = document.getElementById('progress-fill');
  const txt  = document.getElementById('progress-text');
  const pct  = Math.max(0, Math.min(1, p)) * 100;
  if (fill) fill.style.width = pct.toFixed(0) + '%';
  if (txt)  txt.textContent = `Carregando… ${pct.toFixed(0)}%`;
}
export function showStartButton(onStart) {
  const btn = document.getElementById('start-btn');
  if (!btn) return;
  btn.style.display = 'block';
  btn.onclick = () => onStart();
}
export function hideLoading() {
  const el = document.getElementById('loading'); if (el) el.style.display = 'none';
}
export function showControlsInfo() {
  const el = document.getElementById('controls-info'); if (el) el.style.display = 'block';
}
export function showError(msg) {
  hideLoading();
  const el = document.getElementById('error');
  if (el) { el.textContent = '⚠ ' + msg; el.style.display = 'block'; }
}

// -------- Camadas --------
export function initLayerPanel() {
  const panel = document.getElementById('layer-panel');
  if (!panel) return;
  panel.innerHTML = Object.entries(LAYERS).map(([key, cfg]) => `
    <label class="layer-row">
      <input type="checkbox" data-layer="${key}" ${cfg.default ? 'checked' : ''}>
      <span>${cfg.label}</span>
    </label>
  `).join('');
  panel.addEventListener('change', e => {
    const t = e.target;
    if (!(t instanceof HTMLInputElement)) return;
    const key = t.dataset.layer;
    const on = t.checked;
    if (key === 'routes') {
      if (on) showAllRoutes(); else { hideAllRoutes(); clearRouteSelection(); }
    } else if (key === 'markers')   setMarkersVisible(on);
    else if (key === 'obstacles')   setObstaclesVisible(on);
    else if (key === 'hazards')     setHazardsVisible(on);
    else if (key === 'architecture') {
      // Arquitetura: esconde corpos do GLB (não os colisores)
      const root = window.__emerald_model;
      if (root) root.visible = on;
    }
  });
}

// -------- Modo --------
export function initModeToggle() {
  const btn = document.getElementById('mode-btn');
  if (!btn) return;
  btn.addEventListener('click', () => {
    analysisMode = !analysisMode;
    document.body.classList.toggle('analysis-mode', analysisMode);
    btn.textContent = analysisMode ? '● MODO ANÁLISE' : '● MODO EXPLORAÇÃO';
    if (analysisMode) {
      // Ativa camadas de análise
      setMarkersVisible(true); setObstaclesVisible(true); setHazardsVisible(true);
      const routesToggle = document.querySelector('input[data-layer="routes"]');
      if (routesToggle) { routesToggle.checked = true; showAllRoutes(); }
      showRouteSelector();
    } else {
      hideRouteSelector();
      document.querySelector('input[data-layer="routes"]').checked = false;
      hideAllRoutes(); clearRouteSelection();
      hideMarkerPanel();
    }
  });
}

// -------- Painel de rotas --------
export function showRouteSelector() {
  const panel = document.getElementById('route-panel');
  if (!panel) return;
  const routes = getRoutes();
  panel.innerHTML = `<h3>Rotas</h3>` + routes.map(r => `
    <button class="route-btn" data-route="${r.id}">
      <span class="route-status ${r.estado?.startsWith('INTERRUPTED') ? 'st-int' : 'st-ok'}"></span>
      <span class="route-title">${r.id} — ${r.titulo}</span>
    </button>
  `).join('');
  panel.style.display = 'block';
  panel.querySelectorAll('.route-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.dataset.route;
      const meta = selectRoute(id);
      showRouteDetails(meta);
      // Ativa também os marcadores relacionados
      setMarkersVisible(true);
      setObstaclesVisible(true);
      setHazardsVisible(true);
    });
  });
}
export function hideRouteSelector() {
  const p = document.getElementById('route-panel'); if (p) p.style.display = 'none';
  hideRouteDetails();
}

function showRouteDetails(route) {
  const el = document.getElementById('route-details');
  if (!el || !route) return;
  const segs = (route.segments || []).map(s => `
    <li><b>${s.id}</b> — ${s.from.join(',')} → ${s.to.join(',')}
        <span class="seg-meta">[${s.floor}, larg=${s.width_m}m]</span></li>
  `).join('');
  el.innerHTML = `
    <h4>${route.id}</h4>
    <p><b>${route.titulo}</b></p>
    <p><em>${route.origem} → ${route.destino}</em></p>
    <p>${route.objetivo}</p>
    <p><b>Estado:</b> ${route.estado}</p>
    <details><summary>Segmentos (${(route.segments||[]).length})</summary><ul>${segs}</ul></details>
    <div class="route-actions">
      <button id="teleport-start">Ir para origem</button>
      <button id="teleport-end">Ir para destino (demonstrativo)</button>
    </div>
  `;
  el.style.display = 'block';
  document.getElementById('teleport-start')?.addEventListener('click', () => {
    if (onTeleport) onTeleport(route.waypoints[0]);
  });
  document.getElementById('teleport-end')?.addEventListener('click', () => {
    const last = route.waypoints[route.waypoints.length-1];
    if (onTeleport) onTeleport(last);
  });
}
function hideRouteDetails() {
  const el = document.getElementById('route-details'); if (el) el.style.display = 'none';
}

export function setTeleportHandler(fn) { onTeleport = fn; }

// -------- Painel de marcadores --------
export function showMarkerPanel(payload, kind) {
  const el = document.getElementById('marker-panel');
  if (!el) return;
  const color = kind === 'marker' ? '#2e86de' : (kind === 'obstacle' ? '#f1c40f' : '#e74c3c');
  const label = kind === 'marker' ? 'Marcador' : (kind === 'obstacle' ? 'Obstáculo' : 'Perigo');
  const p = payload;
  el.innerHTML = `
    <h3 style="border-bottom-color:${color}">${label}: ${p.nome || p.id}</h3>
    <p><b>ID:</b> ${p.id} · <b>Categoria:</b> ${p.categoria || '—'}</p>
    ${p.descricao ? `<p>${p.descricao}</p>` : ''}
    ${p.condicao ? `<p><b>Condição:</b> ${p.condicao}</p>` : ''}
    ${p.severidade ? `<p><b>Severidade:</b> ${p.severidade}</p>` : ''}
    ${p.rota && p.rota.length ? `<p><b>Rota(s):</b> ${p.rota.join(', ')}</p>` : ''}
    ${p.fonte ? `<p><b>Fonte:</b> ${p.fonte}</p>` : ''}
    ${p.estado_dado ? `<p><b>Estado do dado:</b> ${p.estado_dado}</p>` : ''}
    ${p.observacao ? `<p><em>${p.observacao}</em></p>` : ''}
    <button id="close-marker">Fechar</button>
  `;
  el.style.display = 'block';
  document.getElementById('close-marker')?.addEventListener('click', hideMarkerPanel);
}
export function hideMarkerPanel() {
  const el = document.getElementById('marker-panel'); if (el) el.style.display = 'none';
}

export function isAnalysisMode() { return analysisMode; }