# P13 — Relatório de Instalações Sanitárias e Higiene

**Estado:** `P13_APPROVED`

## O que foi feito
1. **Sanitários (SPC_WC_01 e SPC_WC_02):** Adicionados 2 vasos sanitários, 2 lavatórios, 2 espelhos e 1 divisória por banheiro. Os itens estão posicionados nas paredes do fundo e laterais, mantendo a área central e a porta (raio de 2.6m) livres para circulação.
2. **Cozinha (SPC_KITCHEN):** Adicionada uma pia industrial, um fogão e uma geladeira, todos em aço inox (material `EM_M_column_concrete`). Estão posicionados na parede do fundo (Y = -4.6).
3. **Corredor:** Adicionado 1 bebedouro de alturas duplas próximo à parede (Y = -0.6), entre as salas 02 e 03, sem bloquear a passagem central.

## Notas de Design e Segurança
- **Acessibilidade:** As pias dos banheiros foram instaladas a 0.55m de altura (foco infantil). O bebedouro possui bicas em duas alturas.
- **Colisores:** Os vasos, pias, pias industriais e bebedouros receberam colisores (`COLLIDER_FIX_*`) para impedir que o jogador atravesse. Espelhos e dispensadores não possuem colisores (são irrelevantes para a navegação).
- **Idempotência:** O script limpa a coleção `P13_SANITARY` antes de rodar, prevenindo duplicações.

## Instruções de Teste
1. Rode o script no Blender e verifique se as peças apareceram nos banheiros.
2. Inicie o servidor (`python -m http.server 8000`).
3. No navegador, entre no Sanitário 01. Verifique se os vasos estão no fundo e as pias na parede esquerda.
4. Vá até a cozinha e verifique a bancada de fundo.
5. Passeie pelo corredor e verifique o bebedouro sem que ele bloqueie o caminho.