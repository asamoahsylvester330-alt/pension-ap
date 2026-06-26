from fastapi import FastAPI, Form, Request, UploadFile, File, Query
from fastapi.responses import FileResponse, Response, JSONResponse
from banks import build_search_map
from engine import process_file, resolve_account
from dotenv import load_dotenv
import shutil
import os
from fastapi.middleware.cors import CORSMiddleware

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

limiter = Limiter(key_func=get_remote_address)

load_dotenv()

PAYSTACK_SECRET = os.getenv("PAYSTACK_SECRET")
GROQ_KEY        = os.getenv("groq_api_key")

_BANK_SEARCH_MAP = None

def get_search_map():
    global _BANK_SEARCH_MAP
    if _BANK_SEARCH_MAP is None:
        _BANK_SEARCH_MAP = build_search_map(PAYSTACK_SECRET)
    return _BANK_SEARCH_MAP


app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request, exc):
    path = request.url.path
    messages = {
        "/resolve": "Lookup rate limit reached. Please wait before trying again.",
        "/upload":  "Upload rate limit reached. Please wait before trying again.",
    }
    detail = messages.get(path, "Rate limit exceeded. Please try again later.")
    return JSONResponse(status_code=429, content={"detail": detail})


# ─── HOME ────────────────────────────────

@app.get("/")
@app.head("/")
async def home():
    return {"status": "Pension API is running"}

# ─── BULK UPLOAD ─────────────────────────

@app.post("/upload")
@limiter.limit("10/hour")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    mode: str = Form("extract"),
):
    input_path  = os.path.join(UPLOAD_DIR, file.filename)
    output_path = os.path.join(OUTPUT_DIR, f"verified_{file.filename}")

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        process_file(
            input_path=input_path,
            output_path=output_path,
            secret_key=PAYSTACK_SECRET,
            search_map=get_search_map(),
            groq_api_key=GROQ_KEY,
            mode=mode,
        )
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="Something went wrong.")

    return FileResponse(
        output_path,
        filename=f"verified_{file.filename}",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# ─── SINGLE RESOLVE ──────────────────────

@app.get("/resolve")
@limiter.limit("5/minute")
async def resolve_single(
    request: Request,
    account_number: str = Query(...),
    bank_code:      str = Query(...),
):
    result = resolve_account(
        account_number=account_number,
        bank_code=bank_code,
        secret_key=PAYSTACK_SECRET,
    )
    return JSONResponse(content=result)


# ─── HEALTH ──────────────────────────────

@app.get("/ping")
@app.head("/ping")
async def ping():
    return Response(status_code=200)
