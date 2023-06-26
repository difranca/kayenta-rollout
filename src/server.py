from prometheus_client import start_http_server, Counter, Gauge
from flask import Flask
import time
import random
import threading

app = Flask(__name__)

# Create metrics
COUNTER = Counter('requests_total', 'Total number of requests', ['path', 'method'])
MEMORY_GAUGE = Gauge('memory_usage', 'Memory usage in bytes')
CPU_GAUGE = Gauge('cpu_usage_percentage', 'CPU usage percentage')

# Fake baseline usages
CPU_USAGE_PERCENTAGE = 25.0
MEMORY_BASELINE = 2.0e9

cpu_thread = None
stop_cpu_consumption = False

def apply_random_percentage(value: float, percentage: float) -> float:
    change = value * percentage
    random_change = random.uniform(-change, change)
    result = value + random_change
    return result

def update_memory_metric(percentage: float, interval: int) -> None:
    while True:
        MEMORY_GAUGE.set(apply_random_percentage(MEMORY_BASELINE, percentage))
        time.sleep(interval)

@app.route('/')
def hello():
    COUNTER.labels(path='/', method='GET').inc()
    return f"Memory: {MEMORY_GAUGE._value.get()/1e9} GB<br>CPU: {CPU_GAUGE._value.get()} %"

@app.route('/cpu/<enable>')
def cpu(enable):
    global stop_cpu_consumption
    COUNTER.labels(path='/cpu', method='GET').inc()

    if enable == "100" and not cpu_thread.is_alive():
        stop_cpu_consumption = False
        CPU_USAGE_PERCENTAGE = 100.0
        cpu_thread.start()
    else:
        stop_cpu_consumption = True
        CPU_USAGE_PERCENTAGE = 25.0
    
    CPU_GAUGE.set(CPU_USAGE_PERCENTAGE)

    return f"CPU: {CPU_USAGE_PERCENTAGE}"

def consume_cpu() -> None:
    while not stop_cpu_consumption:
        pass

if __name__ == '__main__':
    start_http_server(8080)

    CPU_USAGE_PERCENTAGE = 0.1
    cpu(CPU_USAGE_PERCENTAGE)

    metrics_thread = threading.Thread(target=update_memory_metric, args=(0.05, 5))
    metrics_thread.daemon = True
    metrics_thread.start()

    cpu_thread = threading.Thread(target=consume_cpu)
    cpu_thread.daemon = True

    app.run(port=5000, host='0.0.0.0')
