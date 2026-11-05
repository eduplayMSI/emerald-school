// js/markers.js — P03
import * as THREE from 'three';

const COLORS = {
  marker:  0x2e86de,
  obstacle:0xf1c40f,
  hazard:  0xe74c3c
};

let markersData = { markers: [] };
let obstaclesData = { obstacles: [] };
let hazardsData = { hazards: [] };
let scene = null;
let sprites = [];  // { sprite, kind, payload }
let raycaster = new THREE.Raycaster();
raycaster.params.Sprite = { threshold: 0.3 };

export async function initMarkers(sceneRef) {
  scene = sceneRef;
  try {
    const [mr, ob, hz] = await Promise.all([
      fetch('./data/markers.json').then(r => r.json()).catch(() => ({ markers: [] })),
      fetch('./data/obstacles.json').then(r => r.json()).catch(() => ({ obstacles: [] })),
      fetch('./data/hazards.json').then(r => r.json()).catch(() => ({ hazards: [] }))
    ]);
    markersData = mr; obstaclesData = ob; hazardsData = hz;
    console.log(`[EMERALD][markers] ${mr.markers?.length||0} marcadores, ${ob.obstacles?.length||0} obstáculos, ${hz.hazards?.length||0} perigos.`);
  } catch (e) {
    console.error('[EMERALD][markers] falha:', e);
  }
  buildSprites();
}

function spriteFor(kind, pos) {
  const color = COLORS[kind];
  const size = 256;
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = size;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = `rgba(0,0,0,0.0)`; ctx.fillRect(0,0,size,size);
  ctx.beginPath(); ctx.arc(size/2, size/2, size/2 - 6, 0, Math.PI*2);
  ctx.fillStyle = `#${color.toString(16).padStart(6,'0')}`;
  ctx.fill();
  ctx.lineWidth = 8; ctx.strokeStyle = 'rgba(255,255,255,0.85)';
  ctx.stroke();
  ctx.fillStyle = '#ffffff'; ctx.font = 'bold 100px sans-serif';
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(kind === 'marker' ? 'i' : (kind === 'obstacle' ? '!' : 'X'), size/2, size/2 + 8);
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  const mat = new THREE.SpriteMaterial({ map: tex, depthTest: false, transparent: true });
  const sprite = new THREE.Sprite(mat);
  sprite.position.set(pos[0], pos[1] + 0.30, pos[2]);
  sprite.scale.set(0.55, 0.55, 1);
  sprite.renderOrder = 999;
  return sprite;
}

function buildSprites() {
  sprites = [];
  for (const m of markersData.markers || []) {
    const sp = spriteFor('marker', m.coords);
    sp.userData = { kind: 'marker', id: m.id, payload: m };
    scene.add(sp);
    sprites.push({ sprite: sp, kind: 'marker', payload: m });
  }
  for (const o of obstaclesData.obstacles || []) {
    const sp = spriteFor('obstacle', o.coords);
    sp.userData = { kind: 'obstacle', id: o.id, payload: o };
    scene.add(sp);
    sprites.push({ sprite: sp, kind: 'obstacle', payload: o });
  }
  for (const h of hazardsData.hazards || []) {
    const sp = spriteFor('hazard', h.coords);
    sp.userData = { kind: 'hazard', id: h.id, payload: h };
    scene.add(sp);
    sprites.push({ sprite: sp, kind: 'hazard', payload: h });
  }
}

export function setMarkersVisible(v) {
  for (const s of sprites) if (s.kind === 'marker') s.sprite.visible = v;
}
export function setObstaclesVisible(v) {
  for (const s of sprites) if (s.kind === 'obstacle') s.sprite.visible = v;
}
export function setHazardsVisible(v) {
  for (const s of sprites) if (s.kind === 'hazard') s.sprite.visible = v;
}

export function pick(clientX, clientY, camera) {
  const ndc = new THREE.Vector2(
    (clientX / window.innerWidth) * 2 - 1,
    -(clientY / window.innerHeight) * 2 + 1
  );
  raycaster.setFromCamera(ndc, camera);
  const visibleSprites = sprites.filter(s => s.sprite.visible).map(s => s.sprite);
  const hits = raycaster.intersectObjects(visibleSprites, false);
  if (hits.length === 0) return null;
  return hits[0].object.userData;
}

export function getMarkerById(id) { return (markersData.markers||[]).find(m=>m.id===id); }
export function getObstacleById(id) { return (obstaclesData.obstacles||[]).find(m=>m.id===id); }
export function getHazardById(id) { return (hazardsData.hazards||[]).find(m=>m.id===id); }