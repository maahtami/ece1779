# app/db/init_db.py
import os
from sqlalchemy.orm import sessionmaker
from app.database import Base, engine
from app.models.user import User, UserRole
from app.models.item import Item
from app.models.transaction import Transaction
from app.core.security import hash_password

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Create first manager if needed (for production deployments)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if any manager exists
        manager_exists = db.query(User).filter(User.role == UserRole.manager).first()
        if not manager_exists:
            # Try to create from environment variables (for Fly.io deployment)
            admin_username = os.getenv("ADMIN_USERNAME", "manager")
            admin_password = os.getenv("ADMIN_PASSWORD", "managerpass123")
            
            if admin_username and admin_password:
                user = User(
                    username=admin_username,
                    email=f"{admin_username}@ims.local",
                    hashed_password=hash_password(admin_password),
                    role=UserRole.manager,
                    is_active=True
                )
                db.add(user)
                db.commit()
                print(f"✓ Initial manager user created: {admin_username}")
    except Exception as e:
        print(f"Note: Could not create initial manager: {e}")

    finally:
        db.close()