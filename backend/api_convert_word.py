# backend/api_convert_word.py
from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from typing import Optional, Tuple, List
import os, re, tempfile, shutil, subprocess, sys
import fitz  # PyMuPDF
from pdf2docx import Converter
from docx import Document
from docx.shared import Pt

router = APIRouter()

# ======================== Utilidades ========================

def _secure_filename(name: str) -> str:
    name = os.path.basename(name or "arquivo.pdf")
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)
    if not name.lower().endswith(".pdf"):
        name += ".pdf"
    return name

def _parse_pages(pages_str: Optional[str], num_pages: int) -> Tuple[int, int]:
    """Aceita '1-3' ou '5'. Retorna (start, end) base 0."""
    if not pages_str:
        return (0, num_pages - 1)
    s = pages_str.strip().replace(" ", "")
    if "-" in s:
        a, b = s.split("-", 1)
        start, end = int(a) - 1, int(b) - 1
    else:
        start, end = int(s) - 1, int(s) - 1
    start = max(0, min(start, num_pages - 1))
    end = max(0, min(end, num_pages - 1))
    if start > end:
        start, end = end, start
    return (start, end)

def _open_pdf(path: str, password: Optional[str]) -> fitz.Document:
    """Abre PDF com senha opcional."""
    try:
        doc = fitz.open(path)
        if doc.is_encrypted and not doc.authenticate(password or ""):
            raise HTTPException(status_code=401, detail="Senha incorreta para o PDF.")
        return doc
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Falha ao abrir o PDF.")

def _page_has_text(page: fitz.Page, min_chars:int=20) -> bool:
    txt = page.get_text("text") or ""
    txt = re.sub(r"\s+", "", txt)
    return len(txt) >= min_chars

def _needs_ocr(doc: fitz.Document, start:int, end:int, threshold:float=0.7) -> bool:
    """
    Retorna True se >= threshold das páginas no intervalo não tiverem texto extraível.
    """
    total = max(1, end - start + 1)
    no_text = 0
    for i in range(start, end + 1):
        if not _page_has_text(doc.load_page(i)):
            no_text += 1
    return (no_text / total) >= threshold

def _save_subset(doc: fitz.Document, start:int, end:int, out_pdf:str):
    """Salva somente as páginas [start..end] num PDF novo (mais rápido para OCR)."""
    new = fitz.open()
    new.insert_pdf(doc, from_page=start, to_page=end)
    new.save(out_pdf)
    new.close()

def _which_ghostscript() -> Optional[str]:
    import shutil as _sh
    for name in ("gs", "gswin64c", "gswin32c"):
        if _sh.which(name):
            return name
    return None

def _split_langs(ocr_lang: str) -> List[str]:
    s = (ocr_lang or "").strip()
    if not s:
        return []
    return [p.strip() for p in s.split("+") if p.strip()]

def _check_ocr_preflight(ocr_lang: str):
    """
    Checa presença de tesseract e ghostscript no PATH.
    Se algum faltar, levanta HTTP 501 com instruções curtas.
    """
    import shutil as _sh
    tess = _sh.which("tesseract")
    gs = _which_ghostscript()

    missing = []
    if not tess:
        missing.append("tesseract")
    if not gs:
        missing.append("ghostscript")

    if missing:
        where = "Windows" if sys.platform.startswith("win") else "Linux"
        detail = (
            "OCR indisponível. Faltam dependências: "
            + ", ".join(missing)
            + (". " if where == "Windows" else ". ")
        )
        if where == "Windows":
            detail += (
                "No Windows, instale Tesseract (UB Mannheim) e Ghostscript e garanta o PATH:\n"
                " - Tesseract: C:\\Program Files\\Tesseract-OCR\n"
                " - Ghostscript: C:\\Program Files\\gs\\<versão>\\bin\n"
                "Depois reinicie o terminal/servidor."
            )
        else:
            detail += "Instale via gerenciador de pacotes (ex.: apt/yum) e reinicie o serviço."
        raise HTTPException(status_code=501, detail=detail)

    # Checagem rápida do idioma principal
    langs = _split_langs(ocr_lang or "por")
    if sys.platform.startswith("win"):
        tessdata = os.getenv("TESSDATA_PREFIX") or r"C:\Program Files\Tesseract-OCR\tessdata"
        if os.path.isdir(tessdata):
            for lg in langs:
                path = os.path.join(tessdata, f"{lg}.traineddata")
                if not os.path.exists(path):
                    pass

def _run_ocr(in_pdf: str, out_pdf: str, lang: str = "por", force_ocr: bool = True):
    """
    Executa OCR usando ocrmypdf. Tenta via import; se não existir, tenta subprocess.
    Força a apontar Ghostscript correto em Windows quando necessário.
    """
    _check_ocr_preflight(lang)

    env = os.environ.copy()
    gs = _which_ghostscript()
    if gs and sys.platform.startswith("win") and "gs" not in gs:
        env["GS"] = gs

    try:
        import ocrmypdf
        ocrmypdf.ocr(
            in_pdf,
            out_pdf,
            language=lang,
            force_ocr=force_ocr,
            deskew=True,
            optimize=1,
            progress_bar=False,
            env=env,
        )
        return
    except Exception:
        pass

    # Subprocess (fallback)
    cmd = [
        "ocrmypdf",
        "--language", lang,
        "--deskew",
        "--optimize", "1",
        "--force-ocr" if force_ocr else "--skip-text",
        in_pdf,
        out_pdf,
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    except subprocess.CalledProcessError as e:
        std = (e.stderr or b"").decode(errors="ignore")
        if "language data" in std.lower():
            raise HTTPException(
                status_code=501,
                detail=("OCR indisponível: faltam dados de idioma do Tesseract (ex.: 'por'). "
                        "Instale o arquivo .traineddata correspondente e tente novamente.")
            )
        raise HTTPException(
            status_code=501,
            detail=("Falha ao executar o OCR. Verifique Tesseract/Ghostscript no PATH. "
                    f"Detalhe: {std[:400]}")
        )
    except Exception as e:
        raise HTTPException(
            status_code=501,
            detail=("OCR indisponível. Instale 'ocrmypdf' e o Tesseract + Ghostscript. "
                    f"Detalhe: {e}")
        )

# ======================== Conversões ========================

def _convert_layout(pdf_path: str, out_docx: str, start: int, end: int):
    """Modo layout - usa pdf2docx (mais fiel ao visual)."""
    try:
        cv = Converter(pdf_path)
        cv.convert(out_docx, start=start, end=end)
        cv.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha na conversão (layout): {e}")

def _convert_text(doc: fitz.Document, out_docx: str, start: int, end: int):
    """Modo texto - usa python-docx (gera DOCX limpo e fácil de editar)."""
    try:
        docx = Document()
        style = docx.styles["Normal"]
        style.font.name = "Calibri"
        style.font.size = Pt(11)
        for i in range(start, end + 1):
            page = doc.load_page(i)
            text = page.get_text("text") or ""
            if not text.strip():
                docx.add_paragraph("[Página sem texto extraível]")
            else:
                for line in text.splitlines():
                    docx.add_paragraph(line)
            if i < end:
                docx.add_page_break()
        docx.save(out_docx)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha na conversão (texto): {e}")

# ======================== Endpoint ========================

@router.post("/convert/word")
async def convert_pdf_to_word(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    mode: str = Form("layout"),            
    pages: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    ocr: str = Form("auto"),              
    ocr_lang: str = Form("por"),          
):
    """
    Converte PDF para Word (.docx), aplicando OCR conforme opção:
    - ocr='auto' : detecta PDF escaneado no intervalo e aplica OCR antes (recomendado)
    - ocr='on'   : sempre aplica OCR antes
    - ocr='off'  : nunca aplica OCR
    Se OCR for aplicado e o modo for 'layout', rodamos pdf2docx no PDF OCRizado (preserva visual e torna texto selecionável).
    """
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=415, detail="Envie um arquivo PDF válido.")

    tmpdir = tempfile.mkdtemp(prefix="pdf2word_")
    background_tasks.add_task(lambda: shutil.rmtree(tmpdir, ignore_errors=True))

    # salva upload
    in_name = _secure_filename(file.filename or "arquivo.pdf")
    pdf_path = os.path.join(tmpdir, in_name)
    with open(pdf_path, "wb") as f:
        f.write(await file.read())

    # abre PDF e páginas
    doc = _open_pdf(pdf_path, password)
    start, end = _parse_pages(pages, doc.page_count)
    out_docx = os.path.join(tmpdir, os.path.splitext(in_name)[0] + ".docx")

    # Decide se roda OCR
    run_ocr = (ocr == "on") or (ocr == "auto" and _needs_ocr(doc, start, end))
    pdf_for_layout = pdf_path
    text_doc = doc
    layout_start, layout_end = start, end
    text_start, text_end = start, end

    if run_ocr:
        subset_pdf = os.path.join(tmpdir, "subset.pdf")
        _save_subset(doc, start, end, subset_pdf)

        ocr_pdf = os.path.join(tmpdir, "subset_ocr.pdf")
        _run_ocr(subset_pdf, ocr_pdf, lang=ocr_lang, force_ocr=True)

        pdf_for_layout = ocr_pdf
        with fitz.open(ocr_pdf) as od:
            layout_start, layout_end = 0, od.page_count - 1

        text_doc = fitz.open(ocr_pdf)
        text_start, text_end = 0, text_doc.page_count - 1

    # Converte conforme o modo solicitado
    if mode == "layout":
        _convert_layout(pdf_for_layout, out_docx, layout_start, layout_end)
    elif mode == "texto":
        _convert_text(text_doc, out_docx, text_start, text_end)
    else:
        raise HTTPException(status_code=422, detail="Modo inválido. Use 'layout' ou 'texto'.")

    headers = {"Content-Disposition": f'attachment; filename="{os.path.basename(out_docx)}"'}
    return FileResponse(
        out_docx,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers,
    )
