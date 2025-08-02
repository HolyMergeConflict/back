from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app import auth
from app.api.exception_handlers import register_exception_handlers
from app.api.v1.routers import users_router, tasks_router
from app.db.init_db import init_db
from app.router import tasks, model


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="FastAPI",
    docs_url="/docs",
    version="0.1.0",
    description='This is a simple FastAPI app.',
    lifespan=lifespan
)

Instrumentator().instrument(app).expose(app)

sentry_sdk.init(
    dsn="https://40a378732763debb7cc8f058778b6d05@o4509729759232000.ingest.de.sentry.io/4509729761329232",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)

register_exception_handlers(app)

app.include_router(users_router.router)
app.include_router(tasks_router.router)

app.add_middleware(SentryAsgiMiddleware)




@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )