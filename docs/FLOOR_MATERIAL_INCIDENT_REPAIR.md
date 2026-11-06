# Operação Floor Restore — Relatório de Reparação

**Status:** `FLOOR_RESTORED`

## Diagnóstico Comprovado
O problema do "Piso Verde" foi causado por uma sobreposição de falhas:
1. **P09 (Iluminação):** A `HemisphereLight` usava teto azul (`0xBEE3FF`) e chão marrom (`0x8B7355`). A luz azul batendo nas paredes amarelas criou uma ilusão de ótica (verde) que tingiu o piso.
2. **P10 (JavaScript):** O código tentou contornar isso forçando a cor via JS, mas falhou porque o `THREE` não estava importado e a busca por nome exato (`FLOOR_CORRIDOR`) falhava se o GLTFLoader renomeasse a malha.
3. **P07/P08 (Blender):** A exportação de múltiplos objetos criou sufixos (`.001`) nos materiais, quebrando os mapeamentos anteriores.

## Solução Aplicada
1. **Blender:** Criado o script `repair_floor_material_integrity.py` que varre os objetos pelo nome exato (`FLOOR_*`), limpa os slots de material e força os materiais PBR corretos (`EM_M_floor_*`) diretamente na malha. Exportação feita com `export_apply=True`.
2. **WebGL (scene.js):** Removida a cor azul/marrom da luz hemisférica. Substituída por branco/cinza neutro (`0xffffff`, `0xcccccc`). Ativado `ACESFilmicToneMapping`.
3. **JS (main.js):** O `import * as THREE` foi adicionado. O código de override de material foi removido. No lugar, foi criado um `console.group` de auditoria que imprime o nome do objeto, material e cor hexadecimal, provando que o GLB está correto.

## Testes
- [x] Blender exporta GLB com os materiais PBR corretos.
- [x] WebGL carrega as cores sem o filtro verde da iluminação.
- [x] Console F12 mostra os materiais corretos (`EM_M_floor_ceramic_beige`, etc).