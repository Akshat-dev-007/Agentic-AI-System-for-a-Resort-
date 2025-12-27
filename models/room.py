from sqlalchemy import Column, Integer, String, Boolean
from models.base import Base

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True)
    room_number = Column(String(10), unique=True)
    is_available = Column(Boolean, default=True)
