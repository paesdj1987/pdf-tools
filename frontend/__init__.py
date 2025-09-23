# frontend/__init__.py
from fastapi import APIRouter

from .layout_inicial import router as home_router
from .layout_campo import router as editor_router
#from .layout_ocr import router as ocr_page_router 
from .ocr_provisorio import router as ocr_router # provisorio


router = APIRouter()

router.include_router(home_router)          # /
router.include_router(editor_router)        # /inserir
#router.include_router(ocr_page_router)      # /ocr
router.include_router(ocr_router) 