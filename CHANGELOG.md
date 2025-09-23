# Changelog

## [v1.0.0] - 2025-09-23 *****************

### Adicionado
- Estrutura inicial do projeto `edit_pdf` com FastAPI.
- Layout da tela inicial (`layout_inicial.py`) com hero, cards e botão para abrir o editor de PDF.
- Layout de edição (`layout_campo.py`) com suporte a inserir texto, imagens e checkboxes.
- Funcionalidade de apagar campos adicionados e nativos no PDF.
- Download do **Manual de Utilização** direto pela interface (assets/manual.pdf).
- Estilos customizados no `ui_css.py` (hero, grid, botões, toast).
- Scripts de frontend (`ui_js.py`) com validações, feedback visual e efeitos de botão.
- Dockerfile e docker-compose.yaml para execução em container.

### Alterado
- Ajustes visuais no botão **Manual de Utilização** para cor laranja.
- Organização da estrutura de pastas (`frontend`, `backend`, `assets`).
- Inclusão de `.gitignore` com exclusão de `venv`, `.vscode`, `__pycache__` e `backup`.

### Corrigido
- Correção no apontamento do botão **Manual de Utilização** para `/assets/manual.pdf`.
- Ajuste no mapeamento de containers no Docker para expor corretamente a porta `8055`.
