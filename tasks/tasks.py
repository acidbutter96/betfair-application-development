import time

from celery import Celery
from utils.dotenv import REDIS_BROKER_URL, REDIS_URL

app = Celery(
    'data_processing_queue',
    backend=REDIS_URL,
    broker=REDIS_BROKER_URL,
)


@app.task
def test_task(n):
    delay = 5

    print("Task running")
    print(f"Simulationg a {delay} second delay")

    time.sleep(delay)

    print("Task finished")

    _ = f"Hello {n}"
    return _
