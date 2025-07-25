from fastapi import APIRouter

from app.auth import auth

router = APIRouter()
router.include_router(auth.router)