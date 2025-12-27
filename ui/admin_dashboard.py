import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from db import SessionLocal
from models.order import Order
from models.order import OrderItem
from models.service_request import ServiceRequest
from models.room import Room

st.set_page_config(page_title="Resort Admin Dashboard", layout="wide")
st.title("📊 Resort Admin Dashboard")

db = SessionLocal()

# Orders
st.subheader("🍽️ Food Orders")
orders = db.query(Order).all()
st.dataframe([
    {
        "Order ID": o.id,
        "Room": o.room_number,
        "Amount": o.total_amount,
        "Status": o.status,
        "Created At": o.created_at
    }
    for o in orders
])

# Order Items
st.subheader("📦 Order Items")
items = db.query(OrderItem).all()
st.dataframe([
    {
        "Order ID": i.order_id,
        "Item": i.item_name,
        "Qty": i.quantity,
        "Price": i.price
    }
    for i in items
])

# Room Service Requests
st.subheader("🧹 Room Service Requests")
services = db.query(ServiceRequest).all()
st.dataframe([
    {
        "Room": s.room_number,
        "Request": s.request_type,
        "Status": s.status,
        "Created At": s.created_at
    }
    for s in services
])

# Rooms
st.subheader("🛏️ Room Availability")
rooms = db.query(Room).all()
st.dataframe([
    {
        "Room": r.room_number,
        "Available": r.is_available
    }
    for r in rooms
])

db.close()
