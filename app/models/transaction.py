# app/models/transaction.py
from sqlalchemy import Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class TransactionType(str, enum.Enum):
    in_ = "in"
    out = "out"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    type = Column(Enum(TransactionType), nullable=False)

    user = relationship("User", back_populates="transactions")
    item = relationship("Item", back_populates="transactions")