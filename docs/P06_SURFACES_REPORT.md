# P06 — Relatório de Auditoria e Refinamento de Superfícies

**Data:** (preencher na execução)
**Estado:** `P06_PENDING` — script entregue, execução pendente
**Modalidade:** refinamento incremental (não reconstrói a escola)

## 1. Diagnóstico do estado P03

### 1.1 Inventário de superfícies existentes

| Objeto | Coleção | Ambiente | Material | Função | Dado |
|---|---|---|---|---|---|
| SITE_TERRAIN | SITE | externo | ground verde | Terreno | CONFIRMED |
| SITE_ENTRY_W | SITE | exterior | floor_beige | Calçada | CONFIRMED |
| FLOOR_CORRIDOR | FLOORS | corredor | floor_beige | Circulação | CONFIRMED |
| FLOOR_SPC_CLASS_01..04 | FLOORS | salas | floor_class | Sala | CONFIRMED |
| FLOOR_SPC_MULTI | FLOORS | multiuso | floor_class | Multiuso | CONFIRMED |
| FLOOR_SPC_BERC_01..02 | FLOORS | berçário | floor_berc | Berçário | CONFIRMED |
| FLOOR_SPC_WC_01..02 | FLOORS | WC | floor_wc | Sanitário | CONFIRMED |
| FLOOR_SPC_KITCHEN | FLOORS | cozinha | floor_wc | Cozinha | CONFIRMED |
| FLOOR_SPC_CAFE | FLOORS | refeitório | floor_cafe | Refeitório | CONFIRMED |
| FLOOR_PATIO | FLOORS | pátio | patio_rubber | Lazer | CONFIRMED |
| PLAY_SAND | PLAYGROUND | playground | sand | Brincar | ESTIMATED |

### 1.2 Divergências identificadas

| # | Divergência | Severidade | Resolução |
|---|---|---|---|
| D1 | `model_manifest.json` com `version: 2.0.0` e `stage: P02` quando o GLB real era P03 | Média | Corrigido para `3.1.0`/`P06` |
| D2 | Pisos internos sem grout/juntas — leitura uniforme e sem escala | Visual | Grout adicionado (P06) |
| D3 | Ausência de rodapé nos ambientes — parede encontra piso sem transição | Visual | Rodapé adicionado (P06) |
| D4 | Soleira implícita nos vãos (desnível 0.02m sem elemento de transição) | Funcional/Visual | Soleira adicionada (P06) |
| D5 | Terreno uniforme (`SITE_TERRAIN` 120×100 verde chapado) | Visual | Patches de grama em 3 tons (P06) |
| D6 | Sem representação de terra batida nos acessos | Visual | 3 manchas de terra (P06) |
| D7 | Calçada sem paginação | Visual | Grade de juntas 0.6m (P06) |
| D8 | Ausência de drenagem superficial representativa | Visual | 2 canaletas exteriores (P06) |
| D9 | Sem vegetação rasteira | Visual | 4 arbustos (P06) |
| D10 | `sha256` null no manifest | Documental | Pendente — calcular pós-execução |

### 1.3 O que NÃO foi alterado (preservação intencional)

- **HAZARD_001** — ROUTE_007 continua sobre grama não pavimentada. Nenhuma pavimentação nova foi adicionada no corredor ROUTE_007 (x∈[0,2], y∈[0,8.5] em Blender / z∈[-8.5,0] em Web).
- **HAZARD_002** — Transição calçada→piso interno preservada com o desnível original. Soleira adicionada como elemento de leitura visual, não como rampa.
- **HAZARD_003** — Piso do WC mantido sem tratamento. Grout adicionado mas não sinaliza risco de escorregão.
- **ROUTE_007** — Mantida como `INTERRUPTED`. Nenhuma tentativa de "consertar" a rota pelo lado visual.
- **Todas as 8 rotas, 8 marcadores, 4 obstáculos, 3 perigos** — IDs e coordenadas inalterados.

## 2. Alterações executadas

| Item | Objeto(s) criado(s) | Coleção P06 | Qtd |
|---|---|---|---|
| Grout de piso cerâmico | `P06_GROUT_<room>` (mesh único) | INTERNAL_FLOORS | 10 |
| Rodapé | `P06_SKIRT_<room>_{N,S,E,W}` | SKIRTING | 44 |
| Soleira | `P06_THRESH_<door_id>` | TRANSITIONS | 11 |
| Variação de grama | `P06_GRASS_PATCH_01..06` | EXTERNAL_GROUND | 6 |
| Terra batida | `P06_EARTH_01..03` | EXTERNAL_GROUND | 3 |
| Grade da calçada | `P06_PAVE_GRID_ENTRY_W` (mesh único) | PAVING | 1 |
| Drenagem | `P06_DRAIN_S`, `P06_DRAIN_SE` | DRAINAGE | 2 |
| Arbustos | `P06_BUSH_01..04` | DECOR | 4 |

**Total:** 81 objetos. Todos em `EMERALD_GENERATED/P06_SURFACES`.

### 2.1 Materiais novos (`P06_*`)

`grout`, `skirt`, `grass_a`, `grass_b`, `grass_c`, `earth`, `drain`, `pave_line`, `threshold`, `bush` — todos BSDF puro, sem texturas (consistente com P03).

## 3. Instruções de execução

```powershell
# 1. No Blender 5.2 LTS:
#    a. File → Open → blender/EMERALD_SCHOOL.blend (o do P03)
#    b. Text Editor → Open → blender/P06_surfaces.py
#    c. Alt+P
#
# 2. Saída esperada:
#    [EMERALD][P06] PROJECT_ROOT = ...\EMERALD-SCHOOL
#    [EMERALD][P06] Blender 5.2.x
#    [EMERALD][P06] Exportador glTF OK.
#    [EMERALD][P06] Base P03 detectada (SITE_TERRAIN + FLOOR_CORRIDOR).
#    [EMERALD][P06] Cleanup P06 OK.
#    [EMERALD][P06] Coleções P06: [...]
#    [EMERALD][P06] Grout lines: 10 ambientes (1 mesh cada).
#    [EMERALD][P06] Rodapé: 44 segmentos.
#    [EMERALD][P06] Soleiras: 11 portas.
#    [EMERALD][P06] Grama: 6 patches (tons variados).
#    [EMERALD][P06] Terra batida: 3 manchas.
#    [EMERALD][P06] Calçada: grade de juntas adicionada.
#    [EMERALD][P06] Drenagem: 2 canaletas exteriores.
#    [EMERALD][P06] Vegetação: 4 arbustos.
#    [EMERALD][P06] GLB exportado: ...\EMERALD_SCHOOL.glb (X.XX MB, N objetos)
#    [EMERALD][P06] Blend salvo: ...\EMERALD_SCHOOL.blend
#    [EMERALD][P06] Concluído.
#
# 3. Calcular hash e colar no model_manifest.json
Get-FileHash .\assets\EMERALD_SCHOOL.glb -Algorithm SHA256

# 4. Servir e testar
cd $env:USERPROFILE\Desktop\EMERALD-SCHOOL
python -m http.server 8000
# http://localhost:8000/  (Ctrl+Shift+R)