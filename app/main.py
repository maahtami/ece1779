from fastapi import FastAPI

from app.db.init_db import init_db
from app.routers import auth, users, inventory, transactions


app = FastAPI(title="IMS Inventory API")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {"message": "Inventory API running!"}


# Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(inventory.router)
app.include_router(transactions.router)