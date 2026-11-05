import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

let scene, camera, renderer;

export function initScene() {
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x9cc8e4);
  scene.fog = new THREE.Fog(0x9cc8e4, 60, 220);

  camera = new THREE.PerspectiveCamera(72, window.innerWidth / window.innerHeight, 0.1, 500);
  camera.position.set(-4, 1.7, 0);
  camera.rotation.order = 'YXZ';

  renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  document.body.appendChild(renderer.domElement);

  // Luz solar nordestina
  const sun = new THREE.DirectionalLight(0xFFF4E0, 2.4);
  sun.position.set(40, 70, 25);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.camera.left = -60;
  sun.shadow.camera.right = 60;
  sun.shadow.camera.top = 60;
  sun.shadow.camera.bottom = -60;
  sun.shadow.camera.near = 0.5;
  sun.shadow.camera.far = 200;
  scene.add(sun);

  const hemi = new THREE.HemisphereLight(0xBEE3FF, 0x8B7355, 0.7);
  scene.add(hemi);

  const amb = new THREE.AmbientLight(0xffffff, 0.25);
  scene.add(amb);

  // chão de teste (o GLB traz o seu próprio, isto fica por baixo)
  const groundMat = new THREE.MeshStandardMaterial({ color: 0x6e8b4a, roughness: 0.95 });
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(400, 400), groundMat);
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -0.05;
  ground.receiveShadow = true;
  scene.add(ground);

  return scene;
}

export function bindResize() {
  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
}

export function loadModel(url, onProgress) {
  return new Promise((resolve, reject) => {
    const loader = new GLTFLoader();
    loader.load(url,
      gltf => resolve(gltf.scene),
      evt => { if (evt.total) onProgress(evt.loaded / evt.total); },
      err => reject(new Error(`Falha ao carregar GLB: ${err?.message || err}`))
    );
  });
}

export function addToScene(obj) { scene.add(obj); }
export function startRenderLoop() { renderer.render(scene, camera); }
export function getScene() { return scene; }
export function getCamera() { return camera; }
export function getRenderer() { return renderer; }