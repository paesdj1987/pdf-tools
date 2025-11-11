# Changelog

## [v1.2.0] - 2025-11-11 *****************

### Adicionado
- **Editor de Texto (B/I/U + Cor)**:
  - Suporte completo a **Negrito (B)**, **Itálico (I)** e **Sublinhado (U)** no painel do editor.
  - Mapeamento correto de fontes compatíveis com PyMuPDF (`helv`, `times`, `courier`).
  - Função `mapFontToPDF()` revisada para combinar peso/estilo com segurança.
  - Nova função `normalizeColorToHex()` no `ui_js.py` para conversão automática de cores `rgb()`/`#RGB` → `#RRGGBB`.
  - Suporte total à **cor personalizada** no texto, com preview instantâneo e renderização fiel no PDF.

### Alterado
  - `api_apply.py`: redesenho do bloco “Desenhos fixos (texto, imagem, círculos)” para processar:
  - Sublinhado manual (desenha linha sob o texto, sem quebrar `_insert_text`).
  - Log detalhado de erros sem interromper o processamento do PDF.
  - Melhor integração entre frontend e backend: mapeamento de cores e fontes agora consistente.

### Corrigido
- Inconsistência de estilo nos botões B/I/U que não alternavam estado visual (`aria-pressed`).
- Ajuste no status de “Arquivo pronto” (centralizado e tamanho reduzido).
- Remoção definitiva da tarja azul de “Processando”.

---

## [v1.1.1] - 2025-11-10 *****************

### Alterado
- Converter PDF → Word: adiciona estado de loading no botão “Converter” com spinner e rótulo “Convertendo…”.
- Bloqueia inputs (modo, OCR, páginas, senha) e marca `aria-busy` durante o processamento.
- Restaura estado dos controles e habilita download ao concluir.

---

## [v1.1.0] - 2025-11-03 *****************

### Adicionado
- **Nova funcionalidade “Converter PDF → Word”**
  - Novo layout `frontend/converter_word.py` seguindo o padrão visual do módulo Editar.
  - Backend `backend/api_convert_word.py` responsável pela conversão de PDF em `.docx`.
  - Suporte a dois modos de conversão:
    - **Preservar Formatação (pdf2docx)**: mantém layout e estilos originais.
    - **Somente Texto (PyMuPDF + python-docx)**: gera texto limpo e editável.
  - Opções de intervalo de páginas e senha do PDF.
  - Tooltips explicativos sobre os modos de conversão.
  - Sistema de mensagens e toasts aprimorado com feedback visual.

### Alterado
- Ajuste preciso do posicionamento da **toolbar** (removendo espaçamento excessivo).
- Removida a tarja branca sob a toolbar e aplicada cor sólida escura.
- Revisão das cores dos status (`status-hint.ok` e `status-hint.err`) para melhor contraste.
- Eliminação do “botão verde fantasma” após a conversão concluída.
- Unificação de estilos visuais entre os módulos “Editar PDF” e “Converter PDF → Word”.

### Corrigido
- Correção da faixa branca atrás da toolbar.
- Tooltip agora aparece corretamente sobre os demais elementos.
- Mensagens de upload e status com fonte mais legível no tema escuro.
- Correção da margem superior da toolbar (reposicionamento final entre topbar e conteúdo).

---

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
