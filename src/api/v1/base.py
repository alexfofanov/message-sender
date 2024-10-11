from fastapi import APIRouter

from src.api.v1.send_email import send_email_router

api_router = APIRouter()

api_router.include_router(
    send_email_router, prefix='/send_email', tags=['send_email']
)
