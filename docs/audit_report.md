# Auditoria — P01 EMERALD-SCHOOL

## Dados de entrada

| Item | Fonte | Status |
|---|---|---|
| Programa de ambientes | `detalhes-da-escola.txt` | CONFIRMED |
| Dimensões de salas (7×7, 6×6, 8×6, 5×4, 3×2.5, 12×6) | idem | CONFIRMED |
| Pé-direito (3.0m / 2.8m / 3.5m pátio) | idem | CONFIRMED |
| Cores por ambiente | idem | CONFIRMED |
| Orientação solar / ventos | — | MISSING (adotado X=Leste-Oeste) |
| Topografia | — | MISSING (plano) |
| Programa externo (recepção, diretoria) | — | MISSING (omitido) |

## Premissas (INFERRED / ESTIMATED)

1. **Bloco único térreo** — não há indicação de segundo pavimento.
2. **Corredor central de 1.8m** entre as duas fileiras de salas.
3. **Telhado em duas águas** com cumeeira a 4.5m, beirais a 3.1m.
4. **Pátio coberto** ao norte, apoiado em 6 colunas, laje translúcida.
5. **Portas de madeira** com 0.90×2.10m, folha única, pivô esquerdo.
6. **Janelas de vidro** temperado 2.0×1.2m (sill 0.9m, topo 2.1m).

## Divergências

Nenhum conflito entre os dados do memorial e a implementação. A
**cor exata** de cada parede segue o documento; materiais de piso seguem
especificado (`floor_class` = cerâmica madeira clara, `floor_berc` =
vinílico branco-gelo, `floor_wc` = cerâmica cinza, `floor_cafe` = cerâmica clara).

## Simplificações conhecidas (v1)

- Mobiliário interno **não modelado** nesta versão.
- Pátio coberto com laje plana de vidro (visualização do "translúcido").
- Portas ao sul abrem na direção do corredor (não para dentro do berçário);
  corrigível com `emerald_swing = -1` no pivô.
- Ornamentos recicláveis (pneus, caixas) **não incluídos** em P01.

## Nota sobre o eixo glTF

Conversão Blender→glTF: `(x, y, z) → (x, z, -y)`. Portas ao norte
(Belnder y=0.9) ficam com Z(glTF) = -0.9; ao sul ficam com Z = +0.9.
O sinal de abertura em Y no Three.js é derivado desse valor.