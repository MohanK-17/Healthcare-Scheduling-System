from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path
import json
import uuid
import secrets
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["admin"])

security = HTTPBasic()

# ======================
# Hardcoded admin credentials
# ======================
ADMINS = [
    {"username": "danielle.johnsonA01", "password": "Admin#01Pass", "full_name": "Danielle Johnson", "email": "danielle.johnsonA01@example.com"},
    {"username": "john.taylorA02", "password": "Admin#02Pass", "full_name": "John Taylor", "email": "john.taylorA02@example.com"},
    {"username": "erica.mcclainA03", "password": "Admin#03Pass", "full_name": "Erica McClain", "email": "erica.mcclainA03@example.com"},
]

# ======================
# Appointment file
# ======================
APPOINTMENT_FILE = Path(__file__).parent.parent / "db" / "appointments.json"

def load_appointments() -> list[dict]:
    if not APPOINTMENT_FILE.exists():
        return []
    try:
        with open(APPOINTMENT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "appointments" in data:
            return data["appointments"]
        raise HTTPException(status_code=500, detail="appointments.json format invalid")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="appointments.json is invalid JSON")

def save_appointments(appointments: list[dict]):
    with open(APPOINTMENT_FILE, "w", encoding="utf-8") as f:
        json.dump({"appointments": appointments}, f, indent=4)

# ======================
# Admin verification
# ======================
def verify_admin(username: str, password: str) -> dict | None:
    for admin in ADMINS:
        if secrets.compare_digest(admin["username"], username) and secrets.compare_digest(admin["password"], password):
            return admin
    return None

def get_current_admin(credentials: HTTPBasicCredentials = Depends(security)) -> dict:
    admin = verify_admin(credentials.username, credentials.password)
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return admin

# ======================
# Admin Login
# ======================
class AdminLogin(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(admin_login: AdminLogin, db: Session = Depends(get_db)):
    admin = db.query(User).filter(
        User.username == admin_login.username,
        User.role == "admin"
    ).first()
    if not admin or admin.password_plain != admin_login.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "admin": admin.username}

# ======================
# Doctor CRUD
# ======================
@router.get("/doctors", response_model=List[dict])
def list_doctors(db: Session = Depends(get_db), current_admin: dict = Depends(get_current_admin)):
    doctors = db.query(User).filter(User.role == "doctor").all()
    return [
        {
            "id": str(d.id),
            "name": d.full_name,
            "email": d.email,
            "specialization": d.specialization
        }
        for d in doctors
    ]

@router.post("/doctors")
def add_doctor(
    username: str,
    full_name: str,
    email: str,
    password: str,
    specialization: str,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    new_doctor = User(
        id=str(uuid.uuid4()),
        role="doctor",
        username=username,
        full_name=full_name,
        email=email,
        password_plain=password,
        specialization=specialization
    )
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    return {"message": f"Doctor {full_name} added successfully", "id": str(new_doctor.id)}

@router.put("/doctors/{doctor_id}")
def update_doctor(
    doctor_id: str,
    name: str | None = None,
    email: str | None = None,
    specialization: str | None = None,
    password: str | None = None,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    doctor = db.query(User).filter(User.id == doctor_id, User.role == "doctor").first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    if name:
        doctor.full_name = name
    if email:
        doctor.email = email
    if specialization:
        doctor.specialization = specialization
    if password:
        doctor.password_plain = password
    db.commit()
    db.refresh(doctor)
    return {"message": f"Doctor {doctor.full_name} updated successfully"}

@router.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: str, db: Session = Depends(get_db), current_admin: dict = Depends(get_current_admin)):
    doctor = db.query(User).filter(User.id == doctor_id, User.role == "doctor").first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    db.delete(doctor)
    db.commit()
    return {"message": f"Doctor {doctor.full_name} deleted successfully"}
# #---patient----
# @router.get("/patients", response_model=List[dict])
# def list_patients(db: Session = Depends(get_db), current_admin: dict = Depends(get_current_admin)):
#     patients = db.query(User).filter(User.role == "patient").all()
#     return [
#         {
#             "id": str(p.id),
#             "name": p.full_name,
#             "email": p.email,
#             "username": p.username,
#             "age": getattr(p, "age", None),  # optional if stored in User model
#             "gender": getattr(p, "gender", None)
#         }
#         for p in patients
#     ]

# ======================
# Appointment Management
# ======================
@router.get("/appointments")
def view_appointments(current_admin: dict = Depends(get_current_admin)):
    """View all appointments"""
    return {"appointments": load_appointments()}

@router.get("/appointments/doctor/{doctor_id}")
def view_appointments_by_doctor(doctor_id: str, current_admin: dict = Depends(get_current_admin)):
    """View all appointments assigned to a specific doctor"""
    appointments = load_appointments()
    doctor_appointments = [a for a in appointments if str(a.get("doctor_id")) == doctor_id]
    return {"appointments": doctor_appointments}

@router.post("/appointments/assign")
def assign_appointment_to_doctor(
    appointment_id: str,
    doctor_id: str,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Assign an existing appointment to a doctor"""
    appointments = load_appointments()
    for appt in appointments:
        if appt["appointment_id"] == appointment_id:
            doctor = db.query(User).filter(User.id == doctor_id, User.role == "doctor").first()
            if not doctor:
                raise HTTPException(status_code=404, detail="Doctor not found")
            appt["doctor_id"] = doctor_id
            appt["doctor"] = doctor.full_name
            save_appointments(appointments)
            return {"message": f"Appointment {appointment_id} assigned to Dr. {doctor.full_name}"}
    raise HTTPException(status_code=404, detail="Appointment not found")

@router.put("/appointments/{appointment_id}")
def update_appointment(
    appointment_id: str,
    diagnosis: str | None = None,
    date: str | None = None,
    time: str | None = None,
    status_value: str | None = None,
    current_admin: dict = Depends(get_current_admin)
):
    """Update appointment details"""
    appointments = load_appointments()
    for appt in appointments:
        if appt["appointment_id"] == appointment_id:
            if diagnosis:
                appt["diagnosis"] = diagnosis
            if date:
                appt["date"] = date
            if time:
                appt["time"] = time
            if status_value:
                appt["status"] = status_value
            save_appointments(appointments)
            return {"message": f"Appointment {appointment_id} updated successfully"}
    raise HTTPException(status_code=404, detail="Appointment not found")

@router.delete("/appointments/doctor/{doctor_id}")
def delete_appointments_by_doctor(doctor_id: str, current_admin: dict = Depends(get_current_admin)):
    """Delete all appointments for a given doctor"""
    appointments = load_appointments()
    remaining = [a for a in appointments if str(a.get("doctor_id")) != doctor_id]
    deleted_count = len(appointments) - len(remaining)
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="No appointments found for this doctor")
    save_appointments(remaining)
    return {"message": f"Deleted {deleted_count} appointments for doctor ID {doctor_id}"}
