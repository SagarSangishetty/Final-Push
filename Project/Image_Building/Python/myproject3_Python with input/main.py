from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello!"}

@app.get("/greet/{name}")
def greet(name: str):
    return {"message": f"Hello {name}!"}

@app.get("/add/{a}/{b}")
def add(a: int, b: int):
    return {"result": a + b}