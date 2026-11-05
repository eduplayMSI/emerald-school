import * as THREE from 'three'; // IMPORTAÇÃO ESSENCIAL AQUI
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

    // Cache-buster atualizado para ?v=8
    const model = await loadModel('./assets/EMERALD_SCHOOL.glb?v=8', setProgress);
    addToScene(model);
    window.__emerald_model = model;

    // FORÇAR COR DO PISO (À PROVA DE FALHAS)
    const floorColors = [
        { match: 'floor_corridor', color: 0xD1C6B4 },
        { match: 'floor_spc_class', color: 0xC9A882 },
        { match: 'floor_spc_berc', color: 0xFAFAFA },
        { match: 'floor_spc_wc', color: 0x9CA3A8 },
        { match: 'floor_spc_kitchen', color: 0x9CA3A8 },
        { match: 'floor_spc_cafe', color: 0xBFC9CE },
        { match: 'floor_patio', color: 0xB84D47 }
    ];

    model.traverse(child => {
        if (!child.isMesh) return;
        const name = child.name.toLowerCase();
        const match = floorColors.find(f => name.includes(f.match));
        if (match) {
            child.material = new THREE.MeshStandardMaterial({
                color: match.color,
                roughness: 0.65,
                metalness: 0.0
            });
        }
    });

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