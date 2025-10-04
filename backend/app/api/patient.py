from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List
from datetime import datetime
from pathlib import Path
import secrets
import json

from app.db.session import get_db
from app.models.user import User
from app.utils.email_utils import send_email

router = APIRouter(prefix="/patient", tags=["Patient"])

# JSON file path
APPOINTMENT_FILE = Path(__file__).parent.parent / "db" / "appointments.json"

# ========================
# Helper Functions
# ========================
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
    try:
        with open(APPOINTMENT_FILE, "w", encoding="utf-8") as f:
            json.dump({"appointments": appointments}, f, indent=4)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving appointments: {e}")


# ========================
# Schemas
# ========================
class PatientRegister(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    password: str


class PatientLogin(BaseModel):
    username: str
    password: str


class AppointmentBook(BaseModel):
    doctor_id: str
    time: str  # "2025-10-02T15:00:00" or simple string like "10:30 AM"


# ========================
# Patient Registration / Login
# ========================
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
        password_plain=patient.password
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

    return {"message": "Login successful", "patient_username": patient.username}


# ========================
# Appointment Booking
# ========================
@router.post("/appointments/book")
async def book_appointment(
    appointment: AppointmentBook,
    patient_username: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Get patient
    patient = db.query(User).filter(User.username == patient_username, User.role == "patient").first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Get doctor
    doctor = db.query(User).filter(User.id == appointment.doctor_id, User.role == "doctor").first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Create new appointment
    appointments = load_appointments()
    appointment_id = f"APT-{int(datetime.utcnow().timestamp())}"

    new_appointment = {
        "appointment_id": appointment_id,
        "doctor_id": str(doctor.id),
        "doctor_name": doctor.full_name,
        "doctor_email": doctor.email,
        "specialization": doctor.specialization,
        "patient_username": patient.username,     # unique for lookup
        "patient_full_name": patient.full_name,   # for display
        "patient_email": patient.email,
        "time": appointment.time,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }

    appointments.append(new_appointment)
    save_appointments(appointments)

    # Email doctor
    body = f"""
    <p>Dear Dr. {doctor.full_name},</p>
    <p>New appointment booked by <b>{patient.full_name}</b> at <b>{appointment.time}</b>.</p>
    <p>Appointment ID: <b>{appointment_id}</b></p>
    <p>Specialization: {doctor.specialization}</p>
    <p>Status: Pending.</p>
    """
    background_tasks.add_task(send_email, [doctor.email], "New Appointment", body)

    return {"message": "Appointment booked successfully", "appointment_id": appointment_id}


# ========================
# View Appointments
# ========================
@router.get("/appointments/{patient_username}", response_model=List[dict])
def view_my_appointments(patient_username: str, db: Session = Depends(get_db)):
    patient = db.query(User).filter(User.username == patient_username, User.role == "patient").first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    appointments = load_appointments()
    my_appointments = [a for a in appointments if a.get("patient_username") == patient.username]
    return my_appointments


# ========================
# Reschedule Appointment
# ========================
@router.put("/appointments/reschedule/{appointment_id}")
def reschedule_appointment(
    appointment_id: str,
    new_time: str,
    patient_username: str,
    background_tasks: BackgroundTasks
):
    appointments = load_appointments()
    appointment = next(
        (a for a in appointments if a["appointment_id"] == appointment_id and a["patient_username"] == patient_username),
        None
    )

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appointment["time"] = new_time
    appointment["status"] = "rescheduled"
    save_appointments(appointments)

    # Email doctor
    body = f"""
    <p>Dear Dr. {appointment['doctor_name']},</p>
    <p>Appointment <b>{appointment_id}</b> has been rescheduled by <b>{appointment['patient_full_name']}</b> to <b>{new_time}</b>.</p>
    """
    background_tasks.add_task(send_email, [appointment["doctor_email"]], "Appointment Rescheduled", body)

    return {"message": "Appointment rescheduled successfully"}


# ========================
# Cancel Appointment
# ========================
@router.delete("/appointments/cancel/{appointment_id}")
def cancel_appointment(
    appointment_id: str,
    patient_username: str,
    background_tasks: BackgroundTasks
):
    appointments = load_appointments()
    appointment = next(
        (a for a in appointments if a["appointment_id"] == appointment_id and a["patient_username"] == patient_username),
        None
    )

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appointments.remove(appointment)
    save_appointments(appointments)

    # Email doctor
    body = f"""
    <p>Dear Dr. {appointment['doctor_name']},</p>
    <p>Appointment <b>{appointment_id}</b> has been cancelled by <b>{appointment['patient_full_name']}</b>.</p>
    """
    background_tasks.add_task(send_email, [appointment["doctor_email"]], "Appointment Cancelled", body)

    return {"message": "Appointment cancelled successfully"}
