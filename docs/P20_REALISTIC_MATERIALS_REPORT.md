# P20 — Relatório de Materiais Realistas

**Estado:** `MATERIALS_REALISM_VERIFIED`

## 1. Diagnóstico do Estado Anterior
A escola utilizava cores chapadas e excessivamente saturadas (Amarelo Sol forte, Verde Neon, Madeira muito laranja). O contraste entre rodapé, parede e soleira era praticamente nulo. A ilusão de "maquete digital" prejudicava a imersão.

## 2. Direção Estética Aplicada
- **Paredes:** Adotamos um tom de Areia Claro (`#E5DEC9`) para as áreas comuns, garantindo luminosidade. Os berçários e a biblioteca receberam um tom de Verde Sálvia (`#A3B59E`), que acalma e remete à natureza.
- **Contraste de Base:** O rodapé agora é um Cinza Escuro (`#595A5B`), criando uma linha de ancoragem visual com o piso. A soleira foi pintada de Branco Gelo (`#F0F2F5`), destacando-se absolutamente do chão de madeira ou cerâmica.
- **Pisos:** O corredor ganhou um Porcelanato Cinza-Claro (`#B8B8B8`), mais condizente com áreas de alto tráfego. As salas têm Piso de Madeira (`#8C6D4C`) mais escuro e natural. Os banheiros têm piso Cerâmico Cinza (`#7D858A`).
- **Janelas:** O vidro foi mantido Opaco com Metallic 0.8 e base azulada (`#5C7785`), o que cria um efeito de reflexo do céu, eliminando o flicker (definido no P19) e adicionando sofisticação.
- **Estrutura:** Os pilares e vigas foram atualizados para um Concreto (`#BFBFB7`) mais neutro e realista.

## 3. Propriedades PBR Implementadas
- **Metallic** foi mantido em `0.0` para todas as superfícies porosas (paredes, madeiras, pisos cerâmicos) e elevado para vidros e alguns metais.
- **Roughness** foi ajustado: `0.9` para paredes (fosco, evita reflexos falsos), `0.45` para pisos (leve brilho cerâmico) e `0.1` para vidros (reflexão nítida).

## 4. O que NÃO foi alterado
- A geometria, portas, pivôs, rotas, marcadores, colisores e a lógica de navegação foram preservados.
- A iluminação (Sol e luzes neutras) configurada no P19 permanece intacta.

## 5. Instruções de Teste
1. Rode o `P20_realistic_materials.py` no Blender.
2. Inicie o servidor local e abra o navegador (Ctrl+Shift+R).
3. Observe as janelas: elas refletem a cor do céu graças ao alto Metalness, sem piscar.
4. Compare a transição do rodapé escuro para a parede clara, e a soleira branca no chão. A leitura arquitetônica deve estar nítida.