import * as THREE from 'three';

export class NPCPathfinding {
    constructor(data) {
        this.nodes = {};
        this.adj = {};
        for (const n of data.nodes) {
            this.nodes[n.id] = { id: n.id, pos: new THREE.Vector3(...n.pos), zone: n.zone || 'corridor' };
            this.adj[n.id] = [];
        }
        for (const e of data.edges) {
            this.adj[e.from].push({ id: e.to, type: e.type });
            this.adj[e.to].push({ id: e.from, type: e.type });
        }
    }

    isZoneAllowed(nodeId, allowedZones) {
        const node = this.nodes[nodeId];
        if (!node) return false;
        return allowedZones.includes(node.zone);
    }

    findPath(startId, endId, allowedZones) {
        if (!this.nodes[startId] || !this.nodes[endId]) return null;
        if (!this.isZoneAllowed(endId, allowedZones)) return null;
        if (startId === endId) return [this.nodes[startId].pos.clone()];

        const distances = {}, prev = {}, queue = [];
        for (const id in this.nodes) { distances[id] = Infinity; prev[id] = null; queue.push(id); }
        distances[startId] = 0;

        while (queue.length > 0) {
            queue.sort((a, b) => distances[a] - distances[b]);
            const u = queue.shift();
            if (u === endId) {
                const path = [];
                let curr = endId;
                while (curr) { path.unshift(this.nodes[curr].pos.clone()); curr = prev[curr]; }
                return path;
            }
            if (distances[u] === Infinity) break;

            for (const v of this.adj[u]) {
                if (!this.isZoneAllowed(v.id, allowedZones)) continue;
                const alt = distances[u] + this.nodes[u].pos.distanceTo(this.nodes[v.id].pos);
                if (alt < distances[v.id]) { distances[v.id] = alt; prev[v.id] = u; }
            }
        }
        return null;
    }

    findNearestNode(position, allowedZones) {
        let bestId = null, bestDist = Infinity;
        for (const id in this.nodes) {
            if (!this.isZoneAllowed(id, allowedZones)) continue;
            const d = this.nodes[id].pos.distanceTo(position);
            if (d < bestDist) { bestDist = d; bestId = id; }
        }
        return bestId;
    }

    getRandomNode(allowedZones, preferredZones = null) {
        const ids = Object.keys(this.nodes).filter(id => this.isZoneAllowed(id, allowedZones));
        if (ids.length === 0) return null;
        const pool = preferredZones
            ? ids.filter(id => preferredZones.includes(this.nodes[id].zone))
            : ids;
        const final = pool.length > 0 ? pool : ids;
        return final[Math.floor(Math.random() * final.length)];
    }
}