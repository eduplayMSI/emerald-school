// js/minimap.js — P03 (mapa esquemático, NÃO técnico)
import * as THREE from 'three';
import { getPlayerPos, getPlayerYaw } from './player.js';

let canvas = null, ctx = null;
let spacesData = null;
let routesData = null;

const WORLD = { xmin: -10, xmax: 42, zmin: -22, zmax: 16 };  // bounds em Web coords

function w2c(x, z, w, h) {
  const px = (x - WORLD.xmin) / (WORLD.xmax - WORLD.xmin) * w;
  const py = (z - WORLD.zmin) / (WORLD.zmax - WORLD.zmin) * h;  // mais negativo = topo
  return [px, py];
}

export async function initMinimap() {
  canvas = document.getElementById('minimap-canvas');
  if (!canvas) return;
  ctx = canvas.getContext('2d');
  try {
    spacesData = await (await fetch('./data/spaces.json')).json();
    routesData = await (await fetch('./data/routes.json')).json();
  } catch (e) {
    console.warn('[EMERALD][minimap] falha JSON:', e);
  }
  resize();
  window.addEventListener('resize', resize);
}

function resize() {
  if (!canvas) return;
  const r = canvas.getBoundingClientRect();
  canvas.width = r.width * devicePixelRatio;
  canvas.height = r.height * devicePixelRatio;
}

export function drawMinimap(activeRouteId) {
  if (!ctx || !canvas) return;
  const w = canvas.width, h = canvas.height;
  ctx.clearRect(0, 0, w, h);
  // Fundo
  ctx.fillStyle = 'rgba(20,30,45,0.85)';
  ctx.fillRect(0, 0, w, h);

  // Ambientes (retângulos)
  if (spacesData) {
    const all = [spacesData.corridor, ...(spacesData.spaces || [])].filter(Boolean);
    for (const sp of all) {
      const [xmin, zmin, xmax, zmax] = sp.bbox;
      const [x1, y1] = w2c(xmin, zmin, w, h);
      const [x2, y2] = w2c(xmax, zmax, w, h);
      ctx.strokeStyle = 'rgba(120,180,230,0.5)';
      ctx.fillStyle = 'rgba(60,110,150,0.25)';
      ctx.lineWidth = 1.5;
      ctx.fillRect(Math.min(x1,x2), Math.min(y1,y2), Math.abs(x2-x1), Math.abs(y2-y1));
      ctx.strokeRect(Math.min(x1,x2), Math.min(y1,y2), Math.abs(x2-x1), Math.abs(y2-y1));
    }
  }

  // Rota ativa
  if (routesData && activeRouteId) {
    const r = routesData.routes.find(x => x.id === activeRouteId);
    if (r) {
      ctx.strokeStyle = '#00e5ff';
      ctx.lineWidth = 3;
      ctx.beginPath();
      r.waypoints.forEach((wp, i) => {
        const [px, py] = w2c(wp[0], wp[2], w, h);
        if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
      });
      ctx.stroke();
      // Origem
      const [ox, oy] = w2c(r.waypoints[0][0], r.waypoints[0][2], w, h);
      ctx.fillStyle = '#2ecc71'; ctx.beginPath(); ctx.arc(ox, oy, 4, 0, Math.PI*2); ctx.fill();
      // Destino
      const last = r.waypoints[r.waypoints.length-1];
      const [dx, dy] = w2c(last[0], last[2], w, h);
      ctx.fillStyle = '#e74c3c'; ctx.beginPath(); ctx.arc(dx, dy, 4, 0, Math.PI*2); ctx.fill();
    }
  }

  // Jogador
  const p = getPlayerPos();
  const yaw = getPlayerYaw();
  const [px, py] = w2c(p.x, p.z, w, h);
  ctx.save();
  ctx.translate(px, py);
  // Como z cresce para baixo na tela, yaw de -PI/2 (leste) aponta para +X
  // O ângulo desenhado: yaw medido a partir de +Z(Web) para +X(Web) é negativo
  ctx.rotate(-yaw);
  ctx.fillStyle = '#ffcc00';
  ctx.beginPath();
  ctx.moveTo(0, -7); ctx.lineTo(-5, 5); ctx.lineTo(5, 5); ctx.closePath(); ctx.fill();
  ctx.restore();

  // Legenda
  ctx.fillStyle = 'rgba(255,255,255,0.9)';
  ctx.font = `${11 * devicePixelRatio}px sans-serif`;
  ctx.fillText('Mapa esquemático (não técnico)', 8 * devicePixelRatio, h - 8 * devicePixelRatio);
}