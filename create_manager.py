#!/usr/bin/env python3
"""
Admin script to create a manager user directly in the database.
Run this locally: python create_manager.py <username> <password>
"""

import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User, UserRole
from app.core.security import hash_password
from app.core.config import settings

if len(sys.argv) < 3:
    print("Usage: python create_manager.py <username> <password>")
    sys.exit(1)

username = sys.argv[1]
password = sys.argv[2]

# Create database connection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # Check if user exists
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        print(f"Error: User '{username}' already exists")
        sys.exit(1)
    
    # Create manager user
    user = User(
        username=username,
        email=f"{username}@ims.local",
        hashed_password=hash_password(password),
        role=UserRole.manager,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    print(f"✓ Manager user created successfully!")
    print(f"  Username: {user.username}")
    print(f"  Role: {user.role.value}")
    print(f"  ID: {user.id}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    db.close()
