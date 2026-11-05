# P02 — Changelog

## Correção principal
- **Bug:** portas abriam visualmente mas o colisor permanecia ativo.
- **Causa:** `setDoorColliderDisabled` casava somente por
  `mesh.userData.emerald_door_id`, que não chega ao navegador em
  reexportações recentes (extras vazios).
- **Correção:** fallback por nome do mesh (`COLLIDER_DOOR_<doorId>`),
  além do caminho por userData. Log adicionado em ambos os lados.

## Melhorias funcionais
- `doors.js` agora prefere o `emerald_swing` gravado no Blender e cai
  para derivação por posição quando ausente.
- Tecla **E** abre a porta mais próxima (raio 3.5 m) como contingência.
- Logs `[EMERALD]` mostram a contagem de colisores e portas no boot.

## Refinamentos arquitetônicos (Blender)
- Pórtico de entrada na fachada oeste com 2 pilares + lintel.
- Marquise plana de 3.2×5.2 m sobre a entrada.
- Batentes visíveis em todas as portas interiores.
- Janelas externas nas fachadas leste/oeste (últimas salas + primeiras).
- Calçada de entrada ampliada para 9×4.4 m.

## Arquivos alterados
- `blender/P02_architecture.py`  (novo)
- `js/collision.js`              (atualizado)
- `js/doors.js`                  (atualizado)
- `data/model_manifest.json`     (versão 2.0.0)
- `docs/test_report.md`          (tabela P02)
- `docs/P02_CHANGELOG.md`        (este arquivo)

## Arquivos inalterados
`index.html`, `css/style.css`, `js/main.js`, `js/scene.js`,
`js/player.js`, `js/interface.js`, `data/spaces.json`,
`data/doors.json`, `data/colliders.json`.