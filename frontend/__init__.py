# frontend/__init__.py
from fastapi import APIRouter

from .layout_inicial import router as home_router
from .layout_campo import router as editor_router
#from .layout_ocr import router as ocr_page_router 
from .ocr import router as ocr_router
from .converter_word import router as conv_word_router
from .converter_excel import router as conv_excel_router


router = APIRouter()

router.include_router(home_router)       # "/"
router.include_router(editor_router)     # "/editar"
router.include_router(ocr_router)        # "/ocr"
router.include_router(conv_word_router)  # "/converter-word"
router.include_router(conv_excel_router) # "/converter-excel"