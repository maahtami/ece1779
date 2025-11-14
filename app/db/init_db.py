# app/db/init_db.py
from app.database import Base, engine
from app.models.user import User
from app.models.item import Item
from app.models.transaction import Transaction

def init_db():
    Base.metadata.create_all(bind=engine)