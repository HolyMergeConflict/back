from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from app.exceptions.base_exception import ServiceException

def register_exception_handlers(app):
    @app.exception_handler(ServiceException)
    async def service_exception_handler(request: Request, exc: ServiceException):
        return JSONResponse(
            status_code=exc.status_code,
            content={'detail': exc.detail},
        )