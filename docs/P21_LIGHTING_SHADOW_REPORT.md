# P21 — Relatório de Iluminação e Sombras

**Estado:** `LIGHTING_REALISM_VERIFIED`

## 1. Estratégia Implementada
Para evitar que o navegador trave com múltiplas fontes de sombra, adotamos a seguinte arquitetura:
- **Sol (`DirectionalLight`)**: Responsável pelas sombras externas globais.
- **Luzes de Preenchimento (`Hemisphere`/`Ambient`)**: Reduzidas drasticamente para criar um contraste real entre interior e exterior.
- **Fontes Internas**:
  - **Corredor**: 7 `PointLight` espaçadas a cada 5 metros.
  - **Salas e Refeitório**: `RectAreaLight` (luz de área) nos painéis de teto. Elas não projetam sombras, mas criam uma iluminação difusa super realista (como lâmpadas de LED reais) e custam quase zero de processamento.
  - **Banheiros e Cozinha**: `PointLight` de curto alcance.

## 2. Luminárias Físicas
O script do Blender (P21) criou 18 luminárias físicas. 
- **Corpo (Frame)**: Metal escuro (`Metallic: 0.8`).
- **Difusor**: Material com `Emission Strength: 5.0` para simular a luz acesa.
- Essas luminárias foram exportadas no GLB e o manifesto JSON foi gerado automaticamente pelo Python.

## 3. Parâmetros de Renderização e Cores
- A iluminação da cena usa `ACESFilmicToneMapping`.
- As luzes artificiais usam a cor `#FFF2D9` (Branco quente, aprox. 4000K).
- A intensidade foi calibrada no manifesto para não estourar as paredes.

## 4. Desempenho
- Como as `RectAreaLights` não geram shadow maps, o FPS permanece excelente (>60 fps).
- Nenhuma luz interna projeta sombras dinâmicas (apenas o Sol projeta). Objetos sob as mesas parecerão levemente iluminados pelo rebote ambiente. Se sombras internas forem estritamente necessárias no futuro, podemos ativar `castShadow` em 1 ou 2 `PointLights` específicas.