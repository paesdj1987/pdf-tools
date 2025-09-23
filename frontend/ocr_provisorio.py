# frontend/ocr_provisorio.py
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/ocr", response_class=HTMLResponse)
def ocr_placeholder():
    return """
<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<title>OCR PDF - Em construção</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  body {
    margin:0; padding:0;
    font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,sans-serif;
    background:#0b0f16; color:#e9eef5;
    display:flex; flex-direction:column;
    justify-content:center; align-items:center;
    height:100vh; text-align:center;
  }
  h1 {
    font-size:clamp(24px, 4vw, 36px);
    margin-bottom:12px;
  }
  p {
    color:#9aa4b2;
    font-size:16px;
    margin-bottom:24px;
  }
  a.btn {
    display:inline-block;
    padding:10px 18px;
    border-radius:12px;
    border:1px solid rgba(239,91,42,.55);
    background:linear-gradient(180deg, rgba(239,91,42,.95), rgba(239,91,42,.80));
    color:#fff; font-weight:600; text-decoration:none;
    box-shadow:0 6px 20px rgba(239,91,42,.35);
    transition:transform .15s ease, box-shadow .15s ease;
  }
  a.btn:hover {
    transform:translateY(-2px);
    box-shadow:0 10px 28px rgba(239,91,42,.45);
  }
</style>
</head>
<body>
  <h1>🚧 Página em construção 🚧</h1>
  <p>A funcionalidade de OCR (Reconhecimento de Texto) estará disponível em breve.</p>
  <a class="btn" href="/">Voltar para a página inicial</a>
</body>
</html>
"""
