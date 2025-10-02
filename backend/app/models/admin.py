# Save in: backend/app/models/admin.py
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base
import uuid



class Admin(Base):
    __tablename__ = "users"  # your actual table
    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    full_name = Column(String)
    email = Column(String)
    password = Column(String)  # store hashed passwords ideally
    role = Column(String)
    specialization = Column(String)