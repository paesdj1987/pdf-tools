# frontend/ui_js.py
JS_EDITOR = r"""
(()=> {
  // ---------- Estado ----------
  let pdfDoc=null, fileBlob=null, processedURL=null;
  const S={ pages:[], history:[], redo:[] };
  const MIN_W=24, MIN_H=16;

  // modos: 'field' | 'text' | 'image' | 'erase' | null
  let mode=null;
  let fieldShapeKind='rect';
  let imageDataURL=null;

  // tipo do campo e grupo de rádio
  let fieldTypeKind = 'text';      // 'text' | 'checkbox'


  // seleção genérica
  let selected={ el:null, type:null, page:-1 };

  // copiar/colar
  let copyBuffer = null;
  let pasteBump  = 0;
  const PASTE_OFFSET = 10;

  const defaultStyle = { font:'Arial', size:10, bold:false, italic:false, underline:false, color:'#000000', align:'left' };

  // ---------- DOM ----------
  const fileInput=document.getElementById('fileInput');
  const viewer=document.getElementById('viewer');
  const applyBtn=document.getElementById('apply');
  const dlBtn=document.getElementById('download');
  const dlLink=document.getElementById('downloadLink');
  const drop=document.getElementById('drop');

  const btnField=document.getElementById('btnField');
  const btnText =document.getElementById('btnText');
  const btnImage=document.getElementById('btnImage');
  const btnErase=document.getElementById('btnErase');
  const fieldShapeSel=document.getElementById('fieldShapeKind');
  const fieldTypeSel=document.getElementById('fieldTypeKind');
  const imgPicker=document.getElementById('imgPicker');

  const undoBtn=document.getElementById('undo');
  const redoBtn=document.getElementById('redo');
  const deleteBtn=document.getElementById('deleteBtn');

  const textPanel=document.getElementById('textPanel');
  const tpFont=document.getElementById('tpFont');
  const tpSize=document.getElementById('tpSize');
  const tpBold=document.getElementById('tpBold');
  const tpItalic=document.getElementById('tpItalic');
  const tpUnderline=document.getElementById('tpUnderline');
  const tpColor=document.getElementById('tpColor');
  const tpAlignL=document.getElementById('tpAlignL');
  const tpAlignC=document.getElementById('tpAlignC');
  const tpAlignR=document.getElementById('tpAlignR');
  
  tpColor.addEventListener('input', () => {
  if (selected.el && selected.type === 'text') {
    const newColor = normalizeColorToHex(tpColor.value);
    selected.el.style.color = newColor;
    if (selected.style) selected.style.color = newColor;
    saveSnapshot();
  }
});


    // --- Regra: Checkbox só com quadrado ---
  function enforceCheckboxSquare(showMsg = true){
    if (fieldTypeKind === 'checkbox' && fieldShapeKind !== 'square') {
      fieldShapeKind = 'square';
      if (fieldShapeSel) fieldShapeSel.value = 'square';
      if (showMsg) showToast('Checkbox só é permitido com o formato quadrado.', 'error');
    }
  }


  function cssAlign(a){ return (a==='center'?'center':(a==='right'?'right':'left')); }
  function toggleBtn(btn, on){ btn.setAttribute('aria-pressed', on?'true':'false'); }
  function isOn(btn){ return btn.getAttribute('aria-pressed')==='true'; }
  function setAlign(a){
    toggleBtn(tpAlignL, a==='left');
    toggleBtn(tpAlignC, a==='center');
    toggleBtn(tpAlignR, a==='right');
  }
  function getAlign(){
    if(isOn(tpAlignC)) return 'center';
    if(isOn(tpAlignR)) return 'right';
    return 'left';
  }
  function getCurrentTextStyle(){
    return {
      font: tpFont.value,
      size: parseInt(tpSize.value,10) || 10,
      bold: isOn(tpBold),
      italic: isOn(tpItalic),
      underline: isOn(tpUnderline),
      color: tpColor.value,
      align: getAlign()
    };
  }
  function showToast(msg, type="") {
    const toast = document.getElementById('toast');
    toast.textContent = msg;

    // limpa classes anteriores
    toast.className = 'toast';
    if (type) toast.classList.add(type);

    // mostra
    toast.classList.add('show');

    // esconde depois de 3s (mas mantém a cor até a próxima msg)
    setTimeout(() => { 
      toast.classList.remove('show'); 
    }, 3000);
  }

  function ensurePDF(){
    if(!pdfDoc || !fileBlob || !S.pages.length){
      showToast('Necessário fazer o upload do arquivo PDF', 'error');

      return false;
    }
    return true;
  }
  function minTextHeightPx(size){ const s = parseInt(size || 10, 10); return Math.max(24, Math.ceil(s * 1.35) + 6); }
  function enforceMinHeightForTextEl(el){
    try{
      const st = JSON.parse(el.dataset.style || "{}");
      const minH = minTextHeightPx(st.size || 10);
      el.style.minHeight = minH + "px";
      const h = parseFloat(el.style.height || "0");
      if(h && h < minH) el.style.height = minH + "px";
    }catch{}
  }
  function applyStyleToElement(el, st){
    el.style.fontFamily = st.font || 'Arial';
    el.style.fontSize   = (st.size||10) + 'px';
    el.style.fontWeight = st.bold ? '700' : '400';
    el.style.fontStyle  = st.italic ? 'italic' : 'normal';
    el.style.textDecoration = st.underline ? 'underline' : 'none';
    el.style.color = normalizeColorToHex(st?.color || '#000000');
    el.style.textAlign  = cssAlign(st.align);
    el.dataset.style = JSON.stringify(st);
    enforceMinHeightForTextEl(el);
  }
  function syncPanelFromEl(el){
    try{
      const st = JSON.parse(el.dataset.style||'{}');
      tpFont.value = st.font || 'Arial';
      tpSize.value = String(st.size || 10);
      toggleBtn(tpBold, !!st.bold);
      toggleBtn(tpItalic, !!st.italic);
      toggleBtn(tpUnderline, !!st.underline);
      tpColor.value = st.color || '#000000';
      setAlign(st.align || 'left');
    }catch{}
  }

  // ---- Toggle de modos
  function setMode(m){
    mode = (mode===m ? null : m);
    [btnField,btnText,btnImage,btnErase].forEach(b=>b.setAttribute('aria-pressed','false'));
    if(mode==='field') btnField.setAttribute('aria-pressed','true');
    if(mode==='text')  btnText.setAttribute('aria-pressed','true');
    if(mode==='image') btnImage.setAttribute('aria-pressed','true');
    if(mode==='erase') btnErase.setAttribute('aria-pressed','true');

    if(mode==='text'){ textPanel.classList.add('visible'); }
    else { textPanel.classList.remove('visible'); }
    if(mode!==null) clearSelection();

    // mostrar/ocultar marcadores de widgets nativos
    refreshWidgetMarkersVisibility();

    setTimeout(resizeWorkarea, 0);
  }
  btnField.onclick = ()=> { if(!ensurePDF()) return; setMode('field'); };
  btnText.onclick  = ()=> { if(!ensurePDF()) return; setMode('text');  };
  btnImage.onclick = ()=> { if(!ensurePDF()) return; setMode('image'); imgPicker.click(); };
  btnErase.onclick = ()=> { if(!ensurePDF()) return; setMode('erase'); };

  fieldShapeSel.onchange = (e)=> {
    if(!ensurePDF()) { e.target.value = fieldShapeKind; return; }
    fieldShapeKind = e.target.value;
    enforceCheckboxSquare(true);   
  };


    fieldTypeSel.onchange = (e)=>{
    fieldTypeKind = e.target.value;
      if (fieldTypeKind === 'checkbox') {
        fieldShapeSel.value = 'square';
        fieldShapeKind = 'square';
      }
      // se quiser avisar ao trocar para checkbox:
      // showToast('Checkbox utiliza o formato quadrado automaticamente.', '');
    };


  imgPicker.addEventListener('change', async (e)=>{
    const f=e.target.files?.[0];
    imageDataURL=null;
    if(!f) return;
    const b=await f.arrayBuffer();
    const blob=new Blob([b],{type:f.type});
    imageDataURL = await new Promise(r=>{ const rd=new FileReader(); rd.onload=()=> r(rd.result); rd.readAsDataURL(blob); });
  });

  // Drag & Drop
  ['dragenter','dragover'].forEach(ev=>drop.addEventListener(ev, e=>{e.preventDefault(); drop.style.opacity=.9}));
  ['dragleave','drop'].forEach(ev=>drop.addEventListener(ev, e=>{e.preventDefault(); drop.style.opacity=1}));
  drop.addEventListener('drop', async e => { const f=e.dataTransfer.files[0]; if(f) await loadFile(f); });

  // Upload (reset para poder re-escolher o mesmo PDF)
  fileInput.addEventListener('change', async e => {
    const f = e.target.files && e.target.files[0];
    if (!f) return;
    await loadFile(f);
    e.target.value = '';
  });

  // Undo/Redo + Delete
  undoBtn.onclick = ()=> undo();
  redoBtn.onclick = ()=> redo();
  deleteBtn.onclick = ()=> removeSelected();
  document.addEventListener('keydown', (e)=>{
    const k = e.key;
    const typing = (e.target && (e.target.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/i.test(e.target.tagName)));
    if ((e.ctrlKey||e.metaKey) && k.toLowerCase()==='z' && !e.shiftKey) { e.preventDefault(); undo(); return; }
    if ((e.ctrlKey||e.metaKey) && (k.toLowerCase()==='y' || (k.toLowerCase()==='z' && e.shiftKey))) { e.preventDefault(); redo(); return; }
    if (!typing && (k === 'Delete' || k === 'Backspace')) { if (selected.el) { e.preventDefault(); removeSelected(); } }
  });

  // Copiar / colar (elementos criados no overlay)
  function isTypingTarget(el){
    return el && (
      el.isContentEditable ||
      /^(INPUT|TEXTAREA|SELECT)$/i.test(el.tagName)
    );
  }
  function px2num(v){ return parseFloat(String(v||'0').replace('px','')) || 0; }

  function findSelectedItem(){
    if(!selected.el || selected.page<0) return null;
    const p = S.pages[selected.page];
    if(selected.type==='field'){
      return (p.boxes||[]).find(b=>b.el===selected.el) || null;
    }
    if(selected.type==='text'){
      return (p.texts||[]).find(b=>b.el===selected.el) || null;
    }
    if(selected.type==='image'){
      return (p.images||[]).find(b=>b.el===selected.el) || null;
    }
    if(selected.type==='redact'){
      return (p.redactions||[]).find(b=>b.el===selected.el) || null;
    }
    return null;
  }

  function snapshotSelection(){
    const it = findSelectedItem();
    if(!it) return null;
    const el = it.el;
    const page = selected.page;
    const snap = {
      kind: selected.type, page,
      x: px2num(el.style.left),  y: px2num(el.style.top),
      w: px2num(el.style.width), h: px2num(el.style.height)
    };
    if(selected.type==='field'){
      snap.ftype = it.ftype || 'text';
      snap.shape = it.shape || 'rect';
    } else if(selected.type==='text'){
      snap.text  = (el.innerText||'');
      try { snap.style = JSON.parse(el.dataset.style||'{}'); } catch { snap.style = {...defaultStyle}; }
    } else if(selected.type==='image'){
      snap.data = it.data || null;
    }
    return snap;
  }

  async function pasteFromSnapshot(snap){
    if(!snap) return;
    const bump = (pasteBump++ % 5) * 6;
    const nx = (snap.x||0) + PASTE_OFFSET + bump;
    const ny = (snap.y||0) + PASTE_OFFSET + bump;
    const page = snap.page;
    const P = S.pages[page];

    if(snap.kind==='field'){
      const prevShape = fieldShapeKind, prevType = fieldTypeKind;
      fieldShapeKind = snap.shape || 'rect';
      fieldTypeKind  = snap.ftype || 'text';
      addField(page, nx, ny, P, true, snap.w, snap.h);
      fieldShapeKind = prevShape; fieldTypeKind = prevType;
      showToast('Campo colado');
      return;
    }
    if(snap.kind==='text'){
      addText(page, nx, ny, P, snap.w, snap.h);
      const newItem = S.pages[page].texts.at(-1);
      if(newItem){
        newItem.el.innerText = snap.text || '';
        applyStyleToElement(newItem.el, snap.style || defaultStyle);
        enforceMinHeightForTextEl(newItem.el);
        saveSnapshot();
      }
      showToast('Texto colado');
      return;
    }
    if(snap.kind==='image' && snap.data){
      const old = imageDataURL; imageDataURL = snap.data;
      addImage(page, nx, ny, P, snap.w, snap.h);
      imageDataURL = old;
      showToast('Imagem colada');
      return;
    }
  }

  document.addEventListener('keydown', async (e)=>{
    if(isTypingTarget(e.target)) return;
    const k = (e.key||'').toLowerCase();
    const withCmd = e.ctrlKey || e.metaKey;

    if(withCmd && k === 'c'){
      const snap = snapshotSelection();
      if(snap){ copyBuffer = snap; showToast('Copiado'); }
      e.preventDefault();
      return;
    }
    if(withCmd && k === 'v'){
      if(copyBuffer){ await pasteFromSnapshot(copyBuffer); }
      e.preventDefault();
      return;
    }
  });

  applyBtn.onclick = ()=> applyChanges();

  // ---------- Funções ----------
  async function loadFile(f){
    resetOutput();
    fileBlob=f;
    const buf=await f.arrayBuffer();
    pdfDoc=await pdfjsLib.getDocument({data:buf}).promise;
    await renderPages();
    wireInteractions();
    applyBtn.disabled=false;
    saveSnapshot();
    resizeWorkarea();
  }

  function resetOutput(){
    if(processedURL){ URL.revokeObjectURL(processedURL); processedURL=null; }
    dlBtn.disabled=true; dlLink.removeAttribute('href');
    viewer.innerHTML=''; S.pages=[]; S.history=[]; S.redo=[];
    clearSelection();
  }

  async function renderPages(){
    viewer.innerHTML=''; S.pages=[];
    for(let i=1;i<=pdfDoc.numPages;i++){
      const page=await pdfDoc.getPage(i);
      const viewport=page.getViewport({scale:1.4});
      const canvas=document.createElement('canvas');
      const ctx=canvas.getContext('2d');
      canvas.width=viewport.width; canvas.height=viewport.height;

      const wrap=document.createElement('div'); wrap.className='page-wrap'; wrap.style.width=viewport.width+'px';
      const overlay=document.createElement('div'); overlay.className='overlay';

      wrap.appendChild(canvas); wrap.appendChild(overlay); viewer.appendChild(wrap);
      await page.render({canvasContext:ctx, viewport}).promise;

      S.pages[i-1]={ w:viewport.width, h:viewport.height, overlay, boxes:[], texts:[], images:[], widgets:[], redactions:[] };

      // Detecta widgets nativos via annotations
      try{
        const annots = await page.getAnnotations(); // sem intent para não filtrar
        (annots||[]).forEach(a=>{
          const isWidget = a && (a.subtype === 'Widget' || a.fieldType != null || a.annotationType === 28);
          if(!isWidget) return;

          const r = viewport.convertToViewportRectangle(a.rect);
          const x = Math.min(r[0], r[2]);
          const y = Math.min(r[1], r[3]);
          const w = Math.abs(r[2]-r[0]);
          const h = Math.abs(r[3]-r[1]);

          const spot = document.createElement('div');
          spot.style.position='absolute';
          spot.style.left=x+'px'; spot.style.top=y+'px';
          spot.style.width=w+'px'; spot.style.height=h+'px';
          spot.style.border='2px dashed rgba(255,165,0,.7)';
          spot.style.background='rgba(255,165,0,.08)';
          spot.style.borderRadius='6px';
          spot.style.pointerEvents='none';   // só ativa no modo erase
          spot.style.display='none';
          spot.style.zIndex='5';

          const name = a.fieldName || a.title || '';
          spot.setAttribute('title', name ? ('Widget: '+name) : 'Widget');

          overlay.appendChild(spot);

          const item = {
            pageIndex: i-1, el: spot, name,
            rectNorm: { x: x/viewport.width, y: y/viewport.height, w: w/viewport.width, h: h/viewport.height },
            selected: false
          };
          spot.addEventListener('click', (ev)=>{
            ev.stopPropagation();
            if(mode !== 'erase') return;
            toggleWidgetRemoval(item);
          });
          S.pages[i-1].widgets.push(item);
        });
      }catch{}
    }
  }

  function refreshWidgetMarkersVisibility(){
    const on = (mode==='erase');
    S.pages.forEach(p=>{
      (p.widgets||[]).forEach(w=>{
        w.el.style.display = on ? 'block' : 'none';
        w.el.style.pointerEvents = on ? 'auto' : 'none';
        // reset visual quando sai do modo
        if(!on){
          w.selected = false;
          w.el.style.border='2px dashed rgba(255,165,0,.7)';
          w.el.style.background='rgba(255,165,0,.08)';
        }
      });
    });
  }

  function toggleWidgetRemoval(item){
    item.selected = !item.selected;
    if(item.selected){
      item.el.style.border='2px solid rgba(239,68,68,.9)';
      item.el.style.background='rgba(239,68,68,.12)';
    }else{
      item.el.style.border='2px dashed rgba(255,165,0,.7)';
      item.el.style.background='rgba(255,165,0,.08)';
    }
  }

  function wireInteractions(){
    S.pages.forEach((p,idx)=>{
      let drawing=false, startX=0, startY=0, ghost=null;

      p.overlay.addEventListener('mousedown', (e)=>{
        // clique fora de elementos => limpa seleção
        if(e.target===p.overlay && mode!=='erase') clearSelection();

        // Inserção / Borracha
        if(e.target!==p.overlay) return;
        if(!mode) return;

        const r=p.overlay.getBoundingClientRect();
        const px=e.clientX - r.left, py=e.clientY - r.top;

        if(mode==='text'){ addText(idx, px, py, p); return; }
        if(mode==='image'){
          if(!imageDataURL) { alert('Selecione uma imagem primeiro.'); return; }
          addImage(idx, px, py, p); return;
        }
        if(mode==='field'){
          drawing=true; startX=px; startY=py;
          ghost=document.createElement('div');
          ghost.className='rubber';
          ghost.style.left=px+'px'; ghost.style.top=py+'px';
          ghost.style.width='0px'; ghost.style.height='0px';
          p.overlay.appendChild(ghost);
          document.body.style.userSelect='none';
          return;
        }
        if(mode==='erase'){
          // desenha retângulo de REDAÇÃO (apagar conteúdo estático)
          drawing=true; startX=px; startY=py;
          ghost=document.createElement('div');
          ghost.className='rubber';
          ghost.style.borderColor='#ef4444';
          ghost.style.background='rgba(239,68,68,.10)';
          ghost.style.left=px+'px'; ghost.style.top=py+'px';
          ghost.style.width='0px'; ghost.style.height='0px';
          p.overlay.appendChild(ghost);
          document.body.style.userSelect='none';
          return;
        }
      });

      p.overlay.addEventListener('mousemove', (e)=>{
        if(!ghost) return;
        const r=p.overlay.getBoundingClientRect();
        const curX=e.clientX - r.left, curY=e.clientY - r.top;
        let x=Math.min(startX, curX), y=Math.min(startY, curY);
        let w=Math.abs(curX - startX), h=Math.abs(curY - startY);

        if(mode==='field' && fieldShapeKind==='square'){
          const s=Math.min(w,h); w=s; h=s;
          x = (curX>startX?startX:startX-s);
          y = (curY>startY?startY:startY-s);
        }

        ghost.style.left=x+'px'; ghost.style.top=y+'px';
        ghost.style.width=w+'px'; ghost.style.height=h+'px';
      });

      const finish = (commit)=>{
        if(!ghost) return;
        const x=parseFloat(ghost.style.left), y=parseFloat(ghost.style.top);
        const w=parseFloat(ghost.style.width), h=parseFloat(ghost.style.height);
        ghost.remove(); ghost=null; document.body.style.userSelect='';

        if(!commit || w<MIN_W || h<MIN_H) return;
        if(mode==='field') addField(idx, x, y, p, true, w, h);
        if(mode==='erase') addRedaction(idx, x, y, p, w, h);
      };

      p.overlay.addEventListener('mouseup', ()=> finish(true));
      p.overlay.addEventListener('mouseleave', ()=> finish(false));
      document.addEventListener('keydown', (e)=>{ if(e.key==='Escape' && ghost) finish(false); });
    });
  }

  function makeDraggable(el, W, H, onEnd){
    let isDragging=false,startX=0,startY=0,origX=0,origY=0;
    el.addEventListener('mousedown', e=>{
      const isHandle=(e.offsetX>el.clientWidth-16)&&(e.offsetY>el.clientHeight-16);
      if(isHandle) return;
      isDragging=true; startX=e.clientX; startY=e.clientY;
      origX=parseFloat(el.style.left)||0; origY=parseFloat(el.style.top)||0;
      document.onmousemove = ev=>{
        if(!isDragging) return;
        let nx=origX+(ev.clientX-startX), ny=origY+(ev.clientY-startY);
        nx=Math.max(0,Math.min(nx,W-el.clientWidth));
        ny=Math.max(0,Math.min(ny,H-el.clientHeight));
        el.style.left=nx+'px'; el.style.top=ny+'px';
      };
      document.onmouseup = ()=>{ isDragging=false; document.onmousemove=null; if(onEnd) onEnd(); };
    });
  }

  function select(el,type,pageIndex){
    clearSelection();
    selected={ el, type, page:pageIndex };
    el.classList.add('selected');
    if(type==='text'){ textPanel.classList.add('visible'); syncPanelFromEl(el); }
    setTimeout(resizeWorkarea, 0);
  }
  function clearSelection(){
    if(selected.el){ selected.el.classList.remove('selected'); }
    selected={ el:null, type:null, page:-1 };
  }
  function removeSelected(){
    if(!selected.el) return;
    const p=S.pages[selected.page];
    if(selected.type==='field'){
      const i=p.boxes.findIndex(b=>b.el===selected.el); if(i>=0) p.boxes.splice(i,1);
    }else if(selected.type==='text'){
      const i=p.texts.findIndex(b=>b.el===selected.el); if(i>=0) p.texts.splice(i,1);
    }else if(selected.type==='image'){
      const i=p.images.findIndex(b=>b.el===selected.el); if(i>=0) p.images.splice(i,1);
    }else if(selected.type==='redact'){
      const i=p.redactions.findIndex(b=>b.el===selected.el); if(i>=0) p.redactions.splice(i,1);
    }
    selected.el.remove();
    clearSelection();
    saveSnapshot();
    setTimeout(resizeWorkarea, 0);
  }

  function addField(pageIndex,x,y,page,track=true,wInit=200,hInit=30){
    const W=page.w, H=page.h;
    const box=document.createElement('div');
    // garantia: checkbox sempre usa quadrado
    if (fieldTypeKind === 'checkbox' && fieldShapeKind !== 'square') {
      fieldShapeKind = 'square';
      if (fieldShapeSel) fieldShapeSel.value = 'square';
    }
    box.className='field-box';

    const ftype = fieldTypeKind || 'text';
    if (ftype === 'checkbox') box.classList.add('field-checkbox');

    box.style.left=x+'px'; box.style.top=y+'px';
    box.style.width=wInit+'px'; box.style.height=hInit+'px';

    box.addEventListener('click', e=>{ e.stopPropagation(); select(box,'field',pageIndex); });
    makeDraggable(box, W, H, saveSnapshot);
    page.overlay.appendChild(box);

    let fieldName;
    const seq = (S.__globalSeq = (S.__globalSeq || 0) + 1);
    fieldName = `campo_${seq}`;


    const item = {
      page: pageIndex, el: box, name: fieldName,
      ftype: ftype,
      shape: (fieldShapeKind==='square') ? 'square' : 'rect',
      rect: () => ({
        x: parseFloat(box.style.left)/W,
        y: parseFloat(box.style.top)/H,
        w: parseFloat(box.style.width)/W,
        h: parseFloat(box.style.height)/H,
        name: fieldName,
        ftype: ftype
      })
    };
    page.boxes.push(item);
    if(track) saveSnapshot();
    select(box,'field',pageIndex);
  }

  function addText(pageIndex,x,y,page,wInit=220,hInit=40){
    const W=page.w, H=page.h;
    const box=document.createElement('div');
    box.className='text-box';
    box.style.left=x+'px'; box.style.top=y+'px';
    box.style.width=wInit+'px'; box.style.height=hInit+'px';
    box.contentEditable = "true";
    applyStyleToElement(box, getCurrentTextStyle());
    enforceMinHeightForTextEl(box);

    box.addEventListener('mousedown', e=>{ e.stopPropagation(); });
    box.addEventListener('click', e=>{ e.stopPropagation(); select(box,'text',pageIndex); box.focus(); });
    box.addEventListener('input', ()=> saveSnapshot());

    makeDraggable(box, W, H, ()=>{ enforceMinHeightForTextEl(box); saveSnapshot(); });
    page.overlay.appendChild(box);

    const item = {
      page: pageIndex, el: box,
      rect: ()=>({ x:parseFloat(box.style.left)/W, y:parseFloat(box.style.top)/H,
                   w:parseFloat(box.style.width)/W, h:parseFloat(box.style.height)/H,
                   text: (box.innerText||""), style: JSON.parse(box.dataset.style||'{}') })
    };
    page.texts.push(item); saveSnapshot();
    select(box,'text',pageIndex); box.focus();
  }

  function addImage(pageIndex,x,y,page,wInit=160,hInit=120){
    if(!imageDataURL) return;
    const W=page.w, H=page.h;
    const box=document.createElement('div'); box.className='img-box';
    box.style.left=x+'px'; box.style.top=y+'px';
    box.style.width=wInit+'px'; box.style.height=hInit+'px';
    const img=document.createElement('img'); img.src=imageDataURL;
    box.appendChild(img);

    box.addEventListener('click', e=>{ e.stopPropagation(); select(box,'image',pageIndex); });
    makeDraggable(box, W, H, saveSnapshot);
    page.overlay.appendChild(box);

    const item = {
      page: pageIndex, el: box, data:imageDataURL,
      rect: ()=>({ x:parseFloat(box.style.left)/W, y:parseFloat(box.style.top)/H,
                   w:parseFloat(box.style.width)/W, h:parseFloat(box.style.height)/H,
                   data:imageDataURL })
    };
    page.images.push(item); saveSnapshot();
    select(box,'image',pageIndex);
  }

  // Redaction (borracha em conteúdo estático)
  function addRedaction(pageIndex, x, y, page, wInit, hInit){
    const W=page.w, H=page.h;
    const box=document.createElement('div');
    box.style.position='absolute';
    box.style.left=x+'px'; box.style.top=y+'px';
    box.style.width=wInit+'px'; box.style.height=hInit+'px';
    box.style.border='2px solid rgba(239,68,68,.9)';
    box.style.background='rgba(239,68,68,.12)';
    box.style.borderRadius='6px';
    box.style.cursor='move';

    box.addEventListener('click', e=>{ e.stopPropagation(); select(box,'redact',pageIndex); });
    makeDraggable(box, W, H, saveSnapshot);
    page.overlay.appendChild(box);

    const item = {
      page: pageIndex, el: box,
      rect: ()=>({ x:parseFloat(box.style.left)/W, y:parseFloat(box.style.top)/H,
                   w:parseFloat(box.style.width)/W, h:parseFloat(box.style.height)/H })
    };
    page.redactions.push(item);
    saveSnapshot();
    select(box,'redact',pageIndex);
  }

  [tpFont,tpSize,tpBold,tpItalic,tpUnderline,tpColor,tpAlignL,tpAlignC,tpAlignR].forEach(el=>{
    el.addEventListener('click', ()=>{
      // Alinhamento
      if(el===tpAlignL) setAlign('left');
      if(el===tpAlignC) setAlign('center');
      if(el===tpAlignR) setAlign('right');

      // B / I / U precisam alternar o aria-pressed
      if (el===tpBold || el===tpItalic || el===tpUnderline) {
        toggleBtn(el, !isOn(el));
      }

      // Aplica no texto selecionado (se houver)
      if (selected.el && selected.type==='text') {
        applyStyleToElement(selected.el, getCurrentTextStyle());
        saveSnapshot();
      }
    });

    el.addEventListener('change', ()=>{
      if(selected.el && selected.type==='text'){ applyStyleToElement(selected.el, getCurrentTextStyle()); saveSnapshot(); }
    });
  });

  function snapshot(){
    const snap = S.pages.map((p,pi)=>({
      w:p.w, h:p.h,
      fields: p.boxes.map(b=>({ page:pi, shape:b.shape, ftype:b.ftype, ...b.rect() })),
      texts:  p.texts.map (b=>({ page:pi, ...b.rect() })),
      images: p.images.map(b=>({ page:pi, ...b.rect() })),
      widgets: (p.widgets||[]).map(w=>({ page:pi, name:w.name||"", rect:w.rectNorm||null })),
      redactions: (p.redactions||[]).map(r=>({ page:pi, ...r.rect() }))
    }));
    return JSON.stringify(snap);
  }
  function restore(snapStr){
    const snap = JSON.parse(snapStr);
    S.pages.forEach(p=>{
      [...p.boxes, ...p.texts, ...p.images, ...(p.redactions||[])].forEach(b=>b.el.remove());
      p.boxes=[]; p.texts=[]; p.images=[]; p.redactions=[];
      // widgets (marcadores) são reconstituídos a partir do PDF, não do snapshot
    });
    snap.forEach((ps,pi)=>{
      const P=S.pages[pi];
      // fields
      (ps.fields||[]).forEach(r=>{
        fieldTypeKind  = r.ftype || 'text';

        // normaliza shape legado
        let shape = r.shape || 'rect';
        if (shape === 'circle') shape = 'rect';  // converte círculos antigos para retângulo
        if (fieldTypeKind === 'checkbox') shape = 'square'; // checkbox sempre quadrado

        fieldShapeKind = shape;
        addField(pi, r.x*P.w, r.y*P.h, P, false, r.w*P.w, r.h*P.h);
      });


      // textos
      (ps.texts||[]).forEach(r=> { addText(pi, r.x*P.w, r.y*P.h, P, r.w*P.w, r.h*P.h); });
      P.texts.forEach((t,idx)=>{
        const r = (ps.texts||[])[idx];
        if(!r) return;
        t.el.innerText = r.text || "";
        applyStyleToElement(t.el, r.style || defaultStyle);
        enforceMinHeightForTextEl(t.el);
      });
      // imagens
      (ps.images||[]).forEach(r=> { imageDataURL=r.data; addImage(pi, r.x*P.w, r.y*P.h, P, r.w*P.w, r.h*P.h); });

      // redactions
      (ps.redactions||[]).forEach(r=> { addRedaction(pi, r.x*P.w, r.y*P.h, P, r.w*P.w, r.h*P.h); });

      fieldShapeSel.value = fieldShapeKind;
      fieldTypeSel.value  = fieldTypeKind;
    });
    clearSelection();
    refreshWidgetMarkersVisibility();
  }
  function saveSnapshot(){ const s=snapshot(); if(!S.history.length || S.history.at(-1)!==s){ S.history.push(s); S.redo=[]; } }
  function undo(){ if(S.history.length<=1) return; const cur=S.history.pop(); S.redo.push(cur); restore(S.history[S.history.length-1]); }
  function redo(){ if(!S.redo.length) return; const next=S.redo.pop(); S.history.push(next); restore(next); }

  function alignToPDF(a){ return a==='center'?1:(a==='right'?2:0); }
  // nomes válidos: helv, helv-bold, helv-oblique, helv-boldoblique
  // Converte a escolha do usuário (Arial / Times / Courier + B/I) para nomes válidos do PyMuPDF
  // Helvetica: helv / helv-bold / helv-oblique / helv-boldoblique
  // Times:     times-roman / times-bold / times-italic / times-bolditalic
  // Courier:   courier / courier-bold / courier-oblique / courier-boldoblique
  function mapFontToPDF(st) {
    const fam = String(st?.font || 'Arial').toLowerCase();
    const b = !!st?.bold, i = !!st?.italic;

    const isArial   = fam.includes('arial');           // “Arial” => Helvetica base
    const isTimes   = fam.includes('times');           // “Times New Roman”
    const isCourier = fam.includes('courier');         // “Courier New”

    if (isTimes) {
      if (b && i) return 'times-bolditalic';
      if (b)      return 'times-bold';
      if (i)      return 'times-italic';
      return 'times-roman';
    }
    if (isCourier) {
      if (b && i) return 'courier-boldoblique';
      if (b)      return 'courier-bold';
      if (i)      return 'courier-oblique';
      return 'courier';
    }
    // default: Helvetica (compat “Arial”)
    if (b && i) return 'helv-boldoblique';
    if (b)      return 'helv-bold';
    if (i)      return 'helv-oblique';
    return 'helv';
  }

  function normalizeColorToHex(c) {
    if (!c) return '#000000';
    c = String(c).trim();

    // já está em #RRGGBB
    if (/^#([A-Fa-f0-9]{6})$/.test(c)) return c.toLowerCase();

    // #RGB → #RRGGBB
    if (/^#([A-Fa-f0-9]{3})$/.test(c)) {
      return ('#' + c[1]+c[1] + c[2]+c[2] + c[3]+c[3]).toLowerCase();
    }

    // rgb/rgba → #RRGGBB
    const m = c.match(/^rgba?\s*\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})/i);
    if (m) {
      const r = Math.max(0, Math.min(255, parseInt(m[1], 10)));
      const g = Math.max(0, Math.min(255, parseInt(m[2], 10)));
      const b = Math.max(0, Math.min(255, parseInt(m[3], 10)));
      const toHex = (n) => n.toString(16).padStart(2, '0');
      return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
    }

    // fallback: se vier sem # mas com 6 hex
    if (/^[A-Fa-f0-9]{6}$/.test(c)) return ('#' + c).toLowerCase();

    return '#000000';
  }

  
  async function applyChanges(){
    const fields=[]; const draws=[];
    const removals=[]; const redactions=[];

    S.pages.forEach((p,pi)=>{
      p.boxes.forEach(b=>{
        const r=b.rect();
        fields.push({ page:pi, x:r.x, y:r.y, w:r.w, h:r.h, name:r.name, ftype:r.ftype });
      });
      p.texts .forEach(b=>{
        const r=b.rect();
        const st = r.style || defaultStyle;
        draws.push({
          kind: 'text',
          page: pi,
          x: r.x, y: r.y, w: r.w, h: r.h,
          text: r.text || '',
          font: mapFontToPDF(st),
          size: st.size || 10,
          color: normalizeColorToHex(st.color || '#000000'),   // <<<<<< AQUI
          align: (st.align === 'center' ? 1 : (st.align === 'right' ? 2 : 0))
          // underline: !!st.underline   // se/quando quiser reativar
        });


      });
      p.images.forEach(b=>{ const r=b.rect(); draws.push({ kind:'image', page:pi, x:r.x, y:r.y, w:r.w, h:r.h, data:r.data }); });

      // widgets nativos marcados para remoção
      (p.widgets||[]).forEach(w=>{
        if(w.selected){
          const sel = { page: pi, name: w.name||"" };
          if(w.rectNorm) Object.assign(sel, w.rectNorm);
          removals.push(sel);
        }
      });

      // redactions
      (p.redactions||[]).forEach(r=>{
        redactions.push({ page: pi, ...r.rect() });
      });
    });

    const fd=new FormData();
    fd.append('file', fileBlob);
    fd.append('fields', JSON.stringify(fields));
    fd.append('draws', JSON.stringify(draws));
    fd.append('state', snapshot());
    fd.append('removals', JSON.stringify(removals));
    fd.append('redactions', JSON.stringify(redactions));

    applyBtn.disabled=true; applyBtn.textContent='Processando...';
    try{
      const res=await fetch('/api/apply',{method:'POST', body:fd});
      if(!res.ok) throw new Error('Falha ao processar PDF');
      const blob=await res.blob();
      processedURL=URL.createObjectURL(blob);
      dlLink.href=processedURL; dlBtn.disabled=false;
    }catch(err){ alert(err.message||err); }
    finally{ applyBtn.disabled=false; applyBtn.textContent='Aplicar alteração'; }
  }

  /* ====== CALCULAR ALTURA ÚTIL DO VIEWER ====== */
  function resizeWorkarea(){
    const work = document.getElementById('workarea');
    const topbar = document.querySelector('.topbar');
    const toolbar = document.querySelector('.toolbar');
    const textPanel = document.getElementById('textPanel');

    const avail = window.innerHeight
      - (topbar?.offsetHeight || 0)
      - (toolbar?.offsetHeight || 0)
      - (textPanel?.offsetHeight || 0)
      - 16;

    const maxH = Math.max(320, avail);
    work.style.setProperty('--workarea-max', maxH + 'px');
    work.style.maxHeight = maxH + 'px';
  }

  const ro = new ResizeObserver(()=> resizeWorkarea());
  const _tb = document.querySelector('.topbar');   if(_tb) ro.observe(_tb);
  const _tl = document.querySelector('.toolbar');  if(_tl) ro.observe(_tl);
  const _tp = document.getElementById('textPanel');if(_tp) ro.observe(_tp);
  window.addEventListener('resize', resizeWorkarea);
  window.addEventListener('load', resizeWorkarea);
  resizeWorkarea();

  setAlign('left');
})();
"""
