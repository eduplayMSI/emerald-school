import * as THREE from 'three';
import { RectAreaLightUniformsLib } from 'three/addons/lights/RectAreaLightUniformsLib.js';

export async function initLighting(scene) {
    try {
        RectAreaLightUniformsLib.init();

        const response = await fetch('./data/lighting_manifest.json');
        const data = await response.json();

        if (!data || !data.lights || !Array.isArray(data.lights)) {
            throw new Error("Manifesto inválido: array 'lights' não encontrado.");
        }

        console.group("[EMERALD] Iluminação P21");
        let pointCount = 0;
        let areaCount = 0;

        for (const lightData of data.lights) {
            // FILTRO: Ignora luzes externas (desligadas) ou de intensidade zero
            if (lightData.category === 'external' || lightData.intensity <= 0) {
                console.log(`Luz externa/desligada ignorada: ${lightData.id}`);
                continue;
            }

            let light;
            const color = new THREE.Color(lightData.color);
            const [x, y, z] = lightData.pos; 

            if (lightData.type === 'point') {
                light = new THREE.PointLight(color, lightData.intensity, lightData.distance, 2);
                light.position.set(x, y, z);
                pointCount++;
            } 
            else if (lightData.type === 'area') {
                light = new THREE.RectAreaLight(color, lightData.intensity, 1.5, 1.5);
                light.position.set(x, y, z);
                light.lookAt(x, y - 1, z); 
                areaCount++;
            }

            if (light) {
                light.name = lightData.id;
                scene.add(light);
            }
        }
        console.log(`Luzes ativas: ${pointCount} PointLights, ${areaCount} RectAreaLights.`);
        console.groupEnd();
    } catch (error) {
        console.warn("[EMERALD] Falha ao carregar iluminação interna.", error);
    }
}