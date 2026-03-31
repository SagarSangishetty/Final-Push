from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List
import models, schemas, crud
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="URL Shortener API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "URL Shortener API is running 🚀"}

@app.get("/health")
def health():
    try:
        conn = engine.connect()
        conn.close()
        return {"status": "ok"}
    except:
        raise HTTPException(status_code=500, detail="DB not ready")

# ── Create short URL ──────────────────────────────
@app.post("/urls", response_model=schemas.URLOut)
def create_url(payload: schemas.URLCreate, db: Session = Depends(get_db)):
    # Check if custom code already exists
    if payload.custom_code:
        existing = crud.get_url_by_code(db, payload.custom_code)
        if existing:
            raise HTTPException(status_code=400, detail="Custom code already taken")
    return crud.create_url(db, payload)

# ── Get all URLs ──────────────────────────────────
@app.get("/urls", response_model=List[schemas.URLOut])
def get_urls(db: Session = Depends(get_db)):
    return crud.get_all_urls(db)

# ── Get single URL + analytics ────────────────────
@app.get("/urls/{code}/stats", response_model=schemas.URLStats)
def get_stats(code: str, db: Session = Depends(get_db)):
    url = crud.get_url_by_code(db, code)
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    clicks = crud.get_clicks(db, url.id)
    return schemas.URLStats(url=url, clicks=clicks)

# ── Delete URL ────────────────────────────────────
@app.delete("/urls/{code}")
def delete_url(code: str, db: Session = Depends(get_db)):
    if not crud.delete_url(db, code):
        raise HTTPException(status_code=404, detail="URL not found")
    return {"message": "Deleted successfully"}

# ── Redirect short URL (tracks click) ────────────
@app.get("/{code}")
def redirect(code: str, request: Request, db: Session = Depends(get_db)):
    url = crud.get_url_by_code(db, code)
    if not url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    # Track the click
    crud.track_click(db, url_id=url.id, request=request)

    return RedirectResponse(url=url.original_url, status_code=307)
