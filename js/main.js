// js/main.js — P03
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

    const model = await loadModel('./assets/EMERALD_SCHOOL.glb', setProgress);
    addToScene(model);
    window.__emerald_model = model;
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

    // Clique: selecionar marcador (se Pointer Lock não estiver ativo)
    document.addEventListener('click', e => {
      if (document.pointerLockElement) return;  // durante o lock, clique não interage com DOM
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
  // waypoint = [x, y, z] em coords Web
  import('./player.js').then(({ getPlayerPos }) => {
    const p = getPlayerPos();
    p.x = waypoint[0];
    p.z = waypoint[2];
    // y é altura de piso; mantemos altura do olho (1.7)
    console.log(`[EMERALD] teleport demonstrativo → (${p.x.toFixed(2)}, ${p.z.toFixed(2)})`);
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