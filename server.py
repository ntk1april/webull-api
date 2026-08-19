"""
Render.com entry-point:  gunicorn server.py
or locally:             uvicorn server:app --reload
"""
import uvicorn
from app.main import app  # noqa: F401  (re-export for gunicorn)
from app.config import PORT

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=PORT, reload=False)
