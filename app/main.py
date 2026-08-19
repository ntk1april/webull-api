"""
FastAPI application entry-point.
"""
import logging
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import market, trade
import os
from app.config import WEBULL_APP_KEY, API_SECRET_KEY, WEBULL_TOKEN_CONTENT

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    if not WEBULL_APP_KEY:
        logger.warning("WEBULL_APP_KEY env var is not set – API calls will fail!")
    if API_SECRET_KEY == "change-me-in-render-env":
        logger.warning("API_SECRET_KEY is still the default value – please change it in Render env vars!")
        
    if WEBULL_TOKEN_CONTENT:
        os.makedirs("conf", exist_ok=True)
        # Handle literal \n if they paste it on one line, else just write it
        content = WEBULL_TOKEN_CONTENT.replace("\\n", "\n")
        with open("conf/token.txt", "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")
        logger.info("Successfully injected WEBULL_TOKEN_CONTENT into conf/token.txt")
        
    logger.info("Webull REST API starting up ✅")
    yield
    logger.info("Webull REST API shutting down")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Webull Market & Trade API",
    description=(
        "A REST proxy for the Webull OpenAPI SDK (Thailand region).\n\n"
        "## Authentication\n"
        "All endpoints require an **`X-API-Key`** header.\n\n"
        "## Endpoints\n"
        "- **Market Data** – quotes, candles, order book, instrument search\n"
        "- **Trade** – accounts, positions, order history"
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS – allow your website domain (tighten in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://doi-again.vercel.app"],   # ← NO trailing slash – browsers omit it
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(market.router)
app.include_router(trade.router)


# ── Global exception handler (turns 500 crashes into readable JSON) ───────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception on %s: %s", request.url, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "path": str(request.url),
        },
    )


# ── Health check (no auth required) ──────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok", "service": "webull-api"}


@app.get("/", tags=["System"])
async def root():
    return {
        "service": "Webull Market & Trade API",
        "docs": "/docs",
        "health": "/health",
    }
