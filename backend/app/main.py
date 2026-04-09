from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import health, threads, documents
from app.db.migrations import init_schema

app = FastAPI(title="Agentic RAG API", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    """Initialize database schema on startup."""
    await init_schema()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(threads.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
