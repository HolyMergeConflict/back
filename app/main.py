import sentry_sdk
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from tortoise.contrib.fastapi import register_tortoise

from app import auth
from app.config import TORTOISE_ORM
from app.router import tasks

app = FastAPI(
    title="FastAPI",
    docs_url="/docs",
    version="0.1.0",
    description='This is a simple FastAPI app.',
)

Instrumentator().instrument(app).expose(app)

sentry_sdk.init(
    dsn="https://40a378732763debb7cc8f058778b6d05@o4509729759232000.ingest.de.sentry.io/4509729761329232",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)

app.include_router(auth.router)
app.include_router(tasks.router)

app.add_middleware(SentryAsgiMiddleware)

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
)

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )