# frontend/ui_css.py
CSS_EDITOR = r"""
:root{
  --bg:#eef1f6; --ink:#0f172a; --panel:#0b1320; --panel2:#0f172a;
  --muted:#94a3b8; --accent:#e64040; --cyan:#38bdf8;
}
*{box-sizing:border-box}

/* ====== PÁGINA COM SCROLL + VIEWER COM SCROLL PRÓPRIO ====== */
html, body { height: 100%; }
body{
  margin:0; background:var(--bg); color:var(--ink);
  font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu;
  overflow:auto; /* página pode rolar */
}
#app{
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
/* Só o PDF rola internamente; altura calculada via JS */
#workarea{
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  max-height: var(--workarea-max, 70vh); /* fallback se JS não rodar */
  padding: 10px 0 24px;
}
#workarea > * { padding-left: 8px; padding-right: 8px; }

/* ====== TOPBAR ====== */
.topbar{
  display:grid; grid-template-columns:1fr auto 1fr; align-items:center;
  gap:.75rem; background:var(--panel); color:#e5e7eb;
  padding:10px 14px; box-shadow:0 1px 0 #1e293b; z-index:9;
  position:sticky; top:0;
}
.topbar .left{display:flex; gap:.5rem; align-items:center}
.topbar .center{justify-self:center}
.topbar .right{justify-self:end; display:flex; gap:.55rem; align-items:center}

.pill{
  display:inline-flex; align-items:center; gap:.55rem;
  padding:.58rem 1rem; border-radius:999px; text-decoration:none; color:#e5e7eb;
  background:linear-gradient(180deg, rgba(255,255,255,.07), rgba(255,255,255,.03));
  border:1px solid rgba(148,163,184,.28);
  backdrop-filter: blur(6px);
  box-shadow:0 2px 12px rgba(0,0,0,.25), inset 0 1px 0 rgba(255,255,255,.05);
  transition: transform .15s ease, border-color .15s ease, box-shadow .15s ease, color .15s ease, background .15s ease;
  cursor:pointer; font-weight:700; letter-spacing:.01em; white-space:nowrap;
}
.pill:hover{ transform: translateY(-1px); border-color: rgba(148,163,184,.45); box-shadow:0 6px 18px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.06); color:#fff; }
.pill:disabled{opacity:.55; cursor:not-allowed}
.pill.primary{ background:linear-gradient(180deg, rgba(56,97,255,.35), rgba(56,97,255,.18)); border-color:rgba(99,102,241,.55) }
.pill.secondary{ background:linear-gradient(180deg, rgba(148,163,184,.22), rgba(148,163,184,.10)); }
.pill.danger{ background:linear-gradient(180deg, rgba(239,68,68,.35), rgba(239,68,68,.18)); border-color:rgba(239,68,68,.55); color:#fff }

.icon-btn{
  width:38px; height:38px; border:1px solid #334155; border-radius:10px;
  background:#1f2937; color:#e5e7eb; display:flex; align-items:center; justify-content:center;
  cursor:pointer; transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease;
}
.icon-btn:active{ transform:translateY(1px) }

/* ===== Sub-barra (Ferramentas) ===== */
.toolbar{ display:flex; justify-content:center; padding:10px;
          background:linear-gradient(180deg,rgba(0,0,0,.10),rgba(0,0,0,0)); z-index:8; position:sticky; top:62px; }
.group{ display:flex; gap:.5rem; background:var(--panel2); padding:.4rem; border-radius:14px; border:1px solid #253046; box-shadow:0 6px 20px rgba(0,0,0,.20) }
.gbtn{
  display:inline-flex; align-items:center; gap:.5rem;
  border:1px solid #334155; background:#1f2937; color:#e5e7eb;
  height:38px; padding:0 .9rem; border-radius:10px; cursor:pointer; user-select:none;
  transition:transform .15s ease, box-shadow .15s ease, border-color .15s ease;
}
.gbtn[aria-pressed="true"]{ background:#0b2a3a; border-color:#22d3ee; box-shadow:0 0 0 2px rgba(34,211,238,.25) inset; }
.select-like{ height:38px; border-radius:10px; border:1px solid #334155; background:#1f2937; color:#e5e7eb; padding:0 .7rem }

/* ===== Painel de Texto ===== */
.text-panel{ display:none; justify-content:center; padding:8px 10px 12px; position:sticky; top:112px; z-index:7; }
.text-panel.visible{ display:flex; }
.text-panel .panel-inner{
  width: clamp(480px, 45vw, 700px);
  background:#0f172a; border:1px solid #253046; border-radius:14px;
  box-shadow:0 8px 24px rgba(0,0,0,.25); padding:8px 10px 10px; color:#e2e8f0; margin:0 auto;
}
.tp-row{ display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
.tp-select{ height:32px; border-radius:8px; border:1px solid #334155; background:#111827; color:#e5e7eb; padding:0 .6rem; }
.tp-btn{ height:32px; min-width:32px; display:inline-flex; align-items:center; justify-content:center; border-radius:8px; border:1px solid #334155; background:#111827; color:#e5e7eb; cursor:pointer; padding:0 .5rem; }
.tp-btn[aria-pressed="true"]{ background:#0b2a3a; border-color:#22d3ee }
.tp-color{ height:32px; width:42px; padding:0; border-radius:8px; border:1px solid #334155; background:#111827 }

/* Viewer */
#drop{margin:20px auto 10px; width:760px; max-width:92%; text-align:center}
.upload{
  position: relative;
  display:inline-block; background:var(--accent); color:#fff; padding:20px 28px; border-radius:14px; font-weight:900; font-size:28px;
  box-shadow:0 12px 30px rgba(230,64,64,.35);
  cursor:pointer; overflow:hidden;
  transition: transform .18s ease, box-shadow .18s ease, background-color .18s ease, filter .18s ease;
  will-change: transform, box-shadow, filter;
}
.upload:hover{ transform: translateY(-1px) scale(1.035); box-shadow: 0 18px 40px rgba(230,64,64,.45); filter: brightness(1.03); }
.upload::after{
  content:""; position:absolute; inset:0; border-radius:inherit;
  background: radial-gradient(120% 120% at 50% -20%, rgba(255,255,255,.25), transparent 60%);
  opacity:0; transition:opacity .18s ease; pointer-events:none;
}
.upload:hover::after{ opacity:.45; }
.hint { color: var(--muted); margin-top: 25px; font-size: 16px; }

#viewer{padding:18px; display:flex; flex-direction:column; gap:18px; align-items:center}
.page-wrap{position:relative; display:inline-block; background:#0b0f18; border-radius:8px; overflow:hidden;
           box-shadow:0 0 0 1px #1f2937, 0 10px 30px rgba(0,0,0,.35)}
.overlay{position:absolute; inset:0}

.selected{ outline:2px solid #22d3ee; outline-offset:1px }
/* ... mantém o que já existe acima ... */

/* Campo genérico */
.field-box{
  position:absolute;
  border:2px solid var(--cyan);
  background:rgba(56,189,248,.10);
  border-radius:6px;
  resize:both; overflow:auto; cursor:move; 
  min-width:40px; min-height:22px;
}
}

/* Mantém o estilo do checkbox (quadrado) */
.field-box.field-checkbox { 
  border-style:dashed; 
}

/* Mantém a seleção padrão para os NÃO-circulares */
.selected{ 
  outline:2px solid #22d3ee; 
  outline-offset:1px; 
}

.text-box{
  position:absolute; background:rgba(255,255,255,.95); border:1px solid #cbd5e1; color:#0f172a;
  min-width:60px; min-height:28px; padding:4px 6px; resize:both; overflow:auto; cursor:text; border-radius:6px;
  white-space: pre-wrap;
}
.img-box{ position:absolute; min-width:40px; min-height:40px; cursor:move; resize:both; overflow:hidden; border-radius:6px; border:1px dashed #9aa4b2; background:rgba(255,255,255,.6) }
.img-box img{ width:100%; height:100%; object-fit:contain; display:block }

.rubber{ position:absolute; border:2px dashed #22d3ee; background:rgba(34,211,238,.10); border-radius:6px; pointer-events:none; }

.toast {
  visibility: hidden;
  min-width: 200px;      /* largura mínima menor (padrão costuma ser 300px+) */
  max-width: 300px;      /* opcional: limitar largura máxima */
  background-color: #333; 
  color: #fff;
  text-align: center;
  border-radius: 6px;
  padding: 8px 12px;     /* menos padding = caixa menor */
  position: fixed;
  z-index: 9999;
  left: 50%;
  bottom: 100px;
  font-size: 12px;       /* diminui o tamanho da fonte */
  transform: translateX(-50%);
  opacity: 0;
  transition: opacity 0.5s, bottom 0.5s;
}

.toast.show {
  visibility: visible;
  opacity: 1;
  bottom: 140px;
}

.toast.error {
  background-color: #FAA61A !important;
  color: #ffffff !important;
}

.toast.success {
  background-color: green !important;
  color: white !important;
}


"""