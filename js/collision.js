import * as THREE from 'three';
import { getPlayerPos } from './player.js';

const PLAYER_RADIUS = 0.28;
const PLAYER_EYE = 1.7;

const colliders = [];   // { box: THREE.Box3, disabled: false }

export function initCollision() {
  colliders.length = 0;
}

export function addCollidersFromModel(model) {
  model.traverse(obj => {
    if (!obj.isMesh) return;
    if (!obj.name.startsWith('COLLIDER_')) return;

    obj.updateWorldMatrix(true, false);
    const geom = obj.geometry;
    if (!geom.boundingBox) geom.computeBoundingBox();
    const box = geom.boundingBox.clone();
    box.applyMatrix4(obj.matrixWorld);

    const entry = { box, disabled: false, mesh: obj };
    colliders.push(entry);

    // ocultar visualmente o colisor
    obj.visible = false;
  });
  console.log(`[EMERALD][collision] ${colliders.length} colisores extraídos.`);
}

export function setDoorColliderDisabled(doorId, disabled) {
  for (const c of colliders) {
    if (c.mesh?.userData?.emerald_door_id === doorId) {
      c.disabled = disabled;
    }
  }
}

export function resolveCollisions() {
  const pos = getPlayerPos();
  const pr = PLAYER_RADIUS;

  for (const c of colliders) {
    if (c.disabled) continue;

    const b = c.box;
    // Só colide se o colisor intersecta a faixa vertical do jogador
    if (b.max.y <= 0.05) continue;
    if (b.min.y >= PLAYER_EYE + 0.1) continue;

    // AABB 2D (plano XZ)
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