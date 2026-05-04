from flask import Flask
import time
import math

app = Flask(__name__)

def cpu_intensive_task():
    x = 0.0001
    for _ in range(10000000):
        x += math.sqrt(x)
    return x

@app.route('/health')
def health():
    return "OK", 200

@app.route('/')
def home():
    start = time.time()
    cpu_intensive_task()
    end = time.time()
    return f"CPU load generated! Time taken: {end - start:.2f} seconds\n"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)