from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List
from datetime import datetime
import secrets
from pathlib import Path
import json

from app.db.session import get_db
from app.models.user import User
from app.utils.email_utils import send_email

router = APIRouter(prefix="/patient", tags=["Patient"])

# Path to appointments JSON
APPOINTMENT_FILE = Path(__file__).parent.parent / "db" / "appointments.json"

# Load & Save appointments helpers
def load_appointments() -> list[dict]:
    if not APPOINTMENT_FILE.exists():
        return []
    try:
        with open(APPOINTMENT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("appointments", [])
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid appointments.json")

def save_appointments(appointments: list[dict]):
    with open(APPOINTMENT_FILE, "w", encoding="utf-8") as f:
        json.dump({"appointments": appointments}, f, indent=4)


# Schemas

class PatientRegister(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    password: str

class PatientLogin(BaseModel):
    username: str
    password: str

class AppointmentBook(BaseModel):
    doctor_name: str
    doctor_email: EmailStr
    time: str  # e.g., "2025-10-02T15:00:00"


# Patient Registration/Login

@router.post("/register")
def register_patient(patient: PatientRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == patient.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_patient = User(
        username=patient.username,
        full_name=patient.full_name,
        email=patient.email,
        role="patient",
        password_plain=patient.password  # For simplicity; ideally hash
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return {"message": "Patient registered successfully"}

@router.post("/login")
def login_patient(patient_login: PatientLogin, db: Session = Depends(get_db)):
    patient = db.query(User).filter(
        User.username == patient_login.username,
        User.role == "patient"
    ).first()
    if not patient or not secrets.compare_digest(patient.password_plain, patient_login.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "patient": patient.full_name}

# Appointment Booking

@router.post("/appointments/book")
async def book_appointment(
    appointment: AppointmentBook,
    patient_username: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Get patient info
    patient = db.query(User).filter(User.username == patient_username, User.role == "patient").first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    appointments = load_appointments()
    appointment_id = f"APT-{int(datetime.utcnow().timestamp())}"

    new_appointment = {
        "appointment_id": appointment_id,
        "doctor": appointment.doctor_name,
        "doctor_email": appointment.doctor_email,
        "patient": patient.full_name,
        "patient_email": patient.email,
        "time": appointment.time,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }

    appointments.append(new_appointment)
    save_appointments(appointments)

    # Notify doctor about new appointment
    body = f"""
    <p>Dear Dr. {appointment.doctor_name},</p>
    <p>New appointment booked by <b>{patient.full_name}</b> at <b>{appointment.time}</b>.</p>
    <p>Appointment ID: {appointment_id}</p>
    <p>Status: Pending. Please accept or reject.</p>
    """
    background_tasks.add_task(send_email, [appointment.doctor_email], "New Appointment Pending", body)

    return {"message": "Appointment booked successfully", "appointment_id": appointment_id}


# View Patient Appointments

@router.get("/appointments/{patient_username}", response_model=List[dict])
def view_my_appointments(patient_username: str, db: Session = Depends(get_db)):
    patient = db.query(User).filter(User.username == patient_username, User.role == "patient").first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    appointments = load_appointments()
    my_appointments = [a for a in appointments if a.get("patient") == patient.full_name]
    return my_appointments
