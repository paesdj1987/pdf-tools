# backend/__init__.py
from fastapi import APIRouter

# Endpoints principais
from .api_apply import router as apply_router

# Novos módulos (converter / OCR)
from .api_convert_word import router as convert_word_router
# from .api_convert_excel import router as convert_excel_router   # ← use quando criar
# from .ocr_apply import router as ocr_router                    # ← futuro OCR backend

router = APIRouter()

# Rota de edição principal
router.include_router(apply_router, prefix="/api", tags=["apply"])

# Conversão PDF → Word
router.include_router(convert_word_router, prefix="/api", tags=["convert-word"])

# Conversão PDF → Excel (quando existir)
# router.include_router(convert_excel_router, prefix="/api", tags=["convert-excel"])

# OCR (quando ativar)
# router.include_router(ocr_router, prefix="/api", tags=["ocr"])
