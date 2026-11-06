# P19 — Relatório de Integridade Visual

**Estado:** `VISUAL_INTEGRITY_VERIFIED`

## Diagnóstico Forense (A Causa Raiz)

### 1. O Piso "Verde" e a Transparência das Paredes (Normais Invertidas)
O script original (P03) possuía uma falha na matriz de faces da função `make_box`. Todos os vetores normais (a "frente" da face) foram apontados para dentro do objeto. 
No Three.js, o padrão é renderizar apenas o lado de fora das faces (`FrontSide`). Portanto, o piso estava invisível visto de cima. O que o usuário via como "piso verde" era o terreno de grama que ficava embaixo do piso invisível. As paredes também estavam invisíveis por fora, mas visíveis por dentro, criando o efeito de "teto marrom" e "paredes planas".

### 2. A Cintilação (Z-Fighting)
Os objetos de detalhe criados no P06 (rejunte, grama e terra) foram posicionados a uma distância de 0.003 a 0.005 metros (3 a 5 milímetros) do chão e do terreno. Isso causa uma sobreposição na memória de vídeo (Z-buffer). Quando a câmera se move, o motor gráfico não sabe qual face desenhar primeiro, criando o efeito de piscar.

## Correções Aplicadas

1. **Blender (`P19_visual_integrity.py`):**
   - Varremos todas as malhas da escola e usamos o comando `bmesh.ops.recalc_face_normals` para forçar o Blender a recalcular os vetores apontando para fora.
   - Elevamos o `P06_GROUT` (rejunte) em 1.5cm em relação ao piso.
   - Elevamos a grama e a terra para 2cm acima do terreno.

2. **Three.js (`scene.js`):**
   - Alteramos o `PerspectiveCamera`. O `near` passou de `0.1` para `0.2` e o `far` de `500` para `250`. Isso dobra a precisão do Z-buffer e acaba com qualquer resquício de Z-fighting em objetos distantes.

3. **Three.js (`main.js`):**
   - Removemos a "gambiarra" do `DoubleSide` (que forçava o piso a ser visível por baixo). Como as normais agora estão corretas no Blender, o `DoubleSide` não é mais necessário e causaria problemas de iluminação.

## Resultado Esperado
Ao rodar o modelo, o piso bege estará visível por padrão, as paredes terão sombreamento realista com base no Sol, e a movimentação não fará mais a grama ou o rejunte piscarem.