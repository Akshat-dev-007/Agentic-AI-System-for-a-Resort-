from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from models.base import Base

class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id = Column(Integer, primary_key=True)
    room_number = Column(String(10))
    request_type = Column(String(100))
    status = Column(String(50), default="Pending")
    created_at = Column(DateTime, default=datetime.utcnow)
