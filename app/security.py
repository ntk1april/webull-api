"""
Security: validates the X-API-Key header on every protected route.
"""
from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader

from app.config import API_SECRET_KEY

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key(api_key: str = Security(api_key_header)) -> str:
    if not api_key or api_key != API_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key header",
        )
    return api_key
