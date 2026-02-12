from fastapi import FastAPI
import psycopg2, redis, os, random, string
from fastapi.responses import RedirectResponse

app = FastAPI()

DB_HOST = os.getenv("DB_HOST", "db")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")

conn = psycopg2.connect(
    host=DB_HOST,
    database="postgres",
    user="admin",
    password="admin123"
)

# Create table once at startup
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS urls(code TEXT, url TEXT)")
conn.commit()

r = redis.Redis(host=REDIS_HOST, port=6379)

def short_code():
    return ''.join(random.choices(string.ascii_letters+string.digits, k=6))


@app.post("/shorten")
def shorten(url: str):
    code = short_code()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS urls(code TEXT, url TEXT)")
    cur.execute("INSERT INTO urls VALUES (%s,%s)", (code, url))
    conn.commit()
    return {"short_url": f"/{code}"}


@app.get("/{code}")
def redirect(code: str):
    cached = r.get(code)
    if cached:
        return RedirectResponse(cached.decode())

    cur = conn.cursor()
    cur.execute("SELECT url FROM urls WHERE code=%s", (code,))
    res = cur.fetchone()

    if res:
        r.set(code, res[0], ex=300)
        return RedirectResponse(res[0])

    return {"error": "Not found"}
