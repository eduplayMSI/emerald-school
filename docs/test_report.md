# Relatório de Testes — Gate P03

| ID  | Procedimento                                           | Esperado                                              | Status |
|-----|--------------------------------------------------------|-------------------------------------------------------|--------|
| G14 | Abrir `.blend` P03; ver viewport                       | Rotas (fitas laranja) + esferas de marcadores visíveis | ⬜ |
| G15 | `data/routes.json` contém 8 rotas                      | OK                                                    | ⬜ |
| G16 | `data/markers.json` contém 8 marcadores                | OK                                                    | ⬜ |
| G17 | Selecionar rota no painel Web                          | Tubo 3D aparece sobre o piso                          | ⬜ |
| G18 | Clicar em um sprite de marcador                        | Painel com descrição/rota/condição abre               | ⬜ |
| G19 | HUD superior esquerdo                                  | Mostra ambiente atual (“Sala de Atividades 01” etc.)  | ⬜ |
| G20 | Painel de camadas (canto superior direito)             | Ligar/desligar camadas altera visibilidade real       | ⬜ |
| G21 | Botão MODO ANÁLISE                                     | Lista de rotas aparece; camadas ativam                 | ⬜ |
| G22 | WASD/mouse/E/portas                                    | Comportamento idêntico ao P02                         | ⬜ |
| G23 | `assets/EMERALD_SCHOOL.glb` atualizado                 | Novo arquivo com playground + pórtico                 | ⬜ |
| G24 | `http://localhost:8000/`                               | Carrega sem erros                                     | ⬜ |

## Logs esperados no console (F12)

[EMERALD][routes] 8 rotas carregadas.
[EMERALD][markers] 8 marcadores, 4 obstáculos, 3 perigos.
[EMERALD][hud] 14 espaços carregados.
[EMERALD][collision] ~90 colisores (11 de porta).
[EMERALD][doors] 11 portas registradas:


## Evidências a capturar

1. 📸 Blender: rotas em fita + playground
2. 📸 Navegador — modo exploração, HUD “Corredor Principal”
3. 📸 Modo análise com rota 002 selecionada (tubo ciano)
4. 📸 Painel de marcador aberto (sprite clicado)
5. 📸 Minimapa mostrando jogador + rota

🚀 Execução

# 1) Colocar todos os arquivos nos caminhos indicados
# 2) Blender 5.2 → salvar .blend em blender\EMERALD_SCHOOL.blend
# 3) Text Editor → blender/P03_accessibility.py → Alt+P
#    Saída esperada:
#       [EMERALD] PROJECT_ROOT = ...\EMERALD-SCHOOL
#       [EMERALD] Portas criadas: 11
#       [EMERALD] Rotas: 8, marcadores: 8, obstáculos: 4, perigos: 3
#       [EMERALD] GLB: ...\assets\EMERALD_SCHOOL.glb (X.XX MB, N objetos)
#       [EMERALD] P03 concluído.
# 4) python -m http.server 8000
# 5) http://localhost:8000/  (Ctrl+Shift+R)
# 6) Clicar em "MODO ANÁLISE" para ver rotas + painel lateral
# 7) Selecionar ROUTE_007 (mostra o estado INTERRUPTED em vermelho)