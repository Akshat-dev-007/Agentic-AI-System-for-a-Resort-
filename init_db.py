from db import engine
from models.base import Base

from models.room import Room
from models.order import Order
from models.service_request import ServiceRequest
from models.menu import MenuCategory, MenuItem

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("✅ Database tables created successfully")

