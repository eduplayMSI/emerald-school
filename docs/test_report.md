# Relatório de Testes — Gate P01

> ⚠ Estes testes devem ser **executados** pelo usuário. Este documento
> é o template a ser preenchido com os resultados observados.

| ID | Procedimento | Resultado esperado | Resultado observado | Status |
|----|--------------|--------------------|---------------------|--------|
| G01 | Abrir `blender/EMERALD_SCHOOL.blend`; verificar viewport | Edificação real (paredes, portas, telhado) | | ⬜ |
| G02 | `ls -la assets/EMERALD_SCHOOL.glb` | Arquivo existe; tamanho > 100 KB | | ⬜ |
| G03 | `python -m http.server 8000` + abrir URL | Página carrega em < 3s | | ⬜ |
| G04 | Clicar INICIAR VISITA | Escola 3D renderiza no navegador | | ⬜ |
| G05 | WASD + mouse | Movimento e orientação corretos (mouse ↑ = olhar ↑) | | ⬜ |
| G06 | Caminhar contra parede | Jogador não atravessa | | ⬜ |
| G07 | Aproximar de porta | Porta abre automaticamente | | ⬜ |
| G08 | Entrar pela fachada oeste | Corredor acessível | | ⬜ |
| G09 | F12 → Console | Nenhum erro vermelho | | ⬜ |
| G10 | Estrutura do repositório | `index.html` na raiz; todos os arquivos presentes | | ⬜ |

## Evidências a capturar

1. 📸 Screenshot do Blender (câmera externa)
2. 📸 Screenshot do navegador (escola visível)
3. 📸 Screenshot durante navegação (crosshair visível)
4. 📸 Screenshot de porta aberta próxima

## Comandos de verificação rápida

```bash
# 1) Estrutura de arquivos
find . -maxdepth 2 -type f | sort

# 2) Tamanho do GLB
du -h assets/EMERALD_SCHOOL.glb

# 3) Servidor local
python -m http.server 8000