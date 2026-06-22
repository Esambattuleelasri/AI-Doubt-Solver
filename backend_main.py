# ─────────────────────────────────────────────
#  backend_main.py — FastAPI Application
# ─────────────────────────────────────────────
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from database.db import init_db
from routes import auth, chat, quiz


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize DB on startup."""
    init_db()
    yield


app = FastAPI(
    title="AI Doubt Solver Pro API",
    description="REST API for AI-powered doubt solving platform",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(quiz.router)


@app.get("/", tags=["Root"])
def root():
    return {"message": "AI Doubt Solver Pro API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health", tags=["Root"])
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend_main:app", host="0.0.0.0", port=8000, reload=True)
