import { initScene, loadModel, addToScene, startRenderLoop, bindResize } from './scene.js';
import { initPlayer, updatePlayer, getPlayerPos } from './player.js';
import { initCollision, addCollidersFromModel, resolveCollisions } from './collision.js';
import { initDoors, updateDoors } from './doors.js';
import { setProgress, showStartButton, hideLoading, hideControlsInfo, showControlsInfo, showError } from './interface.js';

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
    showStartButton(() => {
      hideLoading();
      showControlsInfo();
    });

    bindResize();

    // loop
    const clock = { last: performance.now() };
    function frame(now) {
      const dt = Math.min(0.05, (now - clock.last) / 1000);
      clock.last = now;

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