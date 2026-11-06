import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { clone as cloneSkeleton } from 'three/addons/utils/SkeletonUtils.js';
import { NPCPathfinding } from './NPCPathfinding.js';
import { NPCController } from './NPCController.js';

const CHILD_COLORS  = [0xe74c3c, 0x3498db, 0xf39c12, 0x2ecc71, 0x9b59b6, 0xe67e22];
const TEACHER_COLOR = 0x2c3e50;
const AIDE_COLOR    = 0xf1c40f;
const COOK_COLOR    = 0xf5f5f5;
const SUPER_COLOR   = 0x27ae60;

export class NPCManager {
    constructor(scene) {
        this.scene = scene;
        this.npcs = [];
        this.pathfinder = null;
        this.roles = null;
        this.testModelURL = 'https://threejs.org/examples/models/gltf/Soldier.glb';
        this.loadedAssets = null;
    }

    async init() {
        const [routesRes, rolesRes] = await Promise.all([
            fetch('./data/npc_routes.json'),
            fetch('./data/npc_roles.json')
        ]);
        this.pathfinder = new NPCPathfinding(await routesRes.json());
        this.roles = (await rolesRes.json()).roles;

        const loader = new GLTFLoader();
        await new Promise((resolve, reject) => {
            loader.load(this.testModelURL, (gltf) => {
                this.loadedAssets = gltf;
                gltf.scene.traverse(child => {
                    if (child.isMesh) { child.castShadow = true; child.receiveShadow = true; }
                });
                this.spawnPopulation();
                resolve();
            }, undefined, reject);
        });
    }

    spawnPopulation() {
        // ---- 6 crianças ----
        const childPositions = [
            [3, 0, 0], [8, 0, 0], [14, 0, 0], [20, 0, 0], [28, 0, 0], [8, 0, -11]
        ];
        childPositions.forEach((pos, i) => {
            this.spawnNPC(pos[0], pos[1], pos[2], 'child', CHILD_COLORS[i % CHILD_COLORS.length]);
        });

        // ---- 5 adultos ----
        // 2 professores em salas
        this.spawnNPC(4.5, 0, -3.0, 'teacher', TEACHER_COLOR);
        this.spawnNPC(18.5, 0, -3.0, 'teacher', TEACHER_COLOR);
        // 1 auxiliar acompanhando crianças no parque
        this.spawnNPC(5, 0, -17, 'aide', AIDE_COLOR);
        // 1 cozinheira na cozinha (posição corrigida: z positivo)
        this.spawnNPC(21.5, 0, 3.5, 'cook', COOK_COLOR);
        // 1 supervisor de parque
        this.spawnNPC(8, 0, -18, 'playground_supervisor', SUPER_COLOR);
    }

    spawnNPC(x, y, z, roleId, colorHex) {
        if (!this.loadedAssets) return;
        const role = this.roles[roleId];
        if (!role) {
            console.warn(`[NPC] papel desconhecido: ${roleId}`);
            return;
        }

        const model = cloneSkeleton(this.loadedAssets.scene);
        model.position.set(x, y, z);
        model.scale.setScalar(role.scale);

        if (colorHex !== undefined) {
            model.traverse(child => {
                if (child.isMesh && child.material) {
                    const mats = Array.isArray(child.material) ? child.material : [child.material];
                    mats.forEach(m => {
                        if (m.color && !m.userData.__tinted) {
                            m.color = new THREE.Color(colorHex);
                            m.userData.__tinted = true;
                        }
                    });
                }
            });
        }

        this.scene.add(model);

        const mixer = new THREE.AnimationMixer(model);
        const actions = {};
        for (const clip of this.loadedAssets.animations) {
            actions[clip.name] = mixer.clipAction(clip);
        }
        if (actions['Idle']) actions['Idle'].play();

        const controller = new NPCController(model, mixer, actions, this.pathfinder, role, { label: roleId });
        controller.roleId = roleId;
        this.npcs.push(controller);

        console.log(`[NPC] ${role.displayName} → (${x.toFixed(1)}, ${z.toFixed(1)})`);
    }

    update(dt) {
        for (const npc of this.npcs) npc.update(dt);
    }
}