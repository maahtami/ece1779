from sqlalchemy.orm import Session

from app.db.database import Base, engine
from app.models.user import User
from app.models.item import Item
from app.models.transaction import Transaction
from app.core.security import hash_password


def init_db() -> None:
    # create tables
    Base.metadata.create_all(bind=engine)

    # optional: create an initial manager user
    from sqlalchemy import select

    db: Session = Session(bind=engine)

    try:
        existing = db.execute(select(User).where(User.username == "admin")).scalar_one_or_none()
        if existing is None:
            admin = User(
                username="admin",
                hashed_password=hash_password("admin123"),
                role="manager",
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()