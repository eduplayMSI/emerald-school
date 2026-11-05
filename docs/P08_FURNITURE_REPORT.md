# P08 — Relatório de Mobiliário

**Estado:** `P08_PENDING` (Aguardando execução)

## O que foi feito
- Foram criados blocos de construção procedurais (mesas, cadeiras, estantes, berços, bancadas) usando Python no Blender.
- O mobiliário foi posicionado respeitando o espaço livre das portas (nenhum móvel foi colocado a menos de 1,5m das portas para não bloquear a abertura automática).
- Todos os móveis usam materiais extraídos da biblioteca do P07 (`EM_M_*`).
- O chão verde foi corrigido em definitivo via JavaScript (Three.js `traverse`), forçando os materiais corretos independentemente do que o Blender exporte.

## Ambientes Mobiliados
- **Salas 01-04:** 1 mesa central + 4 cadeiras + 1 estante.
- **Berçários 01-02:** 2 berços + 1 estante.
- **Cozinha:** 2 bancadas (inox).
- **Refeitório:** 2 mesas grandes + 3 bancos.
- **Multiuso:** 2 estantes + 1 mesa.

## Instruções de Execução
1. Abra o Blender 5.2.
2. Carregue `blender/EMERALD_SCHOOL.blend`.
3. Abra `blender/P08_furniture.py` e aperte **Alt+P**.
4. Verifique a saída no console: `[P08] GLB Exportado`.
5. Vá para a pasta do projeto no terminal e rode `python -m http.server 8000`.
6. Abra no navegador e pressione **Ctrl+Shift+R**.

## Correção Definitiva do Piso
O `main.js` foi atualizado. Ele agora intercepta as malhas dos pisos logo após o carregamento do GLB e substitui o material pelo `MeshStandardMaterial` com a cor hexadecimal exata em JavaScript. Isso contorna qualquer falha de exportação de material do Blender.