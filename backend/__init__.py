# backend/__init__.py
from fastapi import APIRouter

from .api_apply import router as apply_router
#from .ocr_apply import router as ocr_router  # <- novo

router = APIRouter()
router.include_router(apply_router, prefix="/api", tags=["apply"])


# novo endpoint de OCR
#router.include_router(ocr_router, prefix="/api", tags=["ocr"])
