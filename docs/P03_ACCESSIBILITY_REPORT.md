# P03 — Relatório de Acessibilidade e Rotas

**Modalidade:** `CONCEPTUAL / SYNTHETIC`
**Data:** — (preencher na execução)

## 1. Metodologia

O memorial `detalhes-da-escola.txt` não apresenta rotas nem critérios de
acessibilidade. As rotas P03 são, portanto, **propostas demonstrativas**
(`ESTIMATED`) e correspondem a percursos fisicamente possíveis no modelo
P02, verificados ponto-a-ponto contra a geometria exportada.

Foi adotada analogia estrutural à metodologia de Corrêa (Parte A — rotas;
Parte B — parque), **sem** reproduzir critérios históricos como norma
vigente. As 8 rotas propostas cobrem os percursos essenciais de uma escola
conceitual.

## 2. Matriz de elementos

| ID | Elemento | Categoria | Rota | Origem | Estado |
|---|---|---|---|---|---|
| ROUTE_001 | Entrada → corredor | Acesso | — | Proposta | ESTIMATED |
| ROUTE_002 | Corredor → sala 01 | Sala | — | Proposta | ESTIMATED |
| ROUTE_003 | Corredor → berçário 01 | Berçário | — | Proposta | ESTIMATED |
| ROUTE_004 | Corredor → WC 01 | Sanitário | — | Proposta | ESTIMATED |
| ROUTE_005 | Corredor → refeitório | Serviço | — | Proposta | ESTIMATED |
| ROUTE_006 | Corredor → cozinha | Serviço | — | Proposta | ESTIMATED |
| ROUTE_007 | Corredor → pátio (contorno) | Lazer | — | Proposta | ESTIMATED |
| ROUTE_008 | Pátio → playground | Lazer | — | Proposta | ESTIMATED |
| OBSTACLE_001 | Soleira da sala 01 | Soleira | ROUTE_002 | Modelo | ESTIMATED |
| OBSTACLE_002 | Pilar pórtico oeste | Estrutura | ROUTE_001 | Modelo | CONFIRMED |
| OBSTACLE_003 | Pilar marquise | Estrutura | — | Modelo | CONFIRMED |
| OBSTACLE_004 | Pilar pátio | Estrutura | ROUTE_007 | Modelo | CONFIRMED |
| HAZARD_001 | Grama sem pavimentação | Piso | ROUTE_007 | Auditoria | ESTIMATED |
| HAZARD_002 | Transição calçada→piso | Piso | ROUTE_001 | Auditoria | ESTIMATED |
| HAZARD_003 | WC cerâmica lisa | Piso | ROUTE_004 | Auditoria | ESTIMATED |
| MARKER_001..008 | Ver `data/markers.json` | Diversos | — | Proposta | ESTIMATED/CONFIRMED |

## 3. Achado principal

**O corredor não possui ligação direta ao pátio** no modelo P02.
A Rota 007 documenta honestamente o desvio: saída pela extremidade oeste
(x=1), contorno externo sobre `SITE_TERRAIN` (grama não pavimentada) e
entrada no pátio pela borda sul (y=8.5 em Blender / z=-8.5 em Web).

**Isso é uma barreira física real** e não foi ocultada. A interface Web
oferece dois botões de *teleporte demonstrativo* (origem/destino) para
inspecionar o trecho bloqueado sem removê-lo.

## 4. Limitações conhecidas

- Sem projeto executivo → nenhuma dimensão de acessibilidade foi
  verificada contra ABNT NBR 9050 ou protocolo equivalente.
- Mobiliário não modelado → não há análise de alcance/mesas adaptadas.
- Playground adicionado em P03 é **conceitual**, não certificado.
- Não há piso tátil, sinalização sonora ou braile no modelo.

## 5. Convenção de coordenadas (validada)

Blender (bx, by, bz) → Web/glTF (bx, bz, -by)


| Ponto | Blender | Web |
|---|---|---|
| Entrada | (-3.5, 0, 0.03) | [-3.5, 0.03, 0] |
| Sala 01 (centro) | (4.5, 3.0, 1.7) | [4.5, 1.7, -3.0] |
| Pátio | (8, 11, 0.05) | [8, 0.05, -11] |

## 6. Arquivos entregues

- `blender/P03_accessibility.py`
- `data/routes.json`, `markers.json`, `obstacles.json`, `hazards.json`, `spaces.json`, `colliders.json`
- `js/routes.js`, `markers.js`, `hud.js`, `minimap.js`, `interface.js`, `main.js`
- `index.html`, `css/style.css`
- `docs/P03_ACCESSIBILITY_REPORT.md` (este arquivo)
- `docs/test_report.md` (atualizado)