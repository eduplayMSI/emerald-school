// js/main.js — versão P01 (50 linhas, sem classList, sem animate global)
import { initScene, loadModel, addToScene, startRenderLoop, bindResize } from './scene.js';
import { initPlayer, updatePlayer } from './player.js';
import { initCollision, addCollidersFromModel, resolveCollisions } from './collision.js';
import { initDoors, updateDoors } from './doors.js';
import { setProgress, showStartButton, hideLoading, showControlsInfo, showError } from './interface.js';

async function bootstrap() {
  try {
    initScene();
    initPlayer();
    initCollision();

    const model = await loadModel('./assets/EMERALD_SCHOOL.glb', setProgress);

    addToScene(model);
    enableShadows(model);
    addCollidersFromModel(model);
    initDoors(model);

    hideLoading();
    showStartButton(() => showControlsInfo());
    bindResize();

    let last = performance.now();
    function frame(now) {
      const dt = Math.min(0.05, (now - last) / 1000);
      last = now;
      updatePlayer(dt);
      resolveCollisions();
      updateDoors(dt);
      startRenderLoop();
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  } catch (err) {
    console.error('[EMERALD] Erro fatal:', err);
    showError(err?.message || 'Falha ao carregar o modelo 3D.');
  }
}

function enableShadows(model) {
  model.traverse(o => {
    if (o.isMesh && !o.name.startsWith('COLLIDER_')) {
      o.castShadow = true;
      o.receiveShadow = true;
    }
  });
}

bootstrap();