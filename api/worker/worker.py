import time
import requests

from sqlalchemy.orm import Session

from api.database.database import SessionLocal
from api.models.delivery import Delivery
from api.models.webhook import Webhook


def process_deliveries():
    db: Session = SessionLocal()

    try:
        deliveries = db.query(Delivery).filter(Delivery.status == "pending").all()

        for delivery in deliveries:

            webhook = db.query(Webhook).filter(Webhook.id == delivery.webhook_id).first()

            if not webhook:
                delivery.status = "failed"
                db.commit()
                continue

            try:
                response = requests.post(
                    webhook.url,
                    json={
                        "event_type": delivery.event_type,
                        "payload": delivery.payload
                    },
                    timeout=5
                )

                if 200 <= response.status_code < 300:
                    delivery.status = "success"
                else:
                    delivery.status = "failed"

            except Exception as e:
                print("Delivery error:", e)
                delivery.status = "failed"

            db.commit()

    finally:
        db.close()


def start_worker():
    print("Worker started...")

    while True:
        process_deliveries()
        time.sleep(2)


if __name__ == "__main__":
    start_worker()