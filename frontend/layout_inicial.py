from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def home():
    return """
<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<title>Ferramenta online para edição de PDF</title>
<meta name="viewport" content="width=device-width, initial-scale=1">

<style>
  :root{
    --bg:#0b0f16; --panel:#0b0e13; --ink:#e9eef5; --muted:#9aa4b2;
    --cta:#ef5b2a; --glow:rgba(239,91,42,.35);
    --card:#0f141d; --card-border:#263244;
    --aurora1:#7c3aed; --aurora2:#22d3ee; --aurora3:#f59e0b; --aurora4:#ef4444;
  }

  *{box-sizing:border-box}
  html,body{height:100%}
  body{
    margin:0; font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu;
    color:var(--ink); background:
      radial-gradient(1200px 700px at 80% -10%, rgba(124,58,237,.10), transparent),
      radial-gradient(1000px 700px at -10% -10%, rgba(34,211,238,.08), transparent),
      linear-gradient(180deg, rgba(11,15,22,1) 0%, rgba(11,15,22,0.95) 100%);
    overflow-x:hidden;
  }
  body::before{
    content:""; position:fixed; inset:0; pointer-events:none;
    background: radial-gradient(circle at 1px 1px, rgba(255,255,255,.06) 1px, transparent 1px);
    background-size:16px 16px; opacity:.25;
  }

  /* Topbar */
  .topbar{
    position:sticky; top:0; z-index:10;
    display:flex; align-items:center; gap:12px;
    padding:10px 16px; background:rgba(11,14,19,.8);
    backdrop-filter: blur(8px);
    box-shadow:0 1px 0 #1b2432;
  }
  .topbar .left img{height:60px; object-fit:contain; display:block}

  /* Hero */
  .hero{
    position:relative; max-width:980px; margin:10px auto 22px; /* subimos um pouco */
    padding:28px 24px; text-align:center; border-radius:24px;
    background:linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.02));
    border:1px solid #1f2a3a;
    box-shadow:0 10px 40px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.04);
    overflow:hidden; z-index:1;
  }
  .hero::before{
    content:""; position:absolute; inset:-30%;
    background: conic-gradient(from 180deg at 50% 50%, var(--aurora1), var(--aurora2), var(--aurora3), var(--aurora4), var(--aurora1));
    filter: blur(64px); opacity:.18; animation: aurora 16s linear infinite; pointer-events:none;
  }
  @keyframes aurora{ to{ transform:rotate(360deg);} }

  h1{margin:0 0 10px; font-size:clamp(26px, 4.2vw, 36px); letter-spacing:.02em}
  p.sub{margin:0 auto; max-width:760px; color:var(--muted); line-height:1.6}

  .cta{margin-top:18px}
  .btn{
    display:inline-block; text-decoration:none; color:#fff; font-weight:700;
    padding:.85rem 1.25rem; border-radius:12px; border:1px solid rgba(239,91,42,.55);
    background:linear-gradient(180deg, rgba(239,91,42,.95), rgba(239,91,42,.80));
    box-shadow:0 10px 28px var(--glow), inset 0 1px 0 rgba(255,255,255,.18);
    transition: transform .15s ease, box-shadow .15s ease, filter .15s ease;
  }
  .btn:hover{ transform: translateY(-1px); filter:brightness(1.02);
              box-shadow:0 16px 38px var(--glow), inset 0 1px 0 rgba(255,255,255,.22); }

  .btn-manual {
    background: linear-gradient(180deg, #FAA61A, #e88c00); /* laranja */
    border: 1px solid #e88c00;
    box-shadow: 0 10px 28px rgba(250,166,26,.35), inset 0 1px 0 rgba(255,255,255,.18);
  }
  .btn-manual:hover {
    filter: brightness(1.05);
    box-shadow: 0 16px 38px rgba(250,166,26,.45), inset 0 1px 0 rgba(255,255,255,.22);
  }


  /* Grid de cards (2 col quando couber) */
  .home-grid{
    display:grid; gap:18px; width:100%; max-width:980px; margin:14px auto 64px; padding:0 12px;
    grid-template-columns:1fr;
  }
  @media (min-width: 880px){ .home-grid{ grid-template-columns:1fr 1fr; } }

  .card{
    width:100%;
    border-radius:18px;
    padding:22px 22px 20px;
    background: linear-gradient(180deg, rgba(255,255,255,.03), rgba(255,255,255,.015));
    border:1px solid var(--card-border);
    box-shadow: 0 12px 40px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.05);
    position:relative; transform-style:preserve-3d;
    transition: transform .18s cubic-bezier(.2,.8,.2,1), box-shadow .18s ease, border-color .18s ease;
    display: flex;
    flex-direction: column;
    justify-content: space-between; /* empurra o botão pro fim */
    min-height: 230px; /* ajuste opcional pra garantir uniformidade */
  }
  /* NOVO BLOCO - uniformiza altura e alinhamento interno */
  .card h3,
  .card p {
    text-align: left;        /* mantém alinhado à esquerda */
  }

  .card h3 {
    min-height: 28px;        /* garante altura fixa do título */
  }

  .card p {
    min-height: 48px;        /* força mesmo espaço entre cards */
    display: flex;
    align-items: flex-start;  /* texto sempre inicia alinhado em cima */
  }
  .card::before{
    content:""; position:absolute; inset:0; border-radius:inherit; padding:1px;
    background: linear-gradient(135deg, rgba(124,58,237,.45), rgba(34,211,238,.35));
    -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
    -webkit-mask-composite: xor; mask-composite: exclude; opacity:.55; pointer-events:none;
    transition: opacity .18s ease;
  }
  .card:hover{
    transform: perspective(800px) rotateX(4deg) rotateY(-3deg) translateY(-2px);
    box-shadow: 0 18px 52px rgba(0,0,0,.45), 0 0 0 1px rgba(130,180,255,.15) inset;
    border-color:#3a4e6a;
  }
  .card:hover::before{ opacity:.9 }

  .icon {
    width: 40px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    color: #fff;
    background: linear-gradient(135deg, #4ade80, #22c55e);
    box-shadow: 0 4px 14px rgba(34, 197, 94, 0.25);
  }

  /* ---- Cores ---- */
  .icon.edit,
  .icon.ocr,
  .icon.word,
  .icon.excel {
    background: linear-gradient(135deg, #e5e7eb, #d1d5db); /* cinza claro moderno */
    box-shadow: 0 4px 14px rgba(229, 231, 235, 0.25);       /* sombra suave */
    color: #1e293b; /* opcional: melhora contraste de ícones escuros */
  }


  .card h3{ margin:12px 0 6px; font-size:22px }
  .card p{ margin:0; color:var(--muted) }
  .actions{ margin-top:14px }
  .btn.outline{
    background:transparent; color:#dbe5f4; border:1px solid #2a3648; box-shadow:none;
  }
  .btn.outline:hover{
    border-color:#4d6b94; box-shadow:0 10px 24px rgba(77,107,148,.20), inset 0 1px 0 rgba(255,255,255,.05);
    transform:translateY(-1px);
  }

  .fade-in{ animation:fade .28s ease-out both }
  @keyframes fade{ from{opacity:0; transform:translateY(6px)} to{opacity:1; transform:none} }
  @media (prefers-reduced-motion: reduce){
    .hero::before, .card:hover{ animation:none; transform:none }
    .fade-in{ animation:none }
  }
</style>
</head>
<body>

  <div class="topbar">
    <div class="left">
      <img src="/assets/logo.png" alt="Logo">
    </div>
  </div>

  <section class="hero fade-in" style="animation-delay:.02s">
    <h1>Ferramenta online para edição de PDF</h1>
    <p class="sub">Ferramenta online e gratuita para os colaboradores da OR Empreendimentos poderem editar PDF. Não requer instalação.</p>
    <div class="cta">
      <a id="btnManual" class="btn btn-manual" href="/assets/manual.pdf" download="Manual_de_Utilizacao.pdf">
        Manual de Utilização
      </a>
    </div>
  </section>

    <section class="home-grid fade-in" style="animation-delay:.06s">

    <!-- Card 1: Editar PDF -->
    <div class="card" id="tool-card">
      <div class="icon edit"><img src="/assets/editpdf.png" alt="Editar" style="width:24px;height:24px;object-fit:contain;"></div>
      <h3>Editar PDF</h3>
      <p>Insira Texto, Imagem, Campo de Seleção de Texto e Remova Texto/Imagem no PDF.</p>
      <div class="actions"><a class="btn outline" href="/editar">Abrir</a></div>
    </div>

    <!-- Card 2: OCR -->
    <div class="card">
      <div class="icon ocr"><img src="/assets/ocr.png" alt="OCR" style="width:24px;height:24px;object-fit:contain;"></div>
      <h3>OCR PDF</h3>
      <p>Converta um PDF escaneado em documento pesquisável.</p>
      <div class="actions"><a class="btn outline" href="/ocr">Abrir</a></div>
    </div>

    <!-- Card 3: PDF → Word -->
    <div class="card">
      <div class="icon word"><img src="/assets/word.png" alt="Word" style="width:24px;height:24px;object-fit:contain;"></div>
      <h3>Converter PDF para Word</h3>
      <p>Gere um arquivo .docx a partir do seu PDF (modo layout ou texto).</p>
      <div class="actions"><a class="btn outline" href="/converter-word">Abrir</a></div>
    </div>

    <!-- Card 4: PDF → Excel -->
    <div class="card">
      <div class="icon excel"><img src="/assets/excel.png" alt="Excel" style="width:24px;height:24px;object-fit:contain;"></div>
      <h3>Converter PDF para Excel</h3>
      <p>Extraia tabelas do PDF e exporte para planilha .xlsx.</p>
      <div class="actions"><a class="btn outline" href="/converter-excel">Abrir</a></div>
    </div>



  </section>


  <script>
    // Tilt 3D suave no card principal (sem libs)
    (() => {
      const el = document.getElementById('tool-card');
      if(!el) return;
      let rect = null;
      const maxTilt = 6;
      const onMove = (e) => {
        rect = rect || el.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width;
        const y = (e.clientY - rect.top) / rect.height;
        const rx = (y - .5) * -maxTilt;
        const ry = (x - .5) *  maxTilt;
        el.style.transform = `perspective(800px) rotateX(${rx}deg) rotateY(${ry}deg) translateY(-2px)`;
      };
      const reset = () => { el.style.transform = ""; rect = null; };
      el.addEventListener('mousemove', onMove);
      el.addEventListener('mouseleave', reset);
      window.addEventListener('scroll', () => rect = null, {passive:true});
      window.addEventListener('resize', () => rect = null);
    })();
  </script>

</body>
<script>
(function(){
  const btn = document.getElementById('btnManual');
  if(!btn) return;

  // Efeito hover extra (pedido)
  btn.addEventListener('mousemove', (e) => {
    const r = btn.getBoundingClientRect();
    const x = e.clientX - r.left, y = e.clientY - r.top;
    btn.style.setProperty('--mx', x+'px');
    btn.style.setProperty('--my', y+'px');
  });

  // Fallback: força download via fetch+blob (se o atributo download não funcionar)
  btn.addEventListener('click', async (ev) => {
    ev.preventDefault();
    try{
      const res = await fetch(btn.getAttribute('href'), { cache: 'no-store' });
      if(!res.ok) throw new Error('Manual não encontrado em /assets/manual.pdf');
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = btn.getAttribute('download') || 'Manual_de_Utilizacao.pdf';
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    }catch(err){
      alert(err.message || err);
    }
  });
})();
</script>
</html>
"""
