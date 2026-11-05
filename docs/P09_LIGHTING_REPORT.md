# P09 — Relatório de Iluminação e Atmosfera

**Estado:** `P09_PENDING`

## Alterações de Iluminação
1. **Sol Nordestino (Blender & Web):** Angulado a 45 graus, cor quente (#FFF2D9). A sombra no Three.js foi ajustada (`shadow.bias`) para evitar o "z-fighting" nos cantos do piso.
2. **Luz Ambiente (Three.js):** O tom marrom da luz hemisférica antiga foi removido e substituído por um tom neutro (`0xB0B0B0`). Isso resolve o problema das paredes amarelas parecerem verdes e do teto parecer marrom.
3. **Luzes de Interior (Blender):** Foram adicionadas 8 luzes pontuais (Point Lights) no teto das salas, corredor e refeitório, exportadas para o navegador via extensão KHR_lights_punctual.
4. **Tone Mapping:** O Three.js agora usa `ACESFilmicToneMapping`, o que garante um contraste mais realista e impede que superfícies claras (como as paredes) estourem para o branco puro.

## Correção do Piso Verde
O arquivo `main.js` foi atualizado para forçar a substituição do material dos pisos via código Javascript. O Three.js agora ignora a cor exportada e aplica as cores `#D1C6B4` (Bege), `#C9A882` (Madeira) e `#B84D47` (Vermelho) diretamente nas malhas.

## Instruções de Execução
1. No Blender: Abra o `.blend`, abra `P09_lighting.py` e aperte **Alt+P**.
2. No Terminal: Rode `python -m http.server 8000`.
3. No Navegador: Pressione **Ctrl+Shift+R**.