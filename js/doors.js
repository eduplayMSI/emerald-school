// js/doors.js — P02 (swing preferido do Blender, E como contingência, log)
import * as THREE from 'three';
import { getPlayerPos } from './player.js';
import { setDoorColliderDisabled } from './collision.js';

const OPEN_DIST = 2.6;
const ANIM_SPEED = 3.2;
const E_FALLBACK_RADIUS = 3.5;

const doors = [];

export function initDoors(model) {
  const pivots = [];
  model.traverse(obj => {
    if (obj.name && obj.name.startsWith('DOOR_PIVOT_')) pivots.push(obj);
  });

  for (const pivot of pivots) {
    const worldPos = new THREE.Vector3();
    pivot.getWorldPosition(worldPos);
    const doorId = pivot.name.replace('DOOR_PIVOT_', '');

    // Prefere o swing gravado no Blender; senão deriva da posição
    const swingProp = pivot.userData?.emerald_swing;
    const swing = Number.isFinite(swingProp)
      ? Math.sign(swingProp) || 1
      : (worldPos.z < 0 ? +1 : -1);

    doors.push({
      pivot,
      doorId,
      openAngle: swing * Math.PI / 2,
      closedAngle: pivot.rotation.y,
      current: 0,
      colliderDisabled: false,
    });
  }
  console.log(`[EMERALD][doors] ${doors.length} portas registradas:`);
  doors.forEach(d => console.log(`  · ${d.doorId} (openAngle=${d.openAngle.toFixed(3)} rad)`));

  // Contingência: E abre a porta mais próxima num raio de 3.5m
  document.addEventListener('keydown', e => {
    if (e.code !== 'KeyE') return;
    const pos = getPlayerPos();
    let best = null, bestDist = E_FALLBACK_RADIUS;
    for (const d of doors) {
      const wp = new THREE.Vector3();
      d.pivot.getWorldPosition(wp);
      const dist = Math.hypot(pos.x - wp.x, pos.z - wp.z);
      if (dist < bestDist) { bestDist = dist; best = d; }
    }
    if (best) {
      best.current = 1;
      best.colliderDisabled = true;
      setDoorColliderDisabled(best.doorId, true);
      best.pivot.rotation.y = best.openAngle;
      console.log(`[EMERALD][doors] E abriu "${best.doorId}"`);
    }
  });
}

// Recebe um array de posições (jogador + npcs)
export function updateDoors(dt, additionalPositions = []) {
  if (doors.length === 0) return;
  const pos = getPlayerPos();
  const allPositions = [pos, ...additionalPositions];

  for (const d of doors) {
    const wp = new THREE.Vector3();
    d.pivot.getWorldPosition(wp);
    
    let minDist = Infinity;
    // Verifica se qualquer um (jogador ou NPC) está perto
    for (const p of allPositions) {
        const dist = Math.hypot(p.x - wp.x, p.z - wp.z);
        if (dist < minDist) minDist = dist;
    }

    const target = minDist < OPEN_DIST ? 1 : 0;
    if (d.current < target) d.current = Math.min(1, d.current + ANIM_SPEED * dt);
    else if (d.current > target) d.current = Math.max(0, d.current - ANIM_SPEED * dt);

    d.pivot.rotation.y = d.closedAngle + d.current * (d.openAngle - d.closedAngle);

    const shouldDisable = d.current > 0.5 || minDist < OPEN_DIST + 0.4;
    if (shouldDisable !== d.colliderDisabled) {
      d.colliderDisabled = shouldDisable;
      const hits = setDoorColliderDisabled(d.doorId, shouldDisable);
    }
  }
}