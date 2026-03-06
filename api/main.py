from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from api.database.database import SessionLocal, engine
from api.models.webhook import Webhook, Base

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------
# Request Schemas
# ----------------------------

class WebhookCreate(BaseModel):
    user_id: str
    url: str
    event_types: List[str]


class WebhookUpdate(BaseModel):
    url: Optional[str] = None
    event_types: Optional[List[str]] = None


# ----------------------------
# CREATE WEBHOOK
# ----------------------------

@app.post("/webhooks")
def register_webhook(webhook: WebhookCreate, db: Session = Depends(get_db)):

    new_webhook = Webhook(
        user_id=webhook.user_id,
        url=webhook.url,
        event_types=webhook.event_types,
        active=True
    )

    db.add(new_webhook)
    db.commit()
    db.refresh(new_webhook)

    return new_webhook


# ----------------------------
# GET ALL WEBHOOKS
# ----------------------------

@app.get("/webhooks")
def list_webhooks(db: Session = Depends(get_db)):
    return db.query(Webhook).all()


# ----------------------------
# UPDATE WEBHOOK
# ----------------------------

@app.put("/webhooks/{webhook_id}")
def update_webhook(
    webhook_id: int,
    update_data: WebhookUpdate,
    db: Session = Depends(get_db)
):

    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()

    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    if update_data.url is not None:
        webhook.url = update_data.url

    if update_data.event_types is not None:
        webhook.event_types = update_data.event_types

    db.commit()
    db.refresh(webhook)

    return webhook


# ----------------------------
# DELETE WEBHOOK
# ----------------------------

@app.delete("/webhooks/{webhook_id}")
def delete_webhook(webhook_id: int, db: Session = Depends(get_db)):

    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()

    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    db.delete(webhook)
    db.commit()

    return {"message": "Webhook deleted"}


# ----------------------------
# DISABLE WEBHOOK
# ----------------------------

@app.patch("/webhooks/{webhook_id}/disable")
def disable_webhook(webhook_id: int, db: Session = Depends(get_db)):

    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()

    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    webhook.active = False
    db.commit()

    return {"message": "Webhook disabled"}


# ----------------------------
# ENABLE WEBHOOK
# ----------------------------

@app.patch("/webhooks/{webhook_id}/enable")
def enable_webhook(webhook_id: int, db: Session = Depends(get_db)):

    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()

    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    webhook.active = True
    db.commit()

    return {"message": "Webhook enabled"}