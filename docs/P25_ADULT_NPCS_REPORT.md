# P25 — Relatório de Equipe Escolar (NPCs Adultos)

**Estado:** `ADULT_NPCS_PARTIALLY_VERIFIED`

## 1. Bug corrigido (P24 → P25)

**Localização da cozinha:** o `NODE_KITCHEN` do P24 estava em `z=-2.9`. Como o Web inverte o eixo Y do Blender, a cozinha real está em `z=+2.9`. Os NPCs eram enviados para o lado errado do corredor.

**Correção:** adicionados `NODE_KITCHEN_01/02/03` em `z ∈ [2.5, 3.5]`, com correta conexão ao corredor via `NODE_CAFE_01`.

## 2. Novos papéis configurados

| Papel | Escala | Zonas permitidas | Zonas preferidas |
|---|---|---|---|
| `teacher` | 1.00 | corredor, sala, parque, refeitório, bebedouro | sala, corredor |
| `aide` | 0.95 | corredor, sala, parque, refeitório, bebedouro | parque, corredor |
| `cook` | 0.95 | **cozinha, refeitório** apenas | cozinha |
| `playground_supervisor` | 1.00 | parque, corredor | parque |

Cada papel recebeu um `preferredZones` explícito, e o `pickPreferredZones` agora respeita esse campo. Antes, esse campo não existia e a heurística excluía cozinhas para qualquer papel (cook ia para o corredor por engano).

## 3. Distribuição de adultos

- **2 professores** em salas de aula (SPC_CLASS_01 e SPC_CLASS_03).
- **1 auxiliar** no playground, acompanhando crianças.
- **1 cozinheira** na cozinha, movimentando-se entre 3 pontos internos.
- **1 supervisor de parque** no centro do playground.

Total: 6 crianças + 5 adultos = 11 NPCs.

## 4. Cores de identificação

- **Criança:** 6 cores rotativas (vermelho, azul, laranja, verde, roxo, âmbar).
- **Professor:** azul-marinho (`#2c3e50`).
- **Auxiliar:** amarelo (`#f1c40f`).
- **Cozinheira:** branco-creme (`#f5f5f5`).
- **Supervisor:** verde (`#27ae60`).

A identificação por cor é auxiliar — o principal é o **comportamento**: a cozinheira não sai da cozinha, o supervisor não sai do parque, os professores ficam perto das salas.

## 5. Limitações (honestas)

- **Modelos:** ainda usam `Soldier.glb` como placeholder. **Não são modelos infantis ou adultos reais.**
- **Vestimentas:** são apenas tints da cor do material. Não há avental de cozinheira nem jaleco de professor.
- **Animações:** todas as atividades mapeiam para `Idle` (não existem `walk_talk`, `work`, `sit` no Soldier).
- **Interação adulto-criança:** não implementada (dependente de animações específicas).
- **Sala dos professores:** não existe no layout arquitetônico do P03. Professores usam a cafeteria e salas como ponto de encontro.

## 6. Roadmap realista para modelos definitivos

O único caminho viável para modelos infantis e adultos com proporções corretas, vestimentas e animações específicas é usar **assets externos com licença verificável**:

1. **Adobe Mixamo** (gratuito, comercial ok) — download de personagens + animações (walk, run, sit, work, etc.).
2. **Quaternius** (CC0) — pacotes "Modular Characters" e "Ultimate Modular Men/Women/Children".
3. **Kenney.nl** (CC0) — "Mini Characters".

Fluxo recomendado:
1. Baixar GLBs com rig.
2. Importar no Blender, aplicar `scale=0.65` para crianças, `1.0` para adultos.
3. Exportar variantes com `export_apply=True`.
4. Substituir `testModelURL` por `./assets/npc/children/child_XX.glb` e `./assets/npc/adults/adult_XX.glb`.
5. Atualizar `npc_roles.json` com cores de roupa por papel (ao invés de tint global).

## 7. Validação

1. Ctrl+Shift+R para recarregar.
2. Observe:
   - **Cozinha:** a cozinheira circula entre bancadas (`z=2.5` a `z=3.5`). Nenhuma criança entra.
   - **Parque:** o supervisor e o auxiliar estão no espaço junto com as crianças.
   - **Salas:** os professores ficam perto do quadro/lousa (idle).
   - **Refeitório:** adultos eventualmente vão almoçar/conversar.
3. Console deve mostrar `[NPC] Cozinheiro(a) → (21.5, 3.5)` e demais.