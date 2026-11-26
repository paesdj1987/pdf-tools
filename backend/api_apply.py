from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
import tempfile, os, json, base64, re, math
import fitz  # PyMuPDF
import traceback

router = APIRouter()

# -------------------------- Utils ------------------------

def _safe_tmp_copy(upload: UploadFile) -> str:
    ext = os.path.splitext(upload.filename or "")[1] or ".pdf"
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        src = tmp.name
        tmp.write(upload.file.read())
    return src

def _parse_json(s: str, default):
    try:
        if s is None:
            return default
        return json.loads(s)
    except Exception:
        return default

def _hex_to_rgb01(s: str):
    """
    Aceita: #RRGGBB, #RGB, RRGGBB, rgb(r,g,b), rgba(r,g,b,a)  -> (r,g,b) em 0..1
    """
    try:
        if not s:
            return (0.0, 0.0, 0.0)
        s = str(s).strip()

        # rgb/rgba(...)
        if s.lower().startswith("rgb"):
            import re
            m = re.match(r"rgba?\s*\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})", s, re.I)
            if m:
                r, g, b = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
                return (max(0, min(255, r))/255.0,
                        max(0, min(255, g))/255.0,
                        max(0, min(255, b))/255.0)

        # remove # se vier sem
        if s.startswith("#"):
            s = s[1:]

        # #RGB → #RRGGBB
        if len(s) == 3 and all(c in "0123456789abcdefABCDEF" for c in s):
            s = "".join([c*2 for c in s])

        if len(s) == 6 and all(c in "0123456789abcdefABCDEF" for c in s):
            r = int(s[0:2], 16) / 255.0
            g = int(s[2:4], 16) / 255.0
            b = int(s[4:6], 16) / 255.0
            return (r, g, b)

    except Exception:
        pass
    return (0.0, 0.0, 0.0)


def _normrect_to_rect(page, x, y, w, h):
    W, H = float(page.rect.width), float(page.rect.height)
    fx, fy, fw, fh = float(x or 0), float(y or 0), float(w or 0), float(h or 0)
    return fitz.Rect(fx * W, fy * H, (fx + fw) * W, (fy + fh) * H)

FUDGE_X_PT = 0.0
FUDGE_Y_PT = 0.0

def _square_topleft(rect: fitz.Rect, min_size_pt: float = 10.0) -> fitz.Rect:
    """Quadrado ancorado no topo-esquerdo do retângulo (sem recentralizar)."""
    s = max(min(rect.width, rect.height), float(min_size_pt))
    return fitz.Rect(rect.x0, rect.y0, rect.x0 + s, rect.y0 + s)

def _base_widget_style(w: fitz.Widget):
    """Estilo base: sem borda e sem fill (transparente) para não ‘apagar’ o fundo."""
    try:
        w.text_color   = (0.00, 0.00, 0.00)
        w.border_color = None
        w.fill_color   = None
        w.border_width = 0
    except Exception:
        pass

# ----------------- Adição de Widgets (Form) --------------
def _add_text_widget(page, name: str, rect: fitz.Rect):
    """Campo de texto com leve borda e fundo claro."""
    w = fitz.Widget()
    w.field_name   = name or "campo"
    w.field_type   = fitz.PDF_WIDGET_TYPE_TEXT
    w.rect         = rect
    _base_widget_style(w)
    try:
        w.border_width = 0.8
        w.border_color = (0.85, 0.88, 0.88)
        w.fill_color   = (1.0, 1.0, 1.0)
    except Exception:
        pass
    page.add_widget(w)

def _draw_rect_outline(page, rect: fitz.Rect, color=(0.15, 0.15, 0.15), width=1.2):
    sh = page.new_shape()
    sh.draw_rect(rect)
    sh.finish(color=color, fill=None, width=width, closePath=True)
    sh.commit()

def _draw_circle_outline(page, rect: fitz.Rect, color=(0.15, 0.15, 0.15), width=1.2):
    cx = (rect.x0 + rect.x1) / 2.0
    cy = (rect.y0 + rect.y1) / 2.0
    r  = min(rect.width, rect.height) / 2.0
    sh = page.new_shape()
    sh.draw_circle((cx, cy), r)
    sh.finish(color=color, fill=None, width=width)
    sh.commit()

def _add_checkbox_widget(page, name: str, rect: fitz.Rect, checked: bool = False):
    """Checkbox: widget transparente + nossa borda retangular no tamanho exato."""
    sq = _square_topleft(rect, min_size_pt=10.0)
    sq = fitz.Rect(sq.x0 + FUDGE_X_PT, sq.y0 + FUDGE_Y_PT,
                   sq.x1 + FUDGE_X_PT, sq.y1 + FUDGE_Y_PT)
    w = fitz.Widget()
    w.field_name = name or "cb"
    w.field_type = fitz.PDF_WIDGET_TYPE_CHECKBOX
    w.rect = sq
    _base_widget_style(w)
    try:
        w.fill_color = None
        w.checkbox_checked = bool(checked)
        w.field_value = "Yes" if checked else "Off"
    except Exception:
        pass
    page.add_widget(w)
    _draw_rect_outline(page, sq)
    return sq

# ---------------- Desenhos: Texto / Imagem ---------------
def _tlen(text: str, fontsize: float, fontname: str) -> float:
    try:
        return fitz.get_text_length(text, fontsize=fontsize, fontname=fontname)
    except Exception:
        return fitz.get_text_length(text, fontsize=fontsize, fontname="helv")

def _wrap_words(line_text: str, W: float, fs: float, fn: str):
    words = line_text.split(" ")
    out, cur = [], ""
    def fits(s: str) -> bool:
        return _tlen(s, fs, fn) <= W
    for w in words:
        t = (cur + " " + w).strip() if cur else w
        if fits(t):
            cur = t
        else:
            if not cur:
                piece = ""
                for ch in w:
                    if fits(piece + ch):
                        piece += ch
                    else:
                        if piece:
                            out.append(piece)
                        piece = ch
                if piece:
                    out.append(piece)
                cur = ""
            else:
                out.append(cur)
                cur = w if fits(w) else ""
                if not cur:
                    piece = ""
                    for ch in w:
                        if fits(piece + ch):
                            piece += ch
                        else:
                            if piece:
                                out.append(piece)
                            piece = ch
                    if piece:
                        out.append(piece)
    if cur:
        out.append(cur)
    return out

def _fit_lines_to_box(lines, rect: fitz.Rect, fs: float, fn: str):
    # laço com limite para evitar loops
    for _ in range(12):
        lh = fs * 1.2
        max_w_line = 0.0
        for ln in lines:
            max_w_line = max(max_w_line, _tlen(ln, fs, fn))
        need_h = len(lines) * lh

        fits_w = (max_w_line <= rect.width)
        fits_h = (need_h <= rect.height)

        if fits_w and fits_h:
            return fs, lines

        # calcula fator de redução por largura/altura
        f_w = rect.width / max(1.0, max_w_line)
        f_h = rect.height / max(1.0, need_h)
        f = min(f_w, f_h) * 0.98  

        new_fs = max(6.0, fs * f)
        if abs(new_fs - fs) < 0.25:
            fs = new_fs
        else:
            fs = new_fs
        recomputed = []
        for original in lines:
            recomputed.extend(_wrap_words(original, rect.width, fs, fn))
        lines = recomputed

    return fs, lines  

def _insert_text(page, rect: fitz.Rect, text: str, font: str, size: float, color_hex: str, align_pdf: int):
    """
    Desenha texto com:
      - quebra de linha por palavras (fallback por caracteres),
      - auto-redução de fonte até caber na largura/altura da caixa.
    """
    r = fitz.Rect(rect)
    fs = float(size or 12)
    fn = font or "helv"
    rgb = _hex_to_rgb01(color_hex or "#000000")

    # prepara linhas (quebra por \n e depois por largura)
    raw_lines = (text or "").split("\n")
    lines = []
    for ln in raw_lines:
        lines.extend(_wrap_words(ln, r.width, fs, fn))

    # auto-ajuste de fonte para caber
    fs, lines = _fit_lines_to_box(lines, r, fs, fn)
    lh = fs * 1.2
    cur_y = r.y0 + fs  

    for ln in lines:
        if cur_y > r.y1 + 0.5:  
            break
        tw = _tlen(ln, fs, fn)
        if align_pdf == 1:    
            x = r.x0 + (r.width - tw) / 2
        elif align_pdf == 2:  
            x = r.x1 - tw
        else:                
            x = r.x0
        try:
            page.insert_text((x, cur_y), ln, fontsize=fs, fontname=fn, color=rgb, render_mode=0)
        except Exception:
            page.insert_text((x, cur_y), ln, fontsize=fs, fontname="helv", color=rgb, render_mode=0)

        cur_y += lh

def _insert_image(page, rect: fitz.Rect, data_url: str):
    if not data_url:
        return
    m = re.match(r"^data:([^;]+);base64,(.+)$", data_url)
    if not m:
        return
    b64 = m.group(2)
    try:
        b = base64.b64decode(b64)
    except Exception:
        return
    page.insert_image(rect, stream=b, keep_proportion=False)

def _draw_circle(page, rect: fitz.Rect):
    cx = (rect.x0 + rect.x1) / 2
    cy = (rect.y0 + rect.y1) / 2
    r = min(rect.width, rect.height) / 2
    shape = page.new_shape()
    shape.draw_circle((cx, cy), r)
    shape.finish(color=(0.13, 0.83, 0.94), fill=None, width=2)
    shape.commit()

def _align_to_pdf(a) -> int:
    if isinstance(a, str):
        a = a.lower().strip()
        if a in ("center", "1"): return 1
        if a in ("right",  "2"): return 2
        return 0
    try:
        ai = int(a)
        return 0 if ai < 0 else (2 if ai > 2 else ai)
    except Exception:
        return 0

# ----------- Fallback: reconstruir do snapshot -----------
def _rebuild_from_state(doc: fitz.Document, state_json: str):
    """Reconstrói textos / imagens se 'draws' veio vazio."""
    try:
        snap = json.loads(state_json or "[]")
    except Exception:
        return
    try:
        for pi, pg in enumerate(snap):
            page = doc[pi]
            W, H = float(page.rect.width), float(page.rect.height)
            for t in pg.get("texts", []):
                r = fitz.Rect(t["x"]*W, t["y"]*H, (t["x"]+t["w"])*W, (t["y"]+t["h"])*H)
                st = t.get("style") or {}
                font = st.get("font") or "helv"
                size = st.get("size") or 12
                color = st.get("color") or "#000000"
                align = _align_to_pdf(st.get("align") or 0)
                _insert_text(page, r, t.get("text") or "", font, size, color, align)
            for im in pg.get("images", []):
                r = fitz.Rect(im["x"]*W, im["y"]*H, (im["x"]+im["w"])*W, (im["y"]+im["h"])*H)
                _insert_image(page, r, im.get("data") or "")
    except Exception:
        pass

# ------ Remoção de widgets nativos (form do PDF) ---------
def _iou(r1: fitz.Rect, r2: fitz.Rect) -> float:
    """Intersection-over-Union simples para retângulos."""
    inter = r1 & r2  
    if inter.is_empty:
        return 0.0
    inter_area = inter.width * inter.height
    union_area = r1.width * r1.height + r2.width * r2.height - inter_area
    if union_area <= 0:
        return 0.0
    return inter_area / union_area

def _center_dist(r1: fitz.Rect, r2: fitz.Rect) -> float:
    c1 = ((r1.x0 + r1.x1) / 2.0, (r1.y0 + r1.y1) / 2.0)
    c2 = ((r2.x0 + r2.x1) / 2.0, (r2.y0 + r2.y1) / 2.0)
    return math.hypot(c1[0]-c2[0], c1[1]-c2[1])

def _delete_widget(page, widget: fitz.Widget) -> bool:
    """Deletar o widget."""
    try:
        page.delete_widget(widget)
        return True
    except Exception:
        pass
    
    try:
        ann = getattr(widget, "annot", None)
        if ann is not None:
            page.delete_annot(ann)
            return True
    except Exception:
        pass
    return False

def _remove_widgets_by_selectors(doc: fitz.Document, removals_data):
    if not isinstance(removals_data, list) or not removals_data:
        return 0

    removed = 0
    for sel in removals_data:
        try:
            pidx = int(sel.get("page", 0))
        except Exception:
            pidx = 0
        if not (0 <= pidx < len(doc)):
            continue

        page = doc[pidx]
        widgets = list(page.widgets() or [])

        # 1) Por xref
        target = None
        xref = sel.get("xref", None)
        if xref is not None:
            try:
                xref = int(xref)
                for w in widgets:
                    if getattr(w, "xref", None) == xref:
                        target = w
                        break
            except Exception:
                pass

        # 2) Por nome
        if target is None:
            name = (sel.get("name") or "").strip()
            if name:
                for w in widgets:
                    try:
                        if (w.field_name or "").strip() == name:
                            target = w
                            break
                    except Exception:
                        pass

        # 3) Por geometria
        if target is None and all(k in sel for k in ("x","y","w","h")):
            try:
                tgt_rect = _normrect_to_rect(page, float(sel["x"]), float(sel["y"]), float(sel["w"]), float(sel["h"]))
                best_iou, best_w = 0.0, None
                for w in widgets:
                    wr = fitz.Rect(w.rect)
                    iou = _iou(wr, tgt_rect)
                    if iou > best_iou:
                        best_iou, best_w = iou, w
                if best_w is not None:
                    wr = fitz.Rect(best_w.rect)
                    if best_iou >= 0.35 or _center_dist(wr, tgt_rect) <= 12.0:
                        target = best_w
            except Exception:
                pass

        # 4) Apaga
        if target is not None:
            if _delete_widget(page, target):
                removed += 1

    return removed

# ---------------------- Redactions -----------------------
def _apply_redactions(doc: fitz.Document, redactions_data):
    if not isinstance(redactions_data, list) or not redactions_data:
        return 0

    # ajuste fino em pontos (1 pt = 1/72")
    SHRINK_ALL_PT = 0.75            
    SHRINK_BOTTOM_EXTRA_PT = 1.00    
    MIN_SIDE_PT = 0.5                

    added = 0
    for rd in redactions_data:
        try:
            pidx = int(rd.get("page", 0))
        except Exception:
            pidx = 0
        if not (0 <= pidx < len(doc)):
            continue

        page = doc[pidx]
        rect = _normrect_to_rect(
            page,
            float(rd.get("x", 0.0)),
            float(rd.get("y", 0.0)),
            float(rd.get("w", 0.0)),
            float(rd.get("h", 0.0)),
        )
        # Cor de preenchimento (padrão branco)
        fill = _hex_to_rgb01(rd.get("fill") or "#FFFFFF")

        rx0 = rect.x0 + SHRINK_ALL_PT
        ry0 = rect.y0 + SHRINK_ALL_PT
        rx1 = rect.x1 - SHRINK_ALL_PT
        ry1 = rect.y1 - (SHRINK_ALL_PT + SHRINK_BOTTOM_EXTRA_PT)

        # garante dimensões mínimas/ordem correta
        if (rx1 - rx0) < MIN_SIDE_PT: rx1 = rx0 + MIN_SIDE_PT
        if (ry1 - ry0) < MIN_SIDE_PT: ry1 = ry0 + MIN_SIDE_PT

        rect = fitz.Rect(rx0, ry0, rx1, ry1)

        try:
            page.add_redact_annot(rect, fill=fill)
            added += 1
        except Exception:
            pass

    if added > 0:
        PIXELS = getattr(fitz, "PDF_REDACT_IMAGE_PIXELS", 0)
        try:
            for p in doc:
                p.apply_redactions(images=PIXELS)
        except Exception:
            try:
                for p in doc:
                    p.apply_redactions()
            except Exception:
                try:
                    doc.apply_redactions()
                except Exception:
                    pass

    return added


# ------------------------ Endpoint -----------------------
@router.post("/apply")
def apply_fields(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    fields: str = Form("[]"),
    draws: str = Form("[]"),
    state: str = Form("[]"),
    removals: str = Form("[]"),    
    redactions: str = Form("[]"),  
):
    src = _safe_tmp_copy(file)
    try:
        fields_data    = _parse_json(fields,    [])
        draws_data     = _parse_json(draws,     [])
        removals_data  = _parse_json(removals,  [])
        redactions_data= _parse_json(redactions,[])
        state_data_str = state or "[]"

        doc = fitz.open(src)

        # 0) Apagar widgets nativos selecionados
        try:
            _remove_widgets_by_selectors(doc, removals_data)
        except Exception:
            pass

        # 0.5) Aplicar redações (conteúdo fixo)
        try:
            _apply_redactions(doc, redactions_data)
        except Exception:
            pass

        # 1) Adicionar widgets (novos campos form)
        for f in fields_data:
            try:
                pidx = int(f.get("page", 0))
            except Exception:
                pidx = 0
            if not (0 <= pidx < len(doc)):
                continue
            page = doc[pidx]
            rect = _normrect_to_rect(page, f.get("x",0), f.get("y",0), f.get("w",0), f.get("h",0))
            ftype = (f.get("ftype") or "text").lower()
            if ftype == "checkbox":
                _add_checkbox_widget(page, f.get("name"), rect, checked=False)
            else:
                _add_text_widget(page, f.get("name"), rect)

      # 2) Desenhos fixos (texto, imagem, círculos)
        def _safe_float(v, default=0.0):
            try:
                return float(v)
            except Exception:
                return float(default)

        drew_any = False
        for d in draws_data:
            try:
                kind = (d.get("kind") or "").lower()
                pidx = int(d.get("page", 0) or 0)
            except Exception:
                kind, pidx = "", 0

            if not (0 <= pidx < len(doc)):
                continue

            page = doc[pidx]
            rect = _normrect_to_rect(
                page,
                _safe_float(d.get("x", 0)),
                _safe_float(d.get("y", 0)),
                _safe_float(d.get("w", 0)),
                _safe_float(d.get("h", 0)),
            )

            try:
                if kind == "text":
                    _insert_text(
                        page, rect,
                        text=d.get("text") or "",
                        font=d.get("font") or "helv", 
                        size=_safe_float(d.get("size", 12.0), 12.0),
                        color_hex=d.get("color") or "#000000",
                        align_pdf=_align_to_pdf(d.get("align") or 0),
                    )

                    # Sublinhado opcional
                    if bool(d.get("underline", False)):
                        rgb = _hex_to_rgb01(d.get("color") or "#000000")
                        # sublinha a última linha do bloco
                        y_line = rect.y1 - max(0.10 * _safe_float(d.get("size", 12.0), 12.0), 0.6)
                        sh = page.new_shape()
                        sh.draw_line((rect.x0, y_line), (rect.x1, y_line))
                        sh.finish(color=rgb, width=max(0.08 * _safe_float(d.get("size", 12.0), 12.0), 0.6))
                        sh.commit()

                    drew_any = True

                elif kind == "image":
                    _insert_image(page, rect, d.get("data") or "")
                    drew_any = True

                elif kind == "circle":
                    _draw_circle(page, rect)
                    drew_any = True

            except Exception as e:
                print("Erro ao processar elemento:", kind, "->", repr(e))
                traceback.print_exc()
                continue


        # 3) Fallback: se nada em draws, tenta reconstruir do snapshot
        if not drew_any and state_data_str and state_data_str not in ("[]","null","None"):
            _rebuild_from_state(doc, state_data_str)

        # Salvar
        fd, dst = tempfile.mkstemp(suffix=".pdf"); os.close(fd)
        doc.save(dst, deflate=True, garbage=4, clean=True, incremental=False)
        doc.close()

        # limpar temporários após envio
        background_tasks.add_task(lambda p: os.path.exists(p) and os.remove(p), src)
        background_tasks.add_task(lambda p: os.path.exists(p) and os.remove(p), dst)

        return FileResponse(dst, filename="pdf_editado.pdf", media_type="application/pdf")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao processar PDF: {e!r}")
    finally:
        if os.path.exists(src):
            try:
                os.remove(src)
            except:
                pass
