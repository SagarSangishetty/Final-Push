from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class URL(Base):
    __tablename__ = "urls"

    id           = Column(Integer, primary_key=True, index=True)
    original_url = Column(String(2048), nullable=False)
    short_code   = Column(String(20), unique=True, index=True, nullable=False)
    title        = Column(String(200), nullable=True)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

    clicks = relationship("Click", back_populates="url", cascade="all, delete")


class Click(Base):
    __tablename__ = "clicks"

    id         = Column(Integer, primary_key=True, index=True)
    url_id     = Column(Integer, ForeignKey("urls.id"), nullable=False)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(300), nullable=True)
    referer    = Column(String(500), nullable=True)
    country    = Column(String(100), nullable=True)
    browser    = Column(String(100), nullable=True)
    clicked_at = Column(DateTime(timezone=True), server_default=func.now())

    url = relationship("URL", back_populates="clicks")
