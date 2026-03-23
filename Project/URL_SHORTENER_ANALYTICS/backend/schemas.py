from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime


class URLCreate(BaseModel):
    original_url: str
    custom_code: Optional[str] = None
    title: Optional[str] = None


class URLOut(BaseModel):
    id: int
    original_url: str
    short_code: str
    title: Optional[str]
    created_at: datetime
    click_count: Optional[int] = 0

    class Config:
        from_attributes = True


class ClickOut(BaseModel):
    id: int
    ip_address: Optional[str]
    browser: Optional[str]
    country: Optional[str]
    referer: Optional[str]
    clicked_at: datetime

    class Config:
        from_attributes = True


class URLStats(BaseModel):
    url: URLOut
    clicks: List[ClickOut]
