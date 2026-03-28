from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Header, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

import database as db
from models import RatingRequest, CommentRequest, normalize_phone, is_valid_phone

BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init_db()
    yield


app = FastAPI(title="Nieznany Numer API", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


# ── Web pages ────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/numer/{phone_number}", response_class=HTMLResponse)
async def web_lookup(request: Request, phone_number: str):
    phone_number = normalize_phone(phone_number)
    if not is_valid_phone(phone_number):
        raise HTTPException(400, "Invalid phone number")
    data = await db.lookup_number(phone_number)
    return templates.TemplateResponse(request, "number.html", {"data": data})


# ── API v1 ───────────────────────────────────────────────────

@app.get("/api/v1/numbers/{phone_number}")
async def api_lookup(phone_number: str):
    phone_number = normalize_phone(phone_number)
    if not is_valid_phone(phone_number):
        raise HTTPException(400, "Invalid phone number")
    data = await db.lookup_number(phone_number)
    return data


@app.post("/api/v1/numbers/{phone_number}/ratings")
async def api_add_rating(
    phone_number: str,
    body: RatingRequest,
    x_device_id: str = Header(),
):
    phone_number = normalize_phone(phone_number)
    if not is_valid_phone(phone_number):
        raise HTTPException(400, "Invalid phone number")
    if not x_device_id or len(x_device_id) < 8:
        raise HTTPException(400, "Invalid device ID")
    return await db.add_rating(phone_number, x_device_id, body.rating)


@app.post("/api/v1/numbers/{phone_number}/comments")
async def api_add_comment(
    phone_number: str,
    body: CommentRequest,
    x_device_id: str = Header(),
):
    phone_number = normalize_phone(phone_number)
    if not is_valid_phone(phone_number):
        raise HTTPException(400, "Invalid phone number")
    if not x_device_id or len(x_device_id) < 8:
        raise HTTPException(400, "Invalid device ID")
    return await db.add_comment(phone_number, x_device_id, body.text)


@app.get("/api/v1/numbers/{phone_number}/comments")
async def api_get_comments(
    phone_number: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    phone_number = normalize_phone(phone_number)
    if not is_valid_phone(phone_number):
        raise HTTPException(400, "Invalid phone number")
    return await db.get_comments(phone_number, page, limit)
