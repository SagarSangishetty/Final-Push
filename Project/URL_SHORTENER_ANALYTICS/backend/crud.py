from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import Request
import models, schemas
import random, string


def generate_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def get_url_by_code(db: Session, code: str):
    return db.query(models.URL).filter(models.URL.short_code == code).first()


def get_all_urls(db: Session):
    urls = db.query(models.URL).order_by(models.URL.created_at.desc()).all()
    for url in urls:
        url.click_count = db.query(func.count(models.Click.id))\
                            .filter(models.Click.url_id == url.id).scalar()
    return urls


def create_url(db: Session, payload: schemas.URLCreate):
    code = payload.custom_code or generate_code()
    # Ensure uniqueness for auto-generated codes
    while not payload.custom_code and get_url_by_code(db, code):
        code = generate_code()

    db_url = models.URL(
        original_url=payload.original_url,
        short_code=code,
        title=payload.title or payload.original_url[:80]
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    db_url.click_count = 0
    return db_url


def delete_url(db: Session, code: str):
    url = get_url_by_code(db, code)
    if not url:
        return False
    db.delete(url)
    db.commit()
    return True


def track_click(db: Session, url_id: int, request: Request):
    ua = request.headers.get("user-agent", "")

    # Simple browser detection
    browser = "Other"
    if "Chrome" in ua and "Edg" not in ua:
        browser = "Chrome"
    elif "Firefox" in ua:
        browser = "Firefox"
    elif "Safari" in ua and "Chrome" not in ua:
        browser = "Safari"
    elif "Edg" in ua:
        browser = "Edge"

    click = models.Click(
        url_id=url_id,
        ip_address=request.client.host if request.client else "unknown",
        user_agent=ua[:300],
        referer=request.headers.get("referer", "Direct"),
        browser=browser,
        country="Unknown",   # integrate ip-api.com for real geo data
    )
    db.add(click)
    db.commit()


def get_clicks(db: Session, url_id: int):
    return db.query(models.Click)\
             .filter(models.Click.url_id == url_id)\
             .order_by(models.Click.clicked_at.desc())\
             .all()
