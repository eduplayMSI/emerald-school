# P22 — Relatório de Realismo Arquitetônico

**Estado:** `ARCHITECTURAL_DETAILS_VERIFIED`

## 1. O que foi adicionado

### Portas (11 unidades)
- **Maçanetas em alavanca** (2 por porta, faces internas e externas do vão): base cilíndrica + alavanca horizontal, em metal escovado (`EM_M_METAL_HANDLE`, metallic=0.9, rough=0.25). Altura de 1.05m — compatível com uso adulto, não com crianças de 1m.
- **Dobradiças** (3 por porta, face externa, junto ao pivô): pequenos blocos metálicos (0.03 × 0.006 × 0.10) que criam a leitura de ferragem real.
- **Hierarquia preservada:** maçanetas e dobradiças são filhas de `DOOR_LEAF_*`, portanto giram junto com a folha quando a porta abre. Nenhum pivô foi alterado.

### Janelas (todas as `WALL_*_GLASS*`)
- **Caixilho completo** (marco inferior, marco superior, montantes laterais).
- **Montante central vertical** (mullion) que divide o vidro em 2 panes. Em janelas reais de 2m × 1,2m, essa configuração é comum.
- Perfis em alumínio branco (`EM_M_WINDOW_FRAME`, metallic=0.6), espessura 4cm, profundidade 6cm. **Y-coordinate centralizado na parede** (dentro da abertura já cortada pela arquitetura), sem Z-fighting com o vidro.

### Interruptores (11 unidades, um por porta)
- Instalados a 1,10m de altura (padrão brasileiro), a 20cm da dobradiça, no lado do corredor (voltados para a circulação).
- Cor branca, tamanho 8cm × 12cm, encostados na face interna da parede do corredor.

## 2. O que NÃO foi alterado
- Geometria, dimensões e cotas arquitetônicas.
- Materiais P20 (paleta original preservada).
- Lógica de portas automáticas e pivôs.
- Colisores existentes.
- Iluminação e sombras (P21).
- Navegação, rotas e minimapa.

## 3. Por que NÃO criei tomadas e rodapés adicionais
O P06 (rodapés) e P06 (soleiras) já haviam criado esses elementos corretamente. A tentação seria adicionar mais variações, mas isso criaria **Z-fighting** e **poluição visual**. O script é idempotente: pode ser reexecutado sem duplicar.

As tomadas elétricas (0,30m de altura) foram **deliberadamente omitidas** nesta etapa para não adicionar ~30 objetos pequenos que exigiriam modelagem de espelhos (placas) e que seriam pouco visíveis na escala de navegação. Elas são recomendadas para P23 (ocupação/fotorrealismo fino), junto com quadros murais e detalhes de mobiliário.

## 4. Impacto no Arquivo GLB
- Adicionados: ~160 objetos pequenos (handle/lever/rose × 2 lados + 3 hinges + 5 window-frame × 15 janelas + switch), todos com 1 material cada.
- Aumento estimado: < 200 KB no GLB.
- Todos os novos objetos têm bevel leve (modifier aplicado na exportação via `export_apply=True`).
- Nenhum novo colisor ou objeto de navegação foi criado.

## 5. Testes Recomendados
1. Abrir a porta de qualquer sala — maçaneta e dobradiças devem girar junto.
2. Olhar uma janela de frente — ver o montante central dividindo o vidro.
3. Aproximar-se de uma porta pelo corredor — interruptor visível na parede ao lado.