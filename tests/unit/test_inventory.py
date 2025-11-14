# tests/unit/test_inventory.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.core.security import hash_password
from app.models.user import User, UserRole

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # or "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def manager_user():
    db = TestingSessionLocal()
    user = User(
        email="manager@test.com",
        hashed_password=hash_password("password"),
        role=UserRole.manager,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user

def get_token(client, email, password):
    response = client.post(
        "/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]

def test_create_item(client, manager_user):
    token = get_token(client, manager_user.email, "password")
    resp = client.post(
        "/items/",
        json={
            "name": "Test Item",
            "description": "desc",
            "sku": "SKU1",
            "quantity": 10,
            "low_stock_threshold": 5,
            "price": 12.5,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Test Item"
    assert data["quantity"] == 10