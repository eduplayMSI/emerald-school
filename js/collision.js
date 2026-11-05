// js/collision.js — P02 (casamento robusto de colisores de porta)
import * as THREE from 'three';
import { getPlayerPos } from './player.js';

const PLAYER_RADIUS = 0.28;
const PLAYER_EYE = 1.7;

const colliders = [];   // { box, disabled, mesh, tag }

export function initCollision() {
  colliders.length = 0;
}

export function addCollidersFromModel(model) {
  let total = 0, doors = 0;
  model.traverse(obj => {
    if (!obj.isMesh) return;
    if (!obj.name.startsWith('COLLIDER_')) return;

    obj.updateWorldMatrix(true, false);
    const geom = obj.geometry;
    if (!geom.boundingBox) geom.computeBoundingBox();
    const box = geom.boundingBox.clone();
    box.applyMatrix4(obj.matrixWorld);

    const isDoor = obj.name.startsWith('COLLIDER_DOOR_');
    if (isDoor) doors++;

    colliders.push({
      box,
      disabled: false,
      mesh: obj,
      tag: isDoor ? 'door' : 'solid',
    });

    obj.visible = false;
    total++;
  });
  console.log(`[EMERALD][collision] ${total} colisores (${doors} de porta).`);
}

/**
 * Desativa/ativa o colisor de uma porta.
 * Casa por (1) userData.emerald_door_id OU (2) prefixo de nome.
 * O fallback por nome é o que garante o funcionamento em todos os GLBs.
 */
export function setDoorColliderDisabled(doorId, disabled) {
  const tag = `COLLIDER_DOOR_${doorId}`;
  let hits = 0;
  for (const c of colliders) {
    if (!c.mesh) continue;
    const ud = c.mesh.userData || {};
    const nm = c.mesh.name || '';
    const byProp = ud.emerald_door_id === doorId;
    const byName = nm === tag || nm.startsWith(tag);
    if (byProp || byName) {
      c.disabled = disabled;
      hits++;
    }
  }
  if (hits === 0 && disabled) {
    // Só avisa quando estamos tentando abrir — evita spam
    console.warn(`[EMERALD][collision] colisor não encontrado: "${tag}"`);
  }
  return hits;
}

export function resolveCollisions() {
  const pos = getPlayerPos();
  const pr = PLAYER_RADIUS;

  for (const c of colliders) {
    if (c.disabled) continue;

    const b = c.box;
    if (b.max.y <= 0.05) continue;
    if (b.min.y >= PLAYER_EYE + 0.1) continue;

    const minX = b.min.x - pr;
    const maxX = b.max.x + pr;
    const minZ = b.min.z - pr;
    const maxZ = b.max.z + pr;

    if (pos.x > minX && pos.x < maxX && pos.z > minZ && pos.z < maxZ) {
      const dxL = pos.x - minX;
      const dxR = maxX - pos.x;
      const dzL = pos.z - minZ;
      const dzR = maxZ - pos.z;
      const m = Math.min(dxL, dxR, dzL, dzR);

      if (m === dxL) pos.x = minX - 0.001;
      else if (m === dxR) pos.x = maxX + 0.001;
      else if (m === dzL) pos.z = minZ - 0.001;
      else pos.z = maxZ + 0.001;
    }
  }
}