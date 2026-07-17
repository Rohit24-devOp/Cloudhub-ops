import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse

from app.api import router
from app.core.config import get_settings
from app.database import Base, engine


settings = get_settings()
structlog.configure(processors=[structlog.processors.JSONRenderer()])
logger = structlog.get_logger()
limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CloudOps Hub API",
    description="Production-oriented cloud operations platform API.",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request, exc):
    return JSONResponse(status_code=429, content={"detail": "Too many requests"})


@app.middleware("http")
async def request_logging(request, call_next):
    response = await call_next(request)
    logger.info("http_request", method=request.method, path=request.url.path, status_code=response.status_code)
    return response


app.include_router(router, prefix="/api")
