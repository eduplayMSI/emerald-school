// js/hud.js — P03
import * as THREE from 'three';
import { getPlayerPos } from './player.js';
import { getActiveRouteId } from './routes.js';

let spacesData = null;
let hudEl = null;
let lastSpaceId = null;

export async function initHUD() {
  hudEl = document.getElementById('hud-space');
  try {
    const res = await fetch('./data/spaces.json');
    if (!res.ok) throw new Error(`spaces.json HTTP ${res.status}`);
    spacesData = await res.json();
    console.log(`[EMERALD][hud] ${spacesData.spaces.length} espaços carregados.`);
  } catch (e) {
    console.warn('[EMERALD][hud] sem spaces.json:', e);
    spacesData = { spaces: [] };
  }
}

export function updateHUD() {
  if (!hudEl || !spacesData) return;
  const p = getPlayerPos();
  let current = null;
  let bestArea = Infinity;

  // Corredor especial (faixa entre as duas fileiras)
  const corr = spacesData.corridor;
  if (corr && p.x >= corr.bbox[0] && p.x <= corr.bbox[2] && p.z >= corr.bbox[1] && p.z <= corr.bbox[3]) {
    current = { id: corr.id, label: corr.label };
  }

  if (!current) {
    for (const sp of spacesData.spaces) {
      const [xmin, zmin, xmax, zmax] = sp.bbox;
      if (p.x >= xmin && p.x <= xmax && p.z >= zmin && p.z <= zmax) {
        const area = (xmax - xmin) * (zmax - zmin);
        if (area < bestArea) { bestArea = area; current = sp; }
      }
    }
  }

  const routeId = getActiveRouteId();
  const routeLine = routeId ? ` · Rota: ${routeId}` : '';

  if (current) {
    if (current.id !== lastSpaceId || routeLine !== (hudEl.dataset.route || '')) {
      hudEl.innerHTML = `<strong>${current.label || current.id}</strong> <span style="opacity:.7">(${current.id})</span>${routeLine}`;
      hudEl.dataset.route = routeLine;
      lastSpaceId = current.id;
    }
  } else if (lastSpaceId !== '__ext__') {
    hudEl.innerHTML = `<em>Área externa</em>${routeLine}`;
    hudEl.dataset.route = routeLine;
    lastSpaceId = '__ext__';
  }
}