from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="User Directory API V2", description="The 'Broken' Version")

# --- Schemas ---
# HARD CHANGE: Semantic split. 'username' is gone. replaced by first_name and last_name.
class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: str

class UserResponse(UserBase):
    id: int

fake_db = {}
current_id = 1

# --- Endpoints ---

# EASY CHANGE: Global Route Prefixing. All routes now start with /api/v2
@app.post("/api/v2/users", response_model=UserResponse, status_code=201)
def create_user(user: UserBase):
    global current_id
    new_user = UserResponse(id=current_id, **user.model_dump())
    fake_db[current_id] = new_user
    current_id += 1
    return new_user

# MEDIUM CHANGE: Response Envelope. Returns {"data": [...]} instead of [...]
@app.get("/api/v2/users")
def get_users():
    return {"data": list(fake_db.values()), "total_count": len(fake_db)}

@app.get("/api/v2/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    if user_id not in fake_db:
        raise HTTPException(status_code=404, detail="User not found")
    return fake_db[user_id]