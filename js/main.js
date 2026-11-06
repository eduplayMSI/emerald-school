import * as THREE from 'three';
import { initScene, loadModel, addToScene, startRenderLoop, bindResize, getCamera, getScene } from './scene.js';
import { NPCManager } from './npc/NPCManager.js';
import { initLighting } from './lighting.js';
import { initPlayer, updatePlayer, resetPosition } from './player.js';
import { initCollision, addCollidersFromModel, resolveCollisions } from './collision.js';
import { initDoors, updateDoors } from './doors.js';
import {
  setProgress, showStartButton, hideLoading, showControlsInfo, showError,
  initLayerPanel, initModeToggle, showMarkerPanel, hideMarkerPanel, setTeleportHandler
} from './interface.js';
import { initRoutes, getActiveRouteId } from './routes.js';
import { initMarkers, pick } from './markers.js';
import { initHUD, updateHUD } from './hud.js';
import { initMinimap, drawMinimap } from './minimap.js';

async function bootstrap() {
  try {
    initScene();
    initPlayer();
    initCollision();

    // Cache-buster ?v=11
// js/main.js
const model = await loadModel('./assets/EMERALD_SCHOOL.glb?v=14', setProgress);
    addToScene(model);
    window.__emerald_model = model;

    console.group("[EMERALD] Auditoria de Materiais (P19)");
    model.traverse(child => {
        if (child.isMesh && child.name.toLowerCase().includes('floor')) {
            const matName = child.material.name || "Sem Nome";
            console.log(`Objeto: ${child.name} | Material: ${matName}`);
        }
    });
    console.groupEnd();

    enableShadows(model);
    addCollidersFromModel(model);
    initDoors(model);

    await initLighting(getScene());
    
    const npcManager = new NPCManager(getScene());
    await npcManager.init();
    
    await initRoutes(getScene());
    await initMarkers(getScene());
    await initHUD();
    await initMinimap();

    initLayerPanel();
    initModeToggle();
    setTeleportHandler(handleTeleport);

    hideLoading();
    showStartButton(() => showControlsInfo());
    bindResize();

    document.addEventListener('click', e => {
      if (document.pointerLockElement) return;
      const hit = pick(e.clientX, e.clientY, getCamera());
      if (hit) showMarkerPanel(hit.payload, hit.kind);
    });

    let last = performance.now();
    function frame(now) {
      const dt = Math.min(0.05, (now - last) / 1000);
      last = now;
      updatePlayer(dt);
      resolveCollisions();
      npcManager.update(dt);
      
      // Coleta posições dos NPCs para as portas
      const npcPositions = npcManager.npcs.map(n => n.model.position);
      updateDoors(dt, npcPositions);
      updateHUD();
      drawMinimap(getActiveRouteId());
      startRenderLoop();
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  } catch (err) {
    console.error('[EMERALD] Erro fatal:', err);
    showError(err?.message || 'Falha ao carregar.');
  }
}

function handleTeleport(waypoint) {
  import('./player.js').then(({ getPlayerPos }) => {
    const p = getPlayerPos();
    p.x = waypoint[0];
    p.z = waypoint[2];
  });
}

function enableShadows(model) {
  model.traverse(o => {
    if (o.isMesh && !o.name.startsWith('COLLIDER_')) {
      o.castShadow = true; o.receiveShadow = true;
    }
  });
}

bootstrap();