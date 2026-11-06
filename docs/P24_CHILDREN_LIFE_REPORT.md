# P24 — Relatório de Crianças Virtuais

**Estado:** `CHILDREN_NPCS_PARTIALLY_VERIFIED`

## 1. O que foi implementado (funcional)

- **6 crianças + 1 adulto** spawnados.
- **Escala infantil** (65% do Soldier = ~1.1m — compatível com mesas de 0,50m, bebedouro de 1m, maçanetas a 1,05m).
- **Variação de cor de roupa** (6 cores, sem duplicação).
- **Regras de zona:** crianças **não entram na cozinha**. Somente o adulto (`adult_staff`) acessa `restricted`.
- **Corrida restrita:** crianças só correm no `playground` (30% de chance por travessia).
- **Bebedouro:** o nó `NODE_FOUNTAIN` (posição 10, 0, 0.6 — em frente ao bebedouro do P13) está no grafo. Crianças que escolhem esse destino permanecem 2–6s "bebendo" (animação Idle) e depois saem.
- **Parque infantil:** preferido por crianças em 70% das decisões. Podem correr.
- **Variação temporal:** timers aleatórios impedem sincronização de movimentos.

## 2. Limitações honestas (o que NÃO foi feito)

- **Modelos infantis reais** (proporções de criança, cabeça grande, membros curtos) **não foram criados**. Uso o Soldier reduzido como placeholder.
- **Animações específicas** (`sit`, `drink`, `play`) **não existem** no Soldier.glb. Mapeei todas para `Idle` por 2–6s. O comportamento é correto (espera no lugar certo), mas a pose não é específica.
- **Variação facial, cabelo, calçados** — não implementadas (dependentes de modelos reais).

## 3. Roadmap para P25 (Children Visual Realism)

Para cumprir o prompt original (modelos infantis com proporções reais):

1. **Adquirir ou criar** um GLB infantil com rig. Recomendações:
   - **Mixamo** (Adobe, gratuito) — animações humanas com rig padrão.
   - **Kenney.nl** — modelos "Mini Characters" (CC0).
   - **Quaternius** (CC0) — personagens estilizados.
2. **Importar** o GLB no Blender 5.2, aplicar escala 0.65, exportar variantes.
3. **Adicionar** animações `Sit`, `Drink`, `Play` (podem ser geradas via Mixamo e re-exportadas).
4. **Substituir** o `testModelURL` por `./assets/npc/children/child_XX.glb`.

## 4. Instruções de teste

1. Substitua `data/npc_routes.json`, crie `data/npc_roles.json`.
2. Substitua `js/npc/NPCPathfinding.js`, `js/npc/NPCController.js`, `js/npc/NPCManager.js`.
3. Recarregue com Ctrl+Shift+R.
4. Observe:
   - 6 bonecos pequenos (1.1m) de cores variadas no corredor e pátio.
   - 1 boneco adulto (1.8m) cinza entrando/saindo da cozinha.
   - Crianças se aproximam do bebedouro (x=10, z=0.6) e param por alguns segundos.
   - Crianças preferem o pátio e o playground (nós 8, 0, -11 e 8, 0, -18).