import * as THREE from 'three';

export class NPCController {
    constructor(model, mixer, actions, pathfinder, roleConfig, options = {}) {
        this.model = model;
        this.mixer = mixer;
        this.actions = actions;
        this.pathfinder = pathfinder;
        this.role = roleConfig;
        this.label = options.label || 'NPC';

        this.state = 'IDLE';
        this.speed = this.role.speed || 1.2;
        this.currentPath = [];
        this.pathIndex = 0;
        this.timer = Math.random() * 2;
        this.lastDestNodeId = null;
        this.currentActivity = null;

        if (this.actions['Idle']) this.actions['Idle'].play();
    }

    update(dt) {
        this.mixer.update(dt);

        if (this.state === 'IDLE') {
            this.timer -= dt;
            if (this.timer <= 0) this.pickNewDestination();
        } else if (this.state === 'WALKING') {
            this.followPath(dt);
        } else if (this.state === 'ACTIVITY') {
            this.timer -= dt;
            if (this.timer <= 0) {
                this.state = 'IDLE';
                this.timer = randRange(this.role.idleTime);
                this.playAnimation('Idle');
            }
        }
    }

    pickNewDestination() {
        const startId = this.pathfinder.findNearestNode(this.model.position, this.role.allowedZones);
        if (!startId) { this.timer = 2; return; }

        const preferred = pickPreferredZones(this.role);
        let targetId = this.pathfinder.getRandomNode(
            this.role.allowedZones,
            Math.random() < 0.8 ? preferred : null
        );

        if (!targetId) { this.timer = 2; return; }

        let safety = 0;
        while (targetId === this.lastDestNodeId && safety < 8) {
            targetId = this.pathfinder.getRandomNode(this.role.allowedZones, preferred);
            safety++;
        }
        this.lastDestNodeId = targetId;

        const path = this.pathfinder.findPath(startId, targetId, this.role.allowedZones);
        if (path && path.length > 0) {
            this.currentPath = path;
            this.pathIndex = 0;
            this.state = 'WALKING';

            const targetZone = this.pathfinder.nodes[targetId].zone;
            const canRun = targetZone === 'playground'
                && this.role.allowedZones.includes('playground')
                && this.role.scale < 0.8  // só crianças correm
                && Math.random() < 0.4;
            this.currentActivity = { zone: targetZone, run: canRun };

            this.playAnimation(canRun ? 'Run' : 'Walk');
            this.speed = canRun ? this.role.runSpeed : this.role.speed;
        } else {
            this.timer = 1 + Math.random() * 2;
        }
    }

    followPath(dt) {
        if (this.pathIndex >= this.currentPath.length) {
            this.onArrival();
            return;
        }
        const target = this.currentPath[this.pathIndex];
        const pos = this.model.position;
        const dx = target.x - pos.x, dz = target.z - pos.z;
        const dist = Math.hypot(dx, dz);

        if (dist < 0.15) { this.pathIndex++; return; }

        const step = this.speed * dt;
        const moveX = (dx / dist) * step;
        const moveZ = (dz / dist) * step;
        pos.x += moveX;
        pos.z += moveZ;

        const angle = Math.atan2(moveX, moveZ);
        const targetQ = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), angle);
        this.model.quaternion.slerp(targetQ, 0.15);
    }

    onArrival() {
        const act = this.currentActivity || { zone: 'corridor' };
        const pool = (this.role.activityPool && this.role.activityPool[act.zone]) || ['idle'];
        const activity = pool[Math.floor(Math.random() * pool.length)];

        // Mapeia atividade → animação disponível no placeholder
        const animMap = {
            'idle': 'Idle', 'walk': 'Idle', 'run': 'Idle', 'sit': 'Idle',
            'drink': 'Idle', 'play': 'Idle', 'work': 'Idle',
            'supervise': 'Idle', 'talk': 'Idle', 'serve': 'Idle'
        };
        this.playAnimation(animMap[activity] || 'Idle');
        this.state = 'ACTIVITY';
        this.timer = randRange(this.role.activityTime);
    }

    playAnimation(name) {
        if (!this.actions[name]) return;
        if (this.actions[name].isRunning()) return;
        for (const k in this.actions) this.actions[k].fadeOut(0.25);
        this.actions[name].reset().fadeIn(0.25).play();
    }
}

function randRange([min, max]) { return min + Math.random() * (max - min); }

function pickPreferredZones(role) {
    // FIX P25: respeita role.preferredZones quando definido
    if (role.preferredZones && role.preferredZones.length > 0) {
        return role.preferredZones.filter(z => role.allowedZones.includes(z));
    }
    const pref = [];
    if (role.allowedZones.includes('corridor'))   pref.push('corridor');
    if (role.allowedZones.includes('playground')) pref.push('playground');
    if (role.allowedZones.includes('classroom'))  pref.push('classroom');
    if (role.allowedZones.includes('fountain'))   pref.push('fountain');
    return pref.length > 0 ? pref : role.allowedZones;
}