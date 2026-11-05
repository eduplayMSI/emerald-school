# EMERALD-SCHOOL — P01

CMEI Nordeste navegável no navegador. Base do projeto **Emerald-Scarlete**.

## Pré-requisitos

- **Blender 5.2 LTS** (com add-on glTF 2.0 habilitado)
- **Navegador moderno** com WebGL
- **Python 3** (para servir o site localmente)
- **Git**

## 1. Gerar o modelo 3D

1. Abra o Blender 5.2 LTS.
2. Abra `blender/P01_school.py` no **Text Editor**.
3. Ajuste a variável `PROJECT_ROOT` no topo se necessário.
4. Execute com **Run Script** (Alt+P).
5. Serão gerados:
   - `blender/EMERALD_SCHOOL.blend`
   - `assets/EMERALD_SCHOOL.glb`

## 2. Rodar a aplicação web

Na raiz do repositório:

```bash
python -m http.server 8000
```

Abra: **http://localhost:8000/**

> ⚠️ `file://` **não funciona** (CORS bloqueia o GLB).

Alternativa: extensão **Live Server** do VS Code.

## 3. Navegação

- **WASD** / setas: mover
- **Mouse**: olhar (clique para capturar)
- **Shift**: correr
- **Esc**: liberar mouse
- **R**: reposicionar na entrada
- Portas abrem **automaticamente** ao aproximar

## 4. Publicar no GitHub Pages

```bash
git init
git add .
git status
git commit -m "P01: escola base navegável"
git branch -M main
git remote add origin https://github.com/<seu-usuario>/EMERALD-SCHOOL.git
git push -u origin main
```

Em **Settings → Pages**, escolha `main` / `root`. A URL pública será:
`https://<seu-usuario>.github.io/EMERALD-SCHOOL/`

## 5. Estrutura

Ver `data/model_manifest.json`, `docs/audit_report.md`, `docs/test_report.md`.

## Licença

Uso reservado — ver `LICENSE.md`.