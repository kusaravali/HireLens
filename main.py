"""HireLens API: upload a resume, paste a job description, get a match report."""
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import MAX_UPLOAD_MB
from .embeddings import get_model
from .llm import explain, llm_enabled
from .matcher import analyze
from .parser import clean_text, extract_text

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"


@asynccontextmanager
async def lifespan(app):
    # Load the embedding model at startup so the first request is fast
    get_model()
    yield


app = FastAPI(title="HireLens", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "llm_enabled": llm_enabled()}


@app.post("/api/analyze")
async def analyze_endpoint(
    jd_text: str = Form(...),
    resume_text: Optional[str] = Form(None),
    resume_file: Optional[UploadFile] = File(None),
):
    # 1. Get the resume text (file wins over pasted text)
    resume = ""
    if resume_file is not None and resume_file.filename:
        data = await resume_file.read()
        if len(data) > MAX_UPLOAD_MB * 1024 * 1024:
            raise HTTPException(status_code=413, detail=f"File is larger than {MAX_UPLOAD_MB} MB.")
        try:
            resume = extract_text(resume_file.filename, data)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error))
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Could not read this file. Try a text-based PDF or paste the text instead.",
            )
    elif resume_text:
        resume = clean_text(resume_text)

    jd = clean_text(jd_text)

    # 2. Basic validation
    if len(resume) < 30:
        raise HTTPException(status_code=400, detail="Please upload or paste your resume.")
    if len(jd) < 30:
        raise HTTPException(status_code=400, detail="Please paste a longer job description.")

    # 3. Run the analysis (CPU work, so keep it off the event loop)
    try:
        result = await run_in_threadpool(analyze, resume, jd)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    result["explanation"] = await run_in_threadpool(explain, result)
    return result
