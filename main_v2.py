from fastapi import FastAPI, Header, Query, Path
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
import uuid

app = FastAPI(
    title="User Directory API V2", 
    description="The 'Broken' Version containing 10 taxonomy changes."
)

# --- Schemas ---

# HARD 9: Enum Validation. The LLM cannot hallucinate roles; it must strictly use "admin" or "customer".
class RoleEnum(str, Enum):
    admin = "admin"
    customer = "customer"

# HARD 8: Semantic Split ('username' replaced by 'first_name' and 'last_name')
# EASY 2: Payload Key Rename ('email' renamed to 'contact_email')
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    contact_email: str
    role: RoleEnum

# EASY 3: Response Key Rename ('id' renamed to 'user_id')
class UserResponse(BaseModel):
    user_id: uuid.UUID
    first_name: str
    last_name: str
    contact_email: str
    role: RoleEnum

# In-Memory DB (Keys are now UUIDs instead of integers)
fake_db = {}

# --- Endpoints ---

# EASY 1: Global Route Prefixing (/api/v2)
# MEDIUM 5: Mandatory Headers (x-api-version is required on all routes)
@app.post("/api/v2/users", response_model=UserResponse, status_code=201)
def create_user(
    user: UserCreate, 
    x_api_version: str = Header(..., description="Strictly requires header 'X-API-Version'")
):
    new_id = uuid.uuid4()
    # model_dump() replaces dict() in Pydantic v2
    new_user = UserResponse(user_id=new_id, **user.model_dump())
    fake_db[new_id] = new_user
    return new_user

# MEDIUM 4: Response Envelope (Returns {"data": [...]} instead of a flat list)
# MEDIUM 7: Pagination (limit and offset are now strictly required query parameters)
@app.get("/api/v2/users")
def get_users(
    limit: int = Query(..., gt=0),
    offset: int = Query(..., ge=0),
    x_api_version: str = Header(...)
):
    all_users = list(fake_db.values())
    paginated_users = all_users[offset : offset + limit]
    return {
        "data": paginated_users, 
        "total_count": len(all_users)
    }

# MEDIUM 6: Path Variable Type Change (user_id is now a UUID, not an integer)
# HARD 10: Error Paradigm Shift (Returns 200 OK with a custom error JSON instead of 404)
@app.get("/api/v2/users/{user_id}")
def get_user(
    user_id: uuid.UUID = Path(...),
    x_api_version: str = Header(...)
):
    if user_id not in fake_db:
        # Returning a 200 OK manually to break traditional 404 testing assertions
        return {"success": False, "error": "User not found", "data": None}
    
    return fake_db[user_id]