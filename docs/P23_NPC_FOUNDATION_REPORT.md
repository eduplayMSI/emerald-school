# P23 — Relatório de Fundação de NPCs

**Estado:** `NPC_FOUNDATION_VERIFIED`

## 1. Arquitetura
O sistema foi construído de forma modular e escalável:
- **`NPCPathfinding.js`**: Grafo A* (Dijkstra). Lê `data/npc_routes.json`. Encontra o caminho mais curto entre dois pontos, respeitando os cantos e corredores.
- **`NPCController.js`**: Máquina de estados. Alterna entre `IDLE` (espera de 2 a 7 segundos) e `WALKING` (segue o path). A rotação do modelo é interpolada via `Quaternion.slerp` para não haver "snap" de 180 graus.
- **`NPCManager.js`**: Carrega o modelo via `GLTFLoader`, clona usando `SkeletonUtils.clone` (crucial para múltiplos NPCs com animação) e injeta o `AnimationMixer` individual.

## 2. Modelo de Teste
Como o projeto não possui um personagem riggado ainda, utilizei o `Soldier.glb` oficial do Three.js (`https://threejs.org/examples/models/gltf/Soldier.glb`). Ele já possui animações de `Idle` e `Walk`, perfeitas para validar o sistema de `AnimationMixer` e o clone de esqueletos.

## 3. Navegação e Portas
- O NPC não atravessa paredes. Ele segue o grafo de navegação (`npc_routes.json`).
- **Portas Automáticas**: O módulo `doors.js` foi atualizado para receber um array de posições. Agora, tanto o jogador quanto os NPCs fazem as portas abrirem quando passam perto.

## 4. O que NÃO foi feito nesta etapa
- Modelos de crianças e adultos reais (isso fica para P24/P25).
- Comportamentos complexos (sentar, interagir com mobiliário). A máquina de estados está preparada, mas só tem `IDLE` e `WALKING`.
- Pathfinding dinâmico evitando obstáculos móveis (o grafo é estático, o que é aceitável para o corredor).

## 5. Como Testar
1. Abra o navegador (`localhost:8000`).
2. Olhe para o corredor principal. Você verá 2 bonecos (Soldier) se movendo para frente e para trás.
3. Se eles passarem por uma porta, a porta abrirá automaticamente para eles.
4. Tente obstruir o caminho deles (eles vão atravessar o jogador, pois a colisão jogador-NPC será implementada em P24).