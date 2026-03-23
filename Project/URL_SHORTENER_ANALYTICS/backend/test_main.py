from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db
import models

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
models.Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app, follow_redirects=False)


def test_root():
    res = client.get("/")
    assert res.status_code == 200

def test_health():
    res = client.get("/health")
    assert res.json()["status"] == "healthy"

def test_create_url():
    res = client.post("/urls", json={"original_url": "https://google.com", "title": "Google"})
    assert res.status_code == 200
    data = res.json()
    assert data["original_url"] == "https://google.com"
    assert len(data["short_code"]) > 0

def test_create_custom_url():
    res = client.post("/urls", json={"original_url": "https://github.com", "custom_code": "gh"})
    assert res.status_code == 200
    assert res.json()["short_code"] == "gh"

def test_duplicate_custom_code():
    client.post("/urls", json={"original_url": "https://example.com", "custom_code": "dup"})
    res = client.post("/urls", json={"original_url": "https://example2.com", "custom_code": "dup"})
    assert res.status_code == 400

def test_get_all_urls():
    res = client.get("/urls")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_redirect():
    create = client.post("/urls", json={"original_url": "https://python.org", "custom_code": "py"})
    code = create.json()["short_code"]
    res = client.get(f"/{code}")
    assert res.status_code == 307
    assert res.headers["location"] == "https://python.org"

def test_delete_url():
    create = client.post("/urls", json={"original_url": "https://delete.com", "custom_code": "del1"})
    code = create.json()["short_code"]
    res = client.delete(f"/urls/{code}")
    assert res.status_code == 200

def test_stats():
    create = client.post("/urls", json={"original_url": "https://stats.com", "custom_code": "st1"})
    code = create.json()["short_code"]
    res = client.get(f"/urls/{code}/stats")
    assert res.status_code == 200
    assert "clicks" in res.json()
