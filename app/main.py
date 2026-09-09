from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

from app.provider import fetch_invoices
from app.schemas import SyncResponse

app = FastAPI()

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc: HTTPException):
    headers = getattr(exc, "headers", None)
    if headers:
        return JSONResponse({"error": exc.detail}, status_code=exc.status_code, headers=headers)
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/v1/sync/invoices", response_model=SyncResponse)
async def sync_invoices():
    invoices = await fetch_invoices()
    return SyncResponse(
        status="success",
        fetched_count=len(invoices),
        invoices=invoices
    )

INDEX_HTML = Path(__file__).resolve().parent / "static" / "index.html"


@app.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    return INDEX_HTML.read_text(encoding="utf-8")
