import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.models.item import Item
from app.models.user import User
from app.services.transaction_service import apply_stock_change, InsufficientStockError


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_apply_stock_change_in(db):
    user = User(username="manager", hashed_password="x", role="manager")
    db.add(user)
    item = Item(name="Mouse", quantity=0, low_stock_threshold=1)
    db.add(item)
    db.commit()
    db.refresh(user)
    db.refresh(item)

    tx = apply_stock_change(db, item, "in", 5, user.id)
    assert tx.quantity == 5
    assert item.quantity == 5
    assert item.is_low_stock is False


def test_apply_stock_change_insufficient(db):
    user = User(username="staff", hashed_password="x", role="staff")
    db.add(user)
    item = Item(name="Keyboard", quantity=1, low_stock_threshold=1)
    db.add(item)
    db.commit()
    db.refresh(user)
    db.refresh(item)

    with pytest.raises(InsufficientStockError):
        apply_stock_change(db, item, "out", 3, user.id)