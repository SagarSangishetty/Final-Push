from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello from Python!"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/user")
def user():
    return {"name": "John", "age": 30}