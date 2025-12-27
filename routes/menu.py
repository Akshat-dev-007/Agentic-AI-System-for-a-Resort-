from flask import Blueprint, jsonify
from db import SessionLocal
from models.menu import MenuCategory

menu_bp = Blueprint("menu", __name__)

@menu_bp.route("/menu", methods=["GET"])
def get_menu():
    db = SessionLocal()
    categories = db.query(MenuCategory).all()

    response = {}
    for category in categories:
        response[category.name] = [
            {
                "id": item.id,
                "name": item.name,
                "price": item.price
            }
            for item in category.items
        ]

    db.close()
    return jsonify(response)
