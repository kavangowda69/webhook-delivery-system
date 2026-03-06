from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import ARRAY
from api.database.database import Base


class Webhook(Base):
    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    url = Column(String)
    event_types = Column(ARRAY(String))
    active = Column(Boolean, default=True)