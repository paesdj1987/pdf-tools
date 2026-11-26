# frontend/converter_word.py
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from .ui_css import CSS_EDITOR

router = APIRouter()

@router.get("/converter-word", response_class=HTMLResponse)
def converter_word_page():
    html = (
        "<!doctype html>"
        "<html lang='pt-br'>"
        "<head>"
        "<meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        "<title>Converter PDF → Word (.docx)</title>"
        "<style>\n"
        + CSS_EDITOR +
        """
/* ====== Ajustes específicos desta página ====== */

/* Evitar tarja branca/blur sob a toolbar */
.toolbar {
  background: transparent !important;
  box-shadow: none !important;
  -webkit-backdrop-filter: none !important;
  backdrop-filter: none !important;
  position: relative;
  top: 10px;                 /* ajuste fino: aproxima da topbar sem colar */
  margin-bottom: 0;
  padding-top: 0;
  z-index: 15;
}
.toolbar::before,
.toolbar::after { display: none !important; }

/* Pílula da toolbar e prevenção de clipping de tooltips */
.toolbar, .toolbar .group {
  position: relative;
  overflow: visible;
  z-index: 30;
}
.toolbar .group {
  background: rgba(2, 6, 23, 0.85);
  border: 1px solid #0f172a;
  border-radius: 16px;
  box-shadow: 0 10px 24px rgba(0,0,0,.35), inset 0 0 0 1px rgba(255,255,255,.02);
  padding: 10px;
}

/* Inputs/seletores na toolbar */
.group .input-like, .group .select-like {
  height: 38px;
  border-radius: 10px;
  border: 1px solid #334155;
  background: #1f2937; color:#e5e7eb;
  padding: 0 .7rem;
}
.group .input-like { min-width: 140px; }
.group .select-like { min-width: 200px; }

/* Tooltip robusto (hover + focus) */
.tooltip-wrapper{
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-right: 8px; /* respiro entre controles */
}
.tooltip-label{ color:#cbd5e1; font-size:14px; }
.tooltip-box{
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  background: rgba(15,23,42,0.98);
  color: #e2e8f0;
  border: 1px solid #475569;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 13px;
  line-height: 1.4;
  width: 300px;
  box-shadow: 0 8px 24px rgba(0,0,0,.5);
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
  transition: opacity .18s ease, visibility .18s ease;
  z-index: 9999;
}
.tooltip-wrapper:hover .tooltip-box,
.tooltip-wrapper:focus-within .tooltip-box{
  opacity: 1; visibility: visible;
}

/* Espaçamento e legibilidade na área de drop */
#drop .upload { min-width: 240px; }
.hint {
  margin-top: 20px;
  margin-bottom: 16px;
  line-height: 1.6;
}
.filename {
  color: #94a3b8;
  margin-top: 10px;
  margin-bottom: 14px;
  font-size: 14px;
}
/* Mensagem principal (status) — só aparece quando tem conteúdo */
.status-hint{
  margin:10px 0;
  font-size:14px;
  border-radius:12px;
  /* sem padding/fundo por padrão */
  padding:0;
  background:transparent;
  border:none;
  color:#e2e8f0;
  box-shadow:none;
  transition: all .25s ease;
}
/* se estiver vazio: não exibe nada */
.status-hint:empty{ display:none; }

/* quando tiver conteúdo, vira “card” */
.status-hint:not(:empty){
  padding:12px 14px;
  background: rgba(15, 23, 42, .8);
  border: 1px solid transparent;
  box-shadow: 0 6px 20px rgba(0, 0, 0, .25);
}

/* variações */
.status-hint.ok{
  border-color: rgba(34,197,94,.55);
  background: linear-gradient(180deg, rgba(6,78,59,.9), rgba(21,128,61,.9));
  color: #d1fae5;
}
.status-hint.err{
  border-color: rgba(239,68,68,.55);
  background: linear-gradient(180deg, rgba(127,29,29,.9), rgba(185,28,28,.9));
  color: #fee2e2;
}
.status-row{ display:flex; align-items:center; gap:10px; }
.status-icon{
  width:28px; height:28px; border-radius:50%;
  background: rgba(255,255,255,.15);
  display:flex; align-items:center; justify-content:center; font-weight:700;
}
/* === Status menor e centralizado === */
#status.status-hint:not(:empty){
  /* largura controlada e central */
  width: clamp(280px, 60vw, 620px);
  margin: 12px auto;           /* centraliza */
  padding: 10px 12px;          /* mais compacto */
  border-radius: 14px;
  box-shadow: 0 10px 24px rgba(0,0,0,.18);
}

/* elementos internos mais compactos */
#status .status-row{ gap: 8px; align-items: center; }
#status .status-icon{
  width: 22px; height: 22px;   /* ícone menor */
  font-size: 13px;
}
#status strong{ font-weight: 800; }
#status small{ opacity: .9; }



/* Sutil respiro entre toolbar e área */
#workarea { margin-top: 8px; }

/* ====== Botão de loading (Converter) ====== */
.pill.loading { position: relative; cursor: default; }
.pill .spinner {
  display: none;
  width: 14px; height: 14px;
  border: 2px solid transparent;
  border-top-color: #fff; border-right-color: #fff;
  border-radius: 50%;
  margin-left: 8px;
  animation: spin .8s linear infinite;
}
.pill.loading .spinner { display: inline-block; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ==== MENSAGENS MODERNAS E ANIMADAS (override) ==== */

/* Mensagem principal (status) — agora aceita HTML e tem estilos modernos */
.status-hint {
  margin: 10px 0;
  font-size: 14px;
  border-radius: 12px;
  padding: 12px 14px;
  border: 1px solid transparent;
  background: rgba(15, 23, 42, .8);
  color: #e2e8f0;
  box-shadow: 0 6px 20px rgba(0, 0, 0, .25);
  transition: all .25s ease;
}
.status-hint.ok {
  border-color: rgba(34,197,94,.55);
  background: linear-gradient(180deg, rgba(6,78,59,.9), rgba(21,128,61,.9));
  color: #d1fae5;
}
.status-hint.err {
  border-color: rgba(239,68,68,.55);
  background: linear-gradient(180deg, rgba(127,29,29,.9), rgba(185,28,28,.9));
  color: #fee2e2;
}
.status-row {
  display: flex; align-items: center; gap: 10px;
}
.status-icon {
  width: 28px; height: 28px;
  border-radius: 50%;
  background: rgba(255,255,255,.15);
  display: flex; align-items: center; justify-content: center;
  font-weight: bold;
}

/* Toast flutuante (notificação superior) moderno */
.toast {
  visibility: hidden;
  position: fixed;
  z-index: 9999;
  left: 50%; bottom: 100px;
  transform: translateX(-50%);
  min-width: 240px;
  padding: 12px 18px;
  border-radius: 14px;
  border: 1px solid rgba(148,163,184,.25);
  background: rgba(15,23,42,.95);
  color: #f1f5f9;
  font-size: 14px;
  opacity: 0;
  transition: opacity .3s ease, bottom .3s ease;
}
.toast.show { visibility: visible; opacity: 1; bottom: 130px; }
.toast.success {
  background: linear-gradient(180deg, rgba(6,78,59,.95), rgba(21,128,61,.92));
  border-color: rgba(34,197,94,.55);
  color: #e6fff1;
}
.toast.error {
  background: linear-gradient(180deg, rgba(127,29,29,.95), rgba(185,28,28,.92));
  border-color: rgba(239,68,68,.55);
  color: #fff1f1;
}

/* Efeito de destaque no botão Download após sucesso */
.pulse-success {
  animation: pulseGlow 1.3s ease-in-out 2;
}
@keyframes pulseGlow {
  0% { box-shadow: 0 0 0 0 rgba(34,197,94,.45) }
  70%{ box-shadow: 0 0 0 12px rgba(34,197,94,0) }
  100%{ box-shadow: 0 0 0 0 rgba(34,197,94,0) }
}
"""
        "</style>"
        "</head>"
        "<body>"
        "<div id='app'>"

        # Topbar
        "<div class='topbar'>"
          "<div class='left'>"
            "<a href='/' class='pill' title='Voltar para Página inicial' aria-label='Voltar para Página inicial'>⬅︎ "
              "<span class='label'>Página inicial</span>"
            "</a>"
          "</div>"
          "<div class='center'>"
            "<div class='title' style='font-weight:900; letter-spacing:.08em; text-transform:uppercase; color:#ffffff; font-size:18px;'>"
              "CONVERTER PDF → WORD"
            "</div>"
          "</div>"
          "<div class='right'>"
            "<button id='convert' class='pill secondary' disabled>"
              "<span class='btn-label'>Converter</span>"
              "<span class='spinner' aria-hidden='true'></span>"
            "</button>"
            "<a id='downloadLink' download='convertido.docx'>"
              "<button id='download' class='pill primary' disabled>Download</button>"
            "</a>"
          "</div>"
        "</div>"

        # Toolbar
        "<div class='toolbar'>"
          "<div class='group' role='group' aria-label='Opções de conversão'>"

            # Modo de conversão
            "<div class='tooltip-wrapper'>"
              "<label for='mode' class='tooltip-label'>Modo de Conversão:</label>"
              "<select id='mode' class='select-like' aria-describedby='mode-help' "
              "title='Selecione como o PDF será convertido'>"
                "<option value='layout'>Preservar Formatação (mais fiel)</option>"
                "<option value='texto'>Somente Texto (editável no Word)</option>"
              "</select>"
              "<div id='mode-help' class='tooltip-box' role='tooltip'>"
                "<strong>Preservar Formatação:</strong> mantém o layout do PDF (melhor para contratos e docs formatados).<br><br>"
                "<strong>Somente Texto:</strong> extrai apenas o texto, gerando DOCX limpo e fácil de editar."
              "</div>"
            "</div>"

            # OCR: Automático / Forçar / Sem
            "<div class='tooltip-wrapper'>"
                "<label for='ocr' class='tooltip-label'>OCR:</label>"
                "<select id='ocr' class='select-like' aria-describedby='ocr-help' "
                    "title='Controle do OCR para PDFs escaneados'>"
                    "<option value='auto' selected>Automático (recomendado)</option>"
                    "<option value='on'>Forçar OCR (Com OCR)</option>"
                    "<option value='off'>Sem OCR</option>"
                "</select>"
                "<div id='ocr-help' class='tooltip-box' role='tooltip'>"
                    "<strong>Com OCR:</strong> reconhece texto em PDFs escaneados para gerar DOCX editável.<br><br>"
                    "<em>a) Automático</em> aplica OCR somente quando necessário.<br>"
                    "<em>b) Forçar</em> aplica OCR sempre.<br>"
                    "<em>c) Sem OCR</em> desativa o reconhecimento (para PDFs nativos)."
                "</div>"
            "</div>"

            "<input id='pages' class='input-like' placeholder='Páginas (ex.: 1-3 ou 5)' title='Intervalo de páginas' />"
            "<input id='password' class='input-like' type='password' placeholder='Senha (se houver)' title='Senha do PDF (opcional)' />"
            "<input id='fileInput' type='file' accept='application/pdf' style='display:none' />"
          "</div>"
        "</div>"

        # Área de trabalho
        "<div id='workarea'>"
          "<div id='drop'>"
            "<label class='upload'>Selecionar arquivo PDF</label>"
            "<div class='hint'>"
              "Escolha o PDF e ajuste as opções acima. "
              "<b>Preservar Formatação</b> mantém o visual; <b>Somente Texto</b> gera DOCX limpo para edição."
            "</div>"
            "<div id='filename' class='filename'></div>"
            "<div id='status' class='status-hint'></div>"
          "</div>"
          "<div id='viewer'></div>"
        "</div>"

        "<div id='toast' class='toast' role='status' aria-live='polite'></div>"
        "</div>"

        "<script>"
        """
(() => {
  // --------- DOM ---------
  const fileInput = document.getElementById('fileInput');
  const convertBt = document.getElementById('convert');
  const convertLabel = convertBt.querySelector('.btn-label');
  const download  = document.getElementById('download');
  const dlLink    = document.getElementById('downloadLink');

  const modeEl    = document.getElementById('mode');
  const ocrEl     = document.getElementById('ocr');
  const pagesEl   = document.getElementById('pages');
  const passEl    = document.getElementById('password');

  const drop      = document.getElementById('drop');
  const uploadBtn = drop.querySelector('.upload');
  const filename  = document.getElementById('filename');
  const statusEl  = document.getElementById('status');
  const toast     = document.getElementById('toast');

  let fileBlob = null, lastURL = null;

  // --------- Helpers ---------
  function showToast(msg, type = "") {
    const icon = type === 'success' ? '✔' : (type === 'error' ? '!' : 'ℹ️');
    toast.innerHTML = `
      <div style="display:flex;align-items:center;gap:10px;">
        <span class="status-icon">${icon}</span>
        <div>${msg}</div>
      </div>`;
    toast.className = 'toast ' + (type || '');
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3500);
  }

  function setStatus(kind, html) {
    statusEl.className = "status-hint" + (kind ? (" " + kind) : "");
    statusEl.innerHTML = html || "";
  }

  function setBusy(on) {
  // botão + spinner
  convertBt.disabled = on || !fileBlob;
  convertBt.classList.toggle('loading', !!on);
  convertBt.setAttribute('aria-busy', on ? 'true' : 'false');
  if (convertLabel) convertLabel.textContent = on ? 'Convertendo...' : 'Converter';

  // trava/destrava controles
  modeEl.disabled = !!on; 
  ocrEl.disabled = !!on; 
  pagesEl.disabled = !!on; 
  passEl.disabled = !!on;

  // >>> NÃO MOSTRA NADA NO STATUS DURANTE O PROCESSAMENTO <<<
  // limpa conteúdo, classes e estilos pra não sobrar “ponto/bola”
  const s = document.getElementById('status');
  s.className = "status-hint";
  s.innerHTML = "";
  s.removeAttribute('style');   // remove inline styles (display, width, etc.)
}


  function ensureFile() {
    if (!fileBlob) {
      setStatus("err", `
        <div class="status-row">
          <span class="status-icon">!</span>
          <div><strong>Nenhum arquivo.</strong><br><small>Selecione um PDF para continuar.</small></div>
        </div>
      `);
      showToast("Necessário selecionar um PDF", "error");
      return false;
    }
    return true;
  }

  function setFilename(f) {
    filename.textContent = f ? ("📄 " + f) : "";
  }

  function resetResult() {
    if (lastURL) { URL.revokeObjectURL(lastURL); lastURL = null; }
    download.disabled = true;
    dlLink.removeAttribute('href');
  }

  function formatBytes(bytes){
    if (!bytes && bytes !== 0) return "";
    const units = ["B","KB","MB","GB","TB"];
    let i = 0, num = bytes;
    while (num >= 1024 && i < units.length-1) { num /= 1024; i++; }
    return (Math.round(num*10)/10) + " " + units[i];
  }

  // --------- Upload ----------
  uploadBtn.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', (e) => {
    const f = e.target.files && e.target.files[0];
    if (!f) return;
    fileBlob = f;
    setFilename(f.name);
    convertBt.disabled = false;
    resetResult();
    setStatus("ok", `
      <div class="status-row" style="gap:8px;align-items:center;">
        <span class="status-icon" style="width:20px;height:20px;font-size:12px;">✔</span>
        <div>
          <strong>Arquivo pronto.</strong><br>
          <small>${formatBytes(f.size)}</small>
        </div>
      </div>
    `);

    // >>> força o card a ficar pequeno e centralizado <<<
    const s = document.getElementById('status');
    s.style.display   = 'inline-flex';
    s.style.alignItems= 'center';
    s.style.gap       = '8px';
    s.style.width     = 'auto';
    s.style.maxWidth  = '320px';   // ajuste aqui: 260/320/420 etc.
    s.style.margin    = '12px auto 0';
    s.style.padding   = '10px 14px';
    s.style.borderRadius = '14px';


  });

  // Drag & Drop
  ['dragenter','dragover'].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.style.opacity = .9; }));
  ['dragleave','drop'].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.style.opacity = 1; }));
  drop.addEventListener('drop', (e) => {
    e.preventDefault();
    const f = e.dataTransfer.files && e.dataTransfer.files[0];
    if (f) {
      fileBlob = f;
      setFilename(f.name);
      convertBt.disabled = false;
      resetResult();
      setStatus("ok", `
        <div class="status-row">
          <span class="status-icon">✔</span>
          <div><strong>Arquivo pronto.</strong><br><small>${formatBytes(f.size)}</small></div>
        </div>
      `);
    }
  });

  // --------- Converter ----------
  convertBt.addEventListener('click', async () => {
    if (!ensureFile()) return;

    const p = (pagesEl.value||'').trim();
    if (p && !/^\\d+(-\\d+)?$/.test(p)) {
      setStatus('err', `
        <div class="status-row">
          <span class="status-icon">!</span>
          <div><strong>Páginas inválidas.</strong><br><small>Use 1-3 ou 5.</small></div>
        </div>
      `);
      showToast('Páginas inválidas. Use 1-3 ou 5.', 'error');
      return;
    }

    setBusy(true);

    const fd = new FormData();
    fd.append('file', fileBlob);
    fd.append('mode', modeEl.value);
    if (p) fd.append('pages', p);
    if ((passEl.value||'').trim()) fd.append('password', passEl.value.trim());
    fd.append('ocr', (ocrEl?.value || 'auto'));   // auto | on | off
    fd.append('ocr_lang', 'por');                 // idioma padrão

    try {
      const res = await fetch('/api/convert/word', { method:'POST', body: fd });
      if (!res.ok) {
        let detail = '';
        try { const j = await res.json(); detail = j.detail || j.message || ''; } catch(_){}
        throw new Error(detail || ('Falha na conversão (HTTP ' + res.status + ').'));
      }
      const blob = await res.blob();
      lastURL = URL.createObjectURL(blob);
      const base = (fileBlob.name || 'saida.pdf').replace(/\\.pdf$/i, '') || 'saida';
      dlLink.href = lastURL;
      dlLink.download = base + '.docx';
      download.disabled = false;

      // --- MENSAGENS MODERNAS: SUCESSO ---
      setStatus("ok", `
        <div class="status-row">
          <span class="status-icon">✔</span>
          <div>
            <strong>Conversão concluída!</strong><br>
            <small>O arquivo está pronto para download.</small>
          </div>
        </div>
      `);
      showToast("Arquivo convertido com sucesso! Você já pode baixar o Word.", "success");

      // realce temporário no botão Download
      download.classList.add('pulse-success');
      setTimeout(() => download.classList.remove('pulse-success'), 2000);

    } catch (err) {
      // --- MENSAGENS MODERNAS: ERRO ---
      const detail = (err && (err.message || err.toString())) || "Falha desconhecida.";
      setStatus("err", `
        <div class="status-row">
          <span class="status-icon">!</span>
          <div>
            <strong>Falha na conversão.</strong><br>
            <small>${detail}</small>
          </div>
        </div>
      `);
      showToast("Não foi possível converter o PDF. Verifique o arquivo e tente novamente.", "error");
    } finally {
      setBusy(false);
    }
  });

  // --------- Altura útil (igual Editar) ----------
  function resizeWorkarea(){
    const work   = document.getElementById('workarea');
    const topbar = document.querySelector('.topbar');
    const toolbar= document.querySelector('.toolbar');
    const avail = window.innerHeight
      - (topbar?.offsetHeight || 0)
      - (toolbar?.offsetHeight || 0)
      - 16;
    const maxH = Math.max(320, avail);
    work.style.setProperty('--workarea-max', maxH + 'px');
    work.style.maxHeight = maxH + 'px';
  }
  window.addEventListener('resize', resizeWorkarea);
  window.addEventListener('load', resizeWorkarea);
  resizeWorkarea();
})();
"""
        "</script>"
        "</body>"
        "</html>"
    )
    return HTMLResponse(html)
