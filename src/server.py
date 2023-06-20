from prometheus_client import start_http_server, Counter, Gauge
from flask import Flask
import time
import random
import threading

app = Flask(__name__)

# Create metrics
COUNTER = Counter('requests_total', 'Total number of requests', ['path', 'method'])
MEMORY_GAUGE = Gauge('memory_usage', 'Memory usage in bytes')

# Fake memory baseline usage
MEMORY_BASELINE = 1.5e9

def apply_random_percentage(value, percentage):
    change = value * percentage
    random_change = random.uniform(-change, change)
    result = value + random_change
    return result

def update_memory_metric():
    while True:
        MEMORY_GAUGE.set(apply_random_percentage(MEMORY_BASELINE, 0.1))
        time.sleep(5)

@app.route('/')
def hello():
    # Increment the counter metric on each request
    COUNTER.labels(path='/', method='GET').inc()
    return f"Memory: {MEMORY_BASELINE}"

if __name__ == '__main__':
    # Start the Prometheus metrics server on port 8080
    start_http_server(8080)

    # Start collecting memory metrics in the background
    metrics_thread = threading.Thread(target=update_memory_metric)
    metrics_thread.daemon = True
    metrics_thread.start()

    # Start the Flask application server on port 8000
    app.run(port=8000)
