# P15 — Relatório de Expansão do Parque Infantil

**Estado:** `P15_APPROVED`

## O que foi feito
O parque infantil, que antes contava apenas com um escorregador e um balanço (P03), agora possui uma variedade de equipamentos lúdicos:

1. **Piso Emborrachado (EPDM):** Adicionada uma área de 4x3m de piso vermelho sob a gangorra e o balanço, representando a zona de amortecimento de impacto.
2. **Gangorra:** Modelada com base central de metal, tábua de plástico azul inclinada a 15° e pegadores. Posicionada no centro do parque.
3. **Casinha de Brincar:** Estrutura de madeira medindo 1,6x1,6m e 1,6m de altura, com telhado de duas águas (terracota) e janela lateral. Posicionada no fundo do parque.
4. **Túnel:** Estrutura de concreto (representada por segmentos de arco) para passagem e escalada, instalado próximo ao escorregador.
5. **Painel Sensorial:** Um quadro de metal com blocos coloridos táteis, instalado próximo ao balanço.

## Notas de Segurança e Navegação
- **Colisores:** Todos os brinquedos estruturais (gangorra, casinha, túnel) receberam colisores (`COLLIDER_PLAY_*`). O piso emborrachado e o painel sensorial não possuem colisores para não bloquear a passagem.
- **Espaçamento:** Os brinquedos foram distribuídos respeitando um raio de segurança de 1,5m entre si. O túnel e o escorregador estão agrupados na zona oeste, a casinha no fundo, e a gangorra no centro, permitindo que o jogador caminhe entre eles.
- **Normas:** As distâncias e alturas são representações visuais estimadas para arquitetura 3D, não atestando conformidade com a NBR 16071 sem laudo técnico.

## Instruções de Teste
1. Rode o script `P15_playground.py` no Blender (Alt+P).
2. Inicie o servidor (`python -m http.server 8000`).
3. Vá até o parque (atrás da escola) e verifique os novos brinquedos.
4. Tente atravessar as paredes da casinha ou a base da gangorra; os colisores devem impedir.