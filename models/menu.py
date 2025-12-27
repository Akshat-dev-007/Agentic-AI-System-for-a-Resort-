from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from models.base import Base

class MenuCategory(Base):
    __tablename__ = "menu_categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)

    items = relationship("MenuItem", back_populates="category")


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True)
    name = Column(String(150))
    description = Column(Text)
    price = Column(Float)

    category_id = Column(Integer, ForeignKey("menu_categories.id"))
    category = relationship("MenuCategory", back_populates="items")
