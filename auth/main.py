import os
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from psycopg2.pool import ThreadedConnectionPool
from contextlib import asynccontextmanager

from lib.logger.config import setup_logging

from auth.http import router as auth_router

DB_POOL_MIN = 2
DB_POOL_MAX = 10 

setup_logging()

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    dsn = (
        f"dbname={os.getenv('DB_NAME')} "
        f"user={os.getenv('DB_USER')} "
        f"password={os.getenv('DB_PASSWORD')} "
        f"host={os.getenv('DB_HOST')}"
    )
    app.state.pool = ThreadedConnectionPool(minconn=DB_POOL_MIN, maxconn=DB_POOL_MAX, dsn=dsn)
    yield
    app.state.pool.closeall()

app = FastAPI(title="Auth Service", lifespan=lifespan)

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception for request {request.url}: {exc}", exc_info=True)
    
    env = os.getenv("APP_ENV")
    is_dev_env = env == "dev" or env == "test"
    
    if is_dev_env:
        error_detail = {
            "detail": "An internal server error occurred.",
            "error_type": str(type(exc).__name__),
            "error_message": str(exc)
        }
    # В production-окружении показываем только общее сообщение
    else:
        error_detail = {"detail": "An internal server error occurred."}

    return JSONResponse(
        status_code=500,
        content=error_detail,
    )

app.include_router(auth_router)
