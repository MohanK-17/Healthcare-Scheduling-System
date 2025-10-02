# Save in: backend/app/schemas/admin.py
from pydantic import BaseModel

class AdminLogin(BaseModel):
    username: str
    password: str

class AdminResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
