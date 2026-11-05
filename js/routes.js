// js/routes.js — P03
import * as THREE from 'three';

const COLOR_OK = 0x2ecc71;
const COLOR_HAZARD = 0xf39c12;
const COLOR_BLOCKED = 0xe74c3c;
const COLOR_SELECTED = 0x00bcd4;

let routesData = null;
let routeGroup = null;
let scene = null;
let activeRouteId = null;
const routeObjects = new Map();  // id -> { tube, markers[] }

export async function initRoutes(sceneRef) {
  scene = sceneRef;
  routeGroup = new THREE.Group();
  routeGroup.name = 'ROUTE_GROUP';
  scene.add(routeGroup);

  try {
    const res = await fetch('./data/routes.json');
    if (!res.ok) throw new Error(`routes.json HTTP ${res.status}`);
    routesData = await res.json();
    console.log(`[EMERALD][routes] ${routesData.routes.length} rotas carregadas.`);
  } catch (e) {
    console.error('[EMERALD][routes] falha ao carregar JSON:', e);
    routesData = { routes: [] };
  }
  buildRoutes();
}

function routeColor(route) {
  if (route.estado?.startsWith('INTERRUPTED')) return COLOR_BLOCKED;
  const hasHazard = (route.hazards_related || []).length > 0;
  return hasHazard ? COLOR_HAZARD : COLOR_OK;
}

function buildRoutes() {
  for (const route of routesData.routes) {
    const pts = route.waypoints.map(w => new THREE.Vector3(w[0], w[1], w[2]));
    if (pts.length < 2) continue;
    const curve = new THREE.CatmullRomCurve3(pts, false, 'catmullrom', 0.0);
    const geom = new THREE.TubeGeometry(curve, pts.length * 12, 0.08, 8, false);
    const mat = new THREE.MeshBasicMaterial({
      color: routeColor(route), transparent: true, opacity: 0.85, depthWrite: false
    });
    const tube = new THREE.Mesh(geom, mat);
    tube.name = `ROUTE_TUBE_${route.id}`;
    tube.userData = { kind: 'route', routeId: route.id };
    tube.renderOrder = 2;
    tube.visible = false;
    routeGroup.add(tube);

    // Origem / destino (esferas)
    const origin = new THREE.Mesh(
      new THREE.SphereGeometry(0.15, 12, 8),
      new THREE.MeshBasicMaterial({ color: 0x2ecc71 })
    );
    origin.position.copy(pts[0]);
    origin.visible = false;
    origin.userData = { kind: 'route-origin', routeId: route.id };
    routeGroup.add(origin);

    const dest = new THREE.Mesh(
      new THREE.SphereGeometry(0.15, 12, 8),
      new THREE.MeshBasicMaterial({ color: 0xe74c3c })
    );
    dest.position.copy(pts[pts.length - 1]);
    dest.visible = false;
    dest.userData = { kind: 'route-dest', routeId: route.id };
    routeGroup.add(dest);

    routeObjects.set(route.id, { tube, origin, dest, meta: route });
  }
}

export function setRouteVisible(id, visible) {
  const obj = routeObjects.get(id);
  if (!obj) return;
  obj.tube.visible = visible;
  obj.origin.visible = visible;
  obj.dest.visible = visible;
}

export function hideAllRoutes() {
  for (const obj of routeObjects.values()) {
    obj.tube.visible = false;
    obj.origin.visible = false;
    obj.dest.visible = false;
  }
}

export function showAllRoutes() {
  for (const obj of routeObjects.values()) {
    obj.tube.visible = true;
    obj.origin.visible = true;
    obj.dest.visible = true;
  }
}

export function selectRoute(id) {
  hideAllRoutes();
  activeRouteId = id;
  const obj = routeObjects.get(id);
  if (!obj) return null;
  obj.tube.visible = true;
  obj.origin.visible = true;
  obj.dest.visible = true;
  obj.tube.material.color.setHex(COLOR_SELECTED);
  obj.tube.material.opacity = 1.0;
  // Restaurar cores das outras
  for (const [oid, o] of routeObjects) {
    if (oid !== id) {
      o.tube.material.color.setHex(routeColor(o.meta));
      o.tube.material.opacity = 0.85;
    }
  }
  return obj.meta;
}

export function clearRouteSelection() {
  activeRouteId = null;
  hideAllRoutes();
  for (const o of routeObjects.values()) {
    o.tube.material.color.setHex(routeColor(o.meta));
    o.tube.material.opacity = 0.85;
  }
}

export function getActiveRouteId() { return activeRouteId; }
export function getRoutes() { return routesData?.routes || []; }
export function getRouteById(id) { return routesData?.routes.find(r => r.id === id); }