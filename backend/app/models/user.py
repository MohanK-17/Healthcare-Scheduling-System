import uuid
from sqlalchemy import Column, String, Enum
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base

# Optional: define roles
from enum import Enum as PyEnum

class UserRole(PyEnum):
    doctor = "doctor"
    patient = "patient"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    role = Column(String, nullable=False)  # could also use Enum(UserRole)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False)
    password_plain = Column(String, nullable=False)  # store hashed password in real app
    specialization = Column(String, nullable=True)