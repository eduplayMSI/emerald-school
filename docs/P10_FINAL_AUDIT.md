# P10 — Auditoria Final e Release

**Estado:** `P10_PENDING`

## Correções Consolidadas
1. **Piso Verde:** O problema foi isolado. Como o usuário relatou que no P06 o piso era normal, a falha estava na tradução dos nomes dos objetos entre o Blender e o Three.js. A solução foi implementada via JavaScript (`main.js`), forçando a cor independente do nome exato (usando `.includes()`).
2. **Iluminação:** O tom esverdeado/marrom foi corrigido em `scene.js`, removendo a luz ambiente colorida e ativando o `ACESFilmicToneMapping`.
3. **Exportação:** O script `P10_final.py` consolida todas as etapas e exporta o modelo final com `export_apply=True` para garantir que escalas e modificadores não quebrem o GLB.

## Checklist de Testes Locais
- [ ] O piso aparece bege/madeira na Web.
- [ ] As paredes estão amarelas e o teto branco.
- [ ] O mobiliário (mesas, berços) está visível.
- [ ] WASD, colisões e portas funcionam.