from orchestrator import create_app
from orchestrator.utilities.scheduler import process_subscription
from datetime import datetime, UTC
import time


def worker():
    print(f"subscription worker started at {datetime.now(UTC)}")
    
    app = create_app()

    with app.app_context():
        while True:
            try:
                process_subscription(batch_size=5)

            except Exception as e:
                print("worker error:", e)

            time.sleep(30)


if __name__ == "__main__":
    worker()




