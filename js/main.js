import * as THREE from 'three'; // Importação essencial
import { initScene, loadModel, addToScene, startRenderLoop, bindResize, getCamera, getScene } from './scene.js';
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

    // Cache-buster ?v=10 para forçar o navegador a baixar o novo código
    const model = await loadModel('./assets/EMERALD_SCHOOL.glb?v=10', setProgress);
    addToScene(model);
    window.__emerald_model = model;

    console.group("[EMERALD] Correção de Normais (Piso)");
    model.traverse(child => {
        if (child.isMesh && child.name.toLowerCase().includes('floor')) {
            // Força a renderização frente e verso para consertar normais invertidas
            child.material.side = THREE.DoubleSide;
            console.log(`Objeto: ${child.name} | Material: ${child.material.name} | DoubleSide: ATIVADO`);
        }
    });
    console.groupEnd();

    enableShadows(model);
    addCollidersFromModel(model);
    initDoors(model);

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
      updateDoors(dt);
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