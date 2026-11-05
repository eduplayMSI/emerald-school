import * as THREE from 'three';

const START_POS = new THREE.Vector3(-4, 1.7, 0);
const START_YAW = -Math.PI / 2;   // olha para +X (fachada leste)
const START_PITCH = 0;

const MOVE_SPEED = 4.2;
const SPRINT_MUL = 1.9;
const MOUSE_SENS = 0.0022;
const PLAYER_HEIGHT = 1.7;

const keys = Object.create(null);
const pos = START_POS.clone();
let yaw = START_YAW;
let pitch = START_PITCH;
let locked = false;
let camera, domEl;

export function initPlayer() {
  camera = document.querySelector('canvas') ? null : null; // preenchido abaixo
  // Usa o canvas criado pelo scene.js
  domEl = document.body;

  // Camera
  import('./scene.js').then(({ getCamera }) => {
    camera = getCamera();
    applyToCamera();
  });

  window.addEventListener('keydown', e => { keys[e.code] = true; });
  window.addEventListener('keyup',   e => { keys[e.code] = false; });

  document.addEventListener('pointerlockchange', () => {
    locked = document.pointerLockElement === document.body ||
             document.pointerLockElement instanceof HTMLElement;
  });

  document.addEventListener('mousemove', e => {
    if (!locked) return;
    yaw   -= e.movementX * MOUSE_SENS;
    pitch -= e.movementY * MOUSE_SENS;
    const lim = Math.PI / 2 - 0.01;
    if (pitch >  lim) pitch =  lim;
    if (pitch < -lim) pitch = -lim;
  });

  document.addEventListener('click', () => {
    if (!locked) document.body.requestPointerLock();
  });

  document.addEventListener('keydown', e => {
    if (e.code === 'Escape' && locked) document.exitPointerLock();
    if (e.code === 'KeyR') resetPosition();
  });
}

function applyToCamera() {
  if (!camera) return;
  camera.position.copy(pos);
  camera.rotation.order = 'YXZ';
  camera.rotation.y = yaw;
  camera.rotation.x = pitch;
}

export function updatePlayer(dt) {
  if (!camera) return;

  const sprint = keys['ShiftLeft'] || keys['ShiftRight'] ? SPRINT_MUL : 1;
  const speed = MOVE_SPEED * sprint * dt;

  const fwd = new THREE.Vector3(-Math.sin(yaw), 0, -Math.cos(yaw));
  const right = new THREE.Vector3(Math.cos(yaw), 0, -Math.sin(yaw));

  const move = new THREE.Vector3();
  if (keys['KeyW'] || keys['ArrowUp'])    move.add(fwd);
  if (keys['KeyS'] || keys['ArrowDown'])  move.sub(fwd);
  if (keys['KeyA'] || keys['ArrowLeft'])  move.sub(right);
  if (keys['KeyD'] || keys['ArrowRight']) move.add(right);

  if (move.lengthSq() > 0) {
    move.normalize().multiplyScalar(speed);
    pos.x += move.x;
    pos.z += move.z;
  }

  camera.position.copy(pos);
  camera.rotation.order = 'YXZ';
  camera.rotation.y = yaw;
  camera.rotation.x = pitch;
}

export function getPlayerPos() { return pos; }
export function getPlayerYaw() { return yaw; }
export function resetPosition() {
  pos.copy(START_POS);
  yaw = START_YAW;
  pitch = START_PITCH;
  applyToCamera();
}
export function setPointerLocked(v) { locked = v; }
export const PLAYER_EYE = PLAYER_HEIGHT;