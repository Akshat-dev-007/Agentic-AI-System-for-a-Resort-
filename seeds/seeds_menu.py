from sqlalchemy.orm import Session
from db import engine
from models.menu import MenuCategory, MenuItem


MENU_DATA = {
    "Breakfast": [
        ("Masala Dosa", "Crispy dosa with spiced potato filling", 120),
        ("Plain Idli", "Steamed rice cakes with chutney", 80),
        ("Medu Vada", "Fried lentil doughnuts", 90),
        ("Upma", "Semolina cooked with vegetables", 100),
        ("Poha", "Flattened rice with peanuts", 100),
        ("Aloo Paratha", "Stuffed paratha with curd", 130),
        ("Paneer Paratha", "Paneer stuffed paratha", 150),
        ("Puri Bhaji", "Fried bread with potato curry", 140),
        ("Omelette", "Indian-style omelette", 90),
        ("Boiled Eggs", "Two boiled eggs", 70),
    ],

    "Veg Starters": [
        ("Paneer Tikka", "Grilled paneer cubes", 220),
        ("Veg Manchurian", "Veg balls in spicy sauce", 180),
        ("Hara Bhara Kabab", "Spinach & peas kabab", 200),
        ("Crispy Corn", "Fried corn with spices", 160),
        ("Aloo Chaat", "Spicy potato snack", 150),
        ("Paneer Pakora", "Fried paneer fritters", 170),
        ("Veg Spring Roll", "Stuffed crispy rolls", 180),
        ("Mushroom Tikka", "Grilled mushrooms", 210),
        ("Corn Cheese Balls", "Cheese filled corn balls", 190),
        ("Stuffed Capsicum", "Veg stuffed capsicum", 200),
    ],

    "Non-Veg Starters": [
        ("Chicken Tikka", "Grilled marinated chicken", 260),
        ("Chicken 65", "Spicy fried chicken", 240),
        ("Fish Fry", "Shallow fried fish", 280),
        ("Mutton Seekh Kabab", "Minced mutton kabab", 320),
        ("Prawn Tempura", "Crispy fried prawns", 350),
        ("Chicken Pakora", "Gram flour fried chicken", 230),
        ("Tandoori Chicken", "Charcoal grilled chicken", 300),
        ("Fish Tikka", "Grilled fish cubes", 290),
        ("Chicken Lollipop", "Fried chicken wings", 250),
        ("Egg Bhurji", "Spiced scrambled eggs", 180),
    ],

    "Veg Main Course": [
        ("Paneer Butter Masala", "Creamy tomato gravy", 260),
        ("Shahi Paneer", "Cashew based gravy", 270),
        ("Dal Tadka", "Yellow lentils tempered", 180),
        ("Dal Makhani", "Creamy black lentils", 220),
        ("Mix Veg", "Seasonal vegetable curry", 200),
        ("Chole Masala", "Chickpea curry", 210),
        ("Rajma Masala", "Red kidney bean curry", 210),
        ("Kadai Paneer", "Spicy paneer curry", 250),
        ("Palak Paneer", "Spinach paneer curry", 240),
        ("Veg Korma", "Mild coconut gravy", 230),
    ],

    "Non-Veg Main Course": [
        ("Butter Chicken", "Creamy tomato chicken curry", 320),
        ("Chicken Curry", "Traditional Indian curry", 280),
        ("Chicken Korma", "Cashew based gravy", 300),
        ("Mutton Rogan Josh", "Kashmiri mutton curry", 380),
        ("Fish Curry", "Spicy fish gravy", 330),
        ("Prawn Masala", "Spicy prawn curry", 360),
        ("Egg Curry", "Boiled eggs in gravy", 220),
        ("Chicken Chettinad", "South Indian spicy curry", 310),
        ("Mutton Curry", "Slow cooked mutton", 360),
        ("Fish Moilee", "Coconut fish curry", 340),
    ],

    "Desserts": [
        ("Gulab Jamun", "Milk dumplings in syrup", 90),
        ("Rasgulla", "Soft cottage cheese balls", 90),
        ("Ice Cream", "Vanilla/Chocolate/Strawberry", 100),
        ("Brownie", "Chocolate brownie", 140),
        ("Fruit Salad", "Fresh seasonal fruits", 120),
        ("Kheer", "Rice pudding", 110),
        ("Gajar Halwa", "Carrot dessert", 130),
        ("Rabri", "Sweet thickened milk", 140),
        ("Kulfi", "Traditional kulfi", 120),
        ("Jalebi", "Crispy syrup dessert", 90),
    ],

    "Drinks": [
        ("Tea", "Indian tea", 40),
        ("Coffee", "Hot coffee", 50),
        ("Masala Chai", "Spiced tea", 50),
        ("Cold Coffee", "Iced coffee", 90),
        ("Fresh Lime Soda", "Sweet or salt", 70),
        ("Soft Drinks", "Coke/Pepsi/Sprite", 60),
        ("Buttermilk", "Spiced yogurt drink", 60),
        ("Lassi", "Sweet or salted", 80),
        ("Fresh Juice", "Seasonal fruit juice", 100),
        ("Mineral Water", "1L bottle", 40),
    ],

    "Breads": [
        ("Tandoori Roti", "Whole wheat roti", 25),
        ("Butter Roti", "Butter topped roti", 30),
        ("Plain Naan", "Refined flour naan", 40),
        ("Butter Naan", "Butter naan", 50),
        ("Garlic Naan", "Garlic flavored naan", 60),
        ("Laccha Paratha", "Layered paratha", 50),
        ("Missi Roti", "Spiced gram flour roti", 45),
        ("Roomali Roti", "Thin soft roti", 40),
        ("Stuffed Naan", "Paneer stuffed naan", 70),
        ("Kulcha", "Leavened bread", 50),
    ],

    "Miscellaneous": [
        ("Extra Rice", "Steamed rice", 80),
        ("Papad", "Roasted or fried", 30),
        ("Raita", "Curd with vegetables", 70),
        ("Pickle", "Indian mixed pickle", 40),
        ("Salad", "Fresh green salad", 80),
        ("Onion Salad", "Sliced onions with lemon", 60),
        ("Boondi Raita", "Curd with boondi", 80),
        ("Lemon Wedges", "Fresh lemon slices", 30),
        ("Extra Gravy", "Additional curry gravy", 60),
        ("Butter", "Extra butter", 40),
    ],
}


def seed_menu():
    session = Session(bind=engine)

    for category_name, items in MENU_DATA.items():
        category = session.query(MenuCategory).filter_by(name=category_name).first()
        if not category:
            category = MenuCategory(name=category_name)
            session.add(category)
            session.commit()
            session.refresh(category)

        for name, desc, price in items:
            exists = (
                session.query(MenuItem)
                .filter_by(name=name, category_id=category.id)
                .first()
            )
            if not exists:
                session.add(
                    MenuItem(
                        name=name,
                        description=desc,
                        price=price,
                        category_id=category.id,
                    )
                )

    session.commit()
    session.close()
    print("✅ Menu seeded successfully")


if __name__ == "__main__":
    seed_menu()
