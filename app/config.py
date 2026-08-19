"""
Configuration – all secrets come from environment variables.
Set these in Render.com → Environment tab.
"""
import os

# ── Webull credentials ────────────────────────────────────────────────────────
WEBULL_APP_KEY: str = os.getenv("WEBULL_APP_KEY", "")
WEBULL_APP_SECRET: str = os.getenv("WEBULL_APP_SECRET", "")
WEBULL_REGION: str = os.getenv("WEBULL_REGION", "th")
WEBULL_ENDPOINT: str = os.getenv("WEBULL_ENDPOINT", "api.webull.co.th")

# ── API security ──────────────────────────────────────────────────────────────
# Pass  X-API-Key: <value>  in every request header from your website.
API_SECRET_KEY: str = os.getenv("API_SECRET_KEY", "change-me-in-render-env")

# ── Server ────────────────────────────────────────────────────────────────────
PORT: int = int(os.getenv("PORT", "8000"))
