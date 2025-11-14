# app/routers/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.core.config import settings
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
ALGORITHM = "HS256"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        user_id: int | None = payload.get("sub")
        if user_id is None:
            raise cred_exc
    except JWTError:
        raise cred_exc

    user = db.query(User).get(int(user_id))
    if user is None:
        raise cred_exc
    return user

def get_current_manager(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.manager:
        raise HTTPException(status_code=403, detail="Managers only")
    return current_user

def get_current_staff_or_manager(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in {UserRole.manager, UserRole.staff}:
        raise HTTPException(status_code=403, detail="Unauthorized role")
    return current_user