"""Práctica 3 · Catálogo de Productos."""

from fastapi import FastAPI

from .routers import productos

app = FastAPI(title="Catálogo de Productos", version="0.3.0")
app.include_router(productos.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
