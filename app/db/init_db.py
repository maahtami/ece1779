from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.db.models import User

def init_db():
    db: Session = SessionLocal()

    # Check if admin already exists
    admin = db.query(User).filter(User.username == "admin").first()

    if not admin:
        admin = User(
            username="admin",
            hashed_password=hash_password("admin123"),
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

    db.close()