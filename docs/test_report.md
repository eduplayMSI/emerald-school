# Relatório de Testes — Gate P02

| ID  | Procedimento                                            | Esperado                                    | Status |
|-----|---------------------------------------------------------|---------------------------------------------|--------|
| G05 | Abrir `blender/EMERALD_SCHOOL.blend` pós-P02            | Pórtico + marquise visíveis                 | ⬜     |
| G06 | `python -m http.server 8000` → carregar GLB novo        | 200, sem erro no console                    | ⬜     |
| G07 | Escola visível em 3D após INICIAR VISITA                | Edifício renderizado com refinamentos       | ⬜     |
| G08 | WASD / setas                                            | Movimento contínuo, diagonal normalizada    | ⬜     |
| G09 | Mouse ↑ / ↓                                             | Pitch sobe / desce (sem inversão)           | ⬜     |
| G10 | Aproximar de qualquer porta (≤ 2.6m)                    | Porta abre automática                       | ⬜     |
| G11 | Atravessar o vão aberto                                 | **Jogador ENTRA na sala** (bug corrigido)   | ⬜     |
| G12 | Afastar-se (> 3m) da porta                              | Porta fecha, colisor reativa                 | ⬜     |
| G13 | Pressionar **E** perto de porta fechada                 | Porta abre imediatamente                    | ⬜     |
| G14 | F12 → Console                                            | Logs `[EMERALD][doors] N portas` + `[EMERALD][collision] N colisores (M de porta)` | ⬜ |
| G15 | Estrutura do repositório                                | `P02_architecture.py` presente; GLB novo    | ⬜     |

## Verificação do fix crítico

Após carregar a página, no console **deve aparecer**:

[EMERALD][collision] 87 colisores (11 de porta).
[EMERALD][doors] 11 portas registradas:
· WALL_SPC_CLASS_01_S_D0 (openAngle=1.571 rad)
· WALL_SPC_CLASS_02_S_D0 (openAngle=1.571 rad)


Ao **atravessar** a primeira porta, deve aparecer:

[EMERALD][doors] "WALL_SPC_CLASS_01_S_D0" abriu mas colisor não foi achado.

**— somente se** o `setDoorColliderDisabled` falhar. Se não aparecer,
o casamento por nome funcionou e o jogador entra na sala.

## Evidências a capturar

1. 📸 Blender — pórtico de entrada + marquise.
2. 📸 Navegador — escola carregada.
3. 📸 Jogador **dentro** de uma sala (evidência do fix).
4. 📸 Console com os logs `[EMERALD]`.