from fastapi import FastAPI
import psycopg2
import redis
import os

app = FastAPI()

DB_HOST = os.getenv("DB_HOST", "db")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")

conn = psycopg2.connect(
    host=DB_HOST,
    database="postgres",
    user="admin",
    password="admin123"
)

r = redis.Redis(host=REDIS_HOST, port=6379)

@app.get("/")
def home():
    return {"message": "Backend running"}


@app.post("/users/{name}")
def add_user(name: str):
    try:
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users(name TEXT)")
        cur.execute("INSERT INTO users VALUES (%s)", (name,))
        conn.commit()
        r.delete("users")
        return {"added": name}

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}


@app.get("/users")
def get_users():
    try:
        cached = r.get("users")
        if cached:
            return {"users": cached.decode()}

        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users(name TEXT)")
        cur.execute("SELECT name FROM users")

        users = [row[0] for row in cur.fetchall()]
        r.set("users", str(users), ex=60)

        return {"users": users}

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}