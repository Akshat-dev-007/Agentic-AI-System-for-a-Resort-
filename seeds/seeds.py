from sqlalchemy.orm import Session
from db import engine
from models.room import Room

def seed_rooms():
    session = Session(bind=engine)

    # Avoid duplicate seeding
    if session.query(Room).count() > 0:
        print("ℹ️ Rooms already seeded")
        return

    rooms = [
        Room(room_number="101", is_available=True),
        Room(room_number="102", is_available=True),
        Room(room_number="103", is_available=False),
        Room(room_number="201", is_available=True),
        Room(room_number="202", is_available=True),
        Room(room_number="203", is_available=False),
    ]

    session.add_all(rooms)
    session.commit()
    session.close()

    print("✅ Rooms seeded successfully")

if __name__ == "__main__":
    seed_rooms()
