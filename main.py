from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

# The OpenAPI schema will be automatically generated at /openapi.json
app = FastAPI(title="User Directory API V1", description="Sandbox for Self-Healing Agents")

# --- Schemas ---
class UserBase(BaseModel):
    username: str
    email: str

class UserResponse(UserBase):
    id: int

# --- In-Memory Database ---
fake_db = {}
current_id = 1

# --- Endpoints ---

# 1. Create a new user
@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserBase):
    global current_id
    new_user = UserResponse(id=current_id, **user.model_dump())
    fake_db[current_id] = new_user
    current_id += 1
    return new_user

# 2. Get all users
@app.get("/users", response_model=List[UserResponse])
def get_users():
    return list(fake_db.values())

# 3. Get a specific user by ID
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    if user_id not in fake_db:
        raise HTTPException(status_code=404, detail="User not found")
    return fake_db[user_id]