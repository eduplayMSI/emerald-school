# P12 — Relatório de Mobiliário Pedagógico

**Estado:** `P12_APPROVED`

## O que foi feito
1. **Salas de Aula (01-04):** Adicionado 1 painel pedagógico (parede norte), 1 tapete de leitura (centro) e 1 armário escaninho (parede leste).
2. **Berçários (01-02):** Adicionado 1 trocador de fraldas, 1 poltrona de amamentação e 1 tapete de estimulação.
3. **Multiuso:** Adicionado 2 expositores de livros e 3 almofadas de leitura.

## Regras de Posicionamento
- **Não bloqueio de portas:** Todos os itens foram posicionados a uma distância mínima de 1,5m das portas para não interferir na abertura automática (que tem raio de 2,6m).
- **Corredores:** Nenhum item foi colocado no corredor ou nas rotas de passagem.
- **Colisores:** Apenas os móveis sólidos (mesas, estantes, escaninhos, trocadores, poltronas) receberam colisores (`COLLIDER_FURN_*`). Tapetes, painéis e almofadas não bloqueiam o jogador.

## Correções Aplicadas
- Os modificadores `Bevel` foram aplicados aos móveis para garantir bordas arredondadas (segurança infantil).
- O script é idempotente: sempre que rodar, ele limpa o mobiliário antigo do P12 e cria o novo, sem duplicar.

## Instruções de Teste
1. Rode o script `P12_pedagogical_furniture.py` no Blender (**Alt+P**).
2. Teste no navegador: `python -m http.server 8000`.
3. Use WASD para andar até uma sala. Verifique se o painel e o tapete estão no fundo e se o escaninho não bloqueia a entrada.
4. Verifique se o piso continua visível (com a correção do `DoubleSide`).