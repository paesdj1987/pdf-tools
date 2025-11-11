# frontend/layout_campo.py
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from .ui_css import CSS_EDITOR
from .ui_js import JS_EDITOR

router = APIRouter()

@router.get("/editar", response_class=HTMLResponse)
def inserir():
    html = f"""
<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<title>Editar PDF (Texto, Checkbox, Radio, Borracha)</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
<script>
  pdfjsLib.GlobalWorkerOptions.workerSrc="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";
</script>
<style>
{CSS_EDITOR}
</style>
</head>
<body>
  <div id="app">
    <!-- Topbar -->
    <div class="topbar">
      <div class="left">
        <a href="/" class="pill" title="Voltar para Página inicial" aria-label="Voltar para Página inicial">⬅︎ <span class="label">Página inicial</span></a>
        <button id="undo" class="icon-btn" title="Desfazer (Ctrl+Z)" aria-label="Desfazer">⤺</button>
        <button id="redo" class="icon-btn" title="Refazer (Ctrl+Y / Ctrl+Shift+Z)" aria-label="Refazer">⤻</button>
        <button id="deleteBtn" class="pill danger" title="Excluir selecionado (Del)">🗑️ Excluir</button>
      </div>
      <div class="center">
        <div class="title" style="font-weight:900; letter-spacing:.08em; text-transform:uppercase; color:#ffffff; font-size:18px;">
          EDITAR PDF
        </div>
      </div>
      <div class="right">
        <button id="apply" class="pill secondary" disabled>Aplicar alteração</button>
        <a id="downloadLink" download="pdf_com_campos.pdf">
          <button id="download" class="pill primary" disabled>Download</button>
        </a>
      </div>
    </div>

    <!-- Ferramentas -->
    <div class="toolbar">
      <div class="group" role="group" aria-label="Ferramentas">
        <button id="btnField"  class="gbtn" aria-pressed="false" title="Adicionar Campo"><span>⊞</span> Campo</button>
        <button id="btnText"   class="gbtn" aria-pressed="false" title="Adicionar Texto"><span>T</span> Texto</button>
        <button id="btnImage"  class="gbtn" aria-pressed="false" title="Adicionar Imagem"><span>🖼️</span> Imagem</button>
        <button id="btnErase"  class="gbtn" aria-pressed="false" title="Borracha: remover campos nativos e/ou áreas do PDF"><span>🧽</span> Borracha</button>

        <!-- Formato visual do campo -->
        <select id="fieldShapeKind" class="select-like" aria-label="Formato do campo" title="Formato do campo">
          <option value="rect">Retângulo</option>
          <option value="square">Quadrado</option>
        </select>

        <!-- Tipo do campo -->
        <select id="fieldTypeKind" class="select-like" aria-label="Tipo do campo" title="Tipo do campo">
          <option value="text" selected>Texto (form)</option>
          <option value="checkbox">Checkbox</option>
        </select>

        <input id="imgPicker" type="file" accept="image/*" style="display:none">
      </div>
    </div>

    <!-- Painel de texto -->
    <div id="textPanel" class="text-panel">
      <div class="panel-inner">
        <div class="tp-row">
          <span style="opacity:.8">T</span>
          <select id="tpFont" class="tp-select" title="Fonte" style="width:140px">
            <option value="Arial">Arial</option>
            <option value="Times New Roman">Times New Roman</option>
            <option value="Courier New">Courier New</option>
          </select>
          <select id="tpSize" class="tp-select" title="Tamanho" style="width:70px">
            <option>8</option><option selected>10</option><option>12</option><option>14</option>
            <option>16</option><option>18</option><option>24</option><option>36</option>
          </select>
          <button id="tpBold" class="tp-btn" title="Negrito" aria-pressed="false"><b>B</b></button>
          <button id="tpItalic" class="tp-btn" title="Itálico" aria-pressed="false"><i>I</i></button>
          <button id="tpUnderline" class="tp-btn" title="Sublinhar" aria-pressed="false"><u>U</u></button>
          <span style="margin-left:6px">A</span>
          <input id="tpColor" type="color" class="tp-color" title="Cor do texto" value="#000000">
          <button id="tpAlignL" class="tp-btn" title="Alinhar à esquerda" aria-pressed="true">≡</button>
          <button id="tpAlignC" class="tp-btn" title="Alinhar ao centro" aria-pressed="false">≣</button>
          <button id="tpAlignR" class="tp-btn" title="Alinhar à direita" aria-pressed="false">≡</button>
        </div>
        <div style="margin-top:6px; color:#9fb3c8; font-size:12px">
          Dica: selecione um bloco de texto no PDF para editar; as mudanças aqui aplicam ao selecionado.
        </div>
      </div>
    </div>

    <div id="toast" class="toast" role="status" aria-live="polite"></div>

    <!-- ====== ÁREA QUE ROLA (PDF) ====== -->
    <div id="workarea">
      <div id="drop">
        <label class="upload">
          <input id="fileInput" type="file" accept="application/pdf" style="display:none">
          Selecionar arquivo PDF
        </label>
        <div class="hint">Campo: clique e arraste. Texto: clique para inserir e digitar. Imagem: selecione e clique para posicionar. Borracha: clique para marcar campos do PDF; arraste para apagar áreas. ESC cancela.</div>
      </div>
      <div id="viewer"></div>
    </div>
  </div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
<script>
  pdfjsLib.GlobalWorkerOptions.workerSrc="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";
</script>
<script>
{JS_EDITOR}
</script>
</body>
</html>
"""
    return HTMLResponse(html)
