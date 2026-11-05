import * as THREE from 'three';
import { getPlayerPos } from './player.js';
import { setDoorColliderDisabled } from './collision.js';

const OPEN_DIST = 2.6;
const ANIM_SPEED = 3.2;   // unidades de abertura por segundo (0→1)

const doors = [];

export function initDoors(model) {
  const pivots = [];
  model.traverse(obj => {
    if (obj.name.startsWith('DOOR_PIVOT_')) pivots.push(obj);
  });

  for (const pivot of pivots) {
    const worldPos = new THREE.Vector3();
    pivot.getWorldPosition(worldPos);

    // swing: portas ao norte (z<0) abrem +90°, ao sul (z>0) abrem -90°
    // Ver nota técnica no relatório.
    const swing = worldPos.z < 0 ? +1 : -1;

    doors.push({
      pivot,
      doorId: pivot.name.replace('DOOR_PIVOT_', ''),
      openAngle: swing * Math.PI / 2,
      closedAngle: pivot.rotation.y,
      current: 0,           // 0 fechada, 1 aberta
      colliderDisabled: false,
    });
  }
  console.log(`[EMERALD][doors] ${doors.length} portas carregadas.`);
}

export function updateDoors(dt) {
  if (doors.length === 0) return;
  const pos = getPlayerPos();

  for (const d of doors) {
    const wp = new THREE.Vector3();
    d.pivot.getWorldPosition(wp);
    const dx = pos.x - wp.x;
    const dz = pos.z - wp.z;
    const dist = Math.hypot(dx, dz);

    const target = dist < OPEN_DIST ? 1 : 0;

    if (d.current < target) {
      d.current = Math.min(1, d.current + ANIM_SPEED * dt);
    } else if (d.current > target) {
      d.current = Math.max(0, d.current - ANIM_SPEED * dt);
    }

    // Aplica rotação
    d.pivot.rotation.y = d.closedAngle + d.current * (d.openAngle - d.closedAngle);

    // Colisão desabilitada quando > 50% aberta (mas NÃO reativa sobre o jogador)
    const shouldDisable = d.current > 0.5 || dist < OPEN_DIST + 0.4;
    if (shouldDisable !== d.colliderDisabled) {
      d.colliderDisabled = shouldDisable;
      setDoorColliderDisabled(d.doorId, shouldDisable);
    }
  }
}