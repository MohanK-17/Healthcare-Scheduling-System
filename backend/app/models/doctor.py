from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(String, primary_key=True)  # same as user.id
    specialization = Column(String, nullable=True)
    experience_years = Column(String, nullable=True)
    license_number = Column(String, nullable=True)

    user_id = Column(String, ForeignKey("users.id"), unique=True)
    user = relationship("User", backref="doctor_profile")
