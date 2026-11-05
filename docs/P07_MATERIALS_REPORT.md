# P07 — Relatório do Sistema de Materiais

**Data:** (preencher na execução)
**Estado:** `P07_PENDING`
**Modalidade:** refinamento material (não reconstrói, não altera geometria)

## 1. Diagnóstico do estado P06

### 1.1 Inventário antes de P07

| Material | Categoria (informal) | Objetos | Base Color | Rough | Metal | Alpha |
|---|---|---|---|---|---|---|
| EM_wall_yellow | parede | todos os muros | #F4D03F | 0.85 | 0 | 1.0 |
| EM_wall_white | parede | forro corredor | #F7F7F7 | 0.85 | 0 | 1.0 |
| EM_floor_beige | piso | corredor, calçada | #DBCCB3 | 0.55 | 0 | 1.0 |
| EM_floor_class | piso | 4 salas + multiuso | #D1B88C | 0.65 | 0 | 1.0 |
| EM_floor_berc | piso | 2 berçários | #FCFCFC | 0.65 | 0 | 1.0 |
| EM_floor_wc | piso | 2 WC + cozinha | #9EA3A8 | 0.55 | 0 | 1.0 |
| EM_floor_cafe | piso | refeitório | #BFC9CE | 0.55 | 0 | 1.0 |
| EM_roof_tile | cobertura | telhado | #B8443A | 0.75 | 0 | 1.0 |
| EM_roof_metal | cobertura | marquise | #C6C6CC | 0.45 | 0.6 | 1.0 |
| EM_column | estrutura | 6 colunas pátio | #E5E5E5 | 0.55 | 0 | 1.0 |
| EM_column_accent | estrutura | 4 pilares | #F28A33 | 0.65 | 0 | 1.0 |
| EM_door_wood | porta | 11 folhas | #855A38 | 0.70 | 0 | 1.0 |
| EM_door_frame | esquadria | 11 batentes | #EAEAEA | 0.60 | 0 | 1.0 |
| EM_glass | vidro | janelas + pátio | #B8DBF2 α0.35 | 0.05 | 0 | 0.35 |
| EM_ground | solo | terreno | #8CAD5A | 0.95 | 0 | 1.0 |
| EM_sand | playground | tanque | #D4C4A0 | 0.95 | 0 | 1.0 |
| EM_patio_rubber | playground | pátio | #B94D4D | 0.85 | 0 | 1.0 |
| EM_play_equip | playground | equipamentos | #5BA8DB | 0.55 | 0.3 | 1.0 |
| P06_grout | junta | 10 ambientes | #8C8074 | 0.95 | 0 | 1.0 |
| P06_skirt | rodapé | 11 ambientes | #B8A898 | 0.80 | 0 | 1.0 |
| P06_grass_a/b/c | vegetação | 6 patches | verdes | 0.95 | 0 | 1.0 |
| P06_earth | solo | 3 manchas | #9E8465 | 0.95 | 0 | 1.0 |
| P06_drain | drenagem | 2 canaletas | #606068 | 0.50 | 0.4 | 1.0 |
| P06_pave_line | calçada | grade | #8C8680 | 0.85 | 0 | 1.0 |
| P06_threshold | soleira | 11 portas | #C7A888 | 0.55 | 0.1 | 1.0 |
| P06_bush | vegetação | 4 arbustos | #4C7A3D | 0.90 | 0 | 1.0 |

**28 materiais arquitetônicos.** 6 materiais técnicos protegidos
(`EM_invisible`, `EM_route_line`, `EM_marker_*`, `EM_door_metal`).

### 1.2 Problemas identificados

| # | Problema | Impacto | Resolução |
|---|---|---|---|
| M1 | Nomes inconsistentes (`EM_*` vs `P06_*`) | Manutenção | Renomeados para `EM_M_*` (prefixo único) |
| M2 | Sem categorização (todos flat) | Auditoria | Categorias em `userData` e manifest |
| M3 | `EM_glass` servia janelas E pátio | Semântica | Unificado em `EM_M_glass_window` (aceitável) |
| M4 | `EM_floor_berc` `roughness=0.65` (vinílico) muito alto | Visual | Reduzido para 0.60 |
| M5 | `EM_column` `roughness=0.55` (concreto) muito baixo | Visual | Elevado para 0.80 |
| M6 | `EM_play_equip` `metallic=0.3` sem motivo | PBR | Reduzido para 0.20 |
| M7 | Cores sem calibração explícita de espaço | Rigor | Todas as cores em sRGB linear (0–1) |
| M8 | Sem `use_backface_culling` definido | Web | Definido: False em glass, True nos demais |
| M9 | Sem manifest documentado | Rastreabilidade | Criado `data/material_manifest.json` |

## 2. Decisão de projeto — sem texturas externas

**Adicionar texturas PBR assadas requer:**
- UV unwrap de ~200 objetos
- Bake via Cycles (lento)
- Empacotamento de imagens no GLB (aumenta tamanho)
- Verificação de `colorSpace` no Three.js

**Ganho visual em geometria blocky de 1ª geração:** marginal.

**Risco introduzido:** quebra do pipeline glTF→Three.js com `colorSpace` errado, perda de banda do usuário, ou falhas de bake.

**Decisão:** P07 entrega **PBR puro** (cores calibradas + roughness + metallic + alpha). Texturas ficam para **P07.1** (ver §9).

## 3. Alterações executadas

### 3.1 Biblioteca criada (28 materiais em 10 categorias)

| Categoria | Qtd | Materiais |
|---|---|---|
| walls | 2 | plaster_white, sun_yellow |
| floors | 5 | ceramic_beige, wood_ceramic, vinyl_white, ceramic_grey, ceramic_cafe |
| roofs | 2 | terracotta, metal |
| structure | 2 | concrete, orange |
| wood | 1 | door_wood |
| metal | 1 | door_frame_white |
| glass | 1 | glass_window |
| ground | 2 | grass_base, earth |
| vegetation | 4 | grass_light, grass_medium, grass_dark, bush |
| playground | 3 | sand, rubber, equipment |
| surfaces | 5 | grout, skirting, threshold, drain, paving_line |

### 3.2 Migração old→new

28 materiais antigos substituídos. Nenhuma geometria alterada.
Todos os objetos mantêm sua posição, nome e colisores.

### 3.3 Materiais técnicos protegidos (não tocados)

`EM_invisible` (colisores), `EM_route_line`, `EM_marker_info`,
`EM_marker_obst`, `EM_marker_haz`, `EM_door_metal` (reservado).

## 4. O que P07 NÃO altera

- Layout, dimensões, número de ambientes, geometria
- 8 rotas, 8 marcadores, 4 obstáculos, 3 perigos, 11 portas
- HAZARD_001/002/003, ROUTE_007 `INTERRUPTED`
- Lógica Web (WASD, colisões, portas, HUD, minimapa, análise)
- `three@0.160.0`

## 5. Instruções de execução

```powershell
# 1. No Blender 5.2 LTS:
#    File → Open → blender\EMERALD_SCHOOL.blend (P06)
#    Text Editor → Open → blender\P07_materials.py
#    Alt+P

# 2. Saída esperada:
#    [EMERALD][P07] PROJECT_ROOT = ...\EMERALD-SCHOOL
#    [EMERALD][P07] Blender 5.2.x
#    [EMERALD][P07] Exportador glTF OK.
#    [EMERALD][P07] Base P03+P06 detectada.
#    [EMERALD][P07] Materiais: 28 criados, 0 atualizados (total 28).
#    [EMERALD][P07] Swaps de material: 247 (skipped 0).
#    [EMERALD][P07] Materiais órfãos purgados: 28.
#    [EMERALD][P07] Inventário de materiais em uso:
#      · EM_M_floor_ceramic_beige      [floors      ]   34 slots
#      · EM_M_wall_sun_yellow          [walls       ]   89 slots
#      ...
#    [EMERALD][P07] GLB: ...\EMERALD_SCHOOL.glb (X.XX MB, N objetos)
#    [EMERALD][P07] Blend salvo: ...\EMERALD_SCHOOL.blend
#    [EMERALD][P07] Concluído.

# 3. Hash
Get-FileHash .\assets\EMERALD_SCHOOL.glb -Algorithm SHA256

# 4. Testar
python -m http.server 8000
# http://localhost:8000/  (Ctrl+Shift+R)