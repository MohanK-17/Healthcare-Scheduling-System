from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from pathlib import Path
import json
import secrets

from app.db.session import get_db
from app.models.user import User
from app.utils.email_utils import send_email

router = APIRouter(prefix="/doctor", tags=["Doctor"])

security = HTTPBasic()
APPOINTMENT_FILE = Path(__file__).parent.parent / "db" / "appointments.json"

# Load & Save Appointments
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

# Authentication
def get_current_doctor(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    doctor = db.query(User).filter(
        User.username == credentials.username,
        User.role == "doctor"
    ).first()
    if not doctor or not secrets.compare_digest(doctor.password_plain, credentials.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return doctor

# Login
class DoctorLogin(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(doctor_login: DoctorLogin, db: Session = Depends(get_db)):
    doctor = db.query(User).filter(
        User.username == doctor_login.username,
        User.role == "doctor"
    ).first()
    if not doctor or doctor.password_plain != doctor_login.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "doctor": doctor.full_name}

# View Appointments
@router.get("/appointments/pending")
def view_pending_appointments(current_doctor: User = Depends(get_current_doctor)):
    appointments = load_appointments()
    pending = [a for a in appointments if a.get("doctor") == current_doctor.full_name and a.get("status") == "pending"]
    return {"pending_appointments": pending}

# Accept/Reject Appointments
@router.put("/appointments/{appointment_id}/decision")
def decide_appointment(
    appointment_id: str,
    decision: str,  # "accepted" or "rejected"
    background_tasks: BackgroundTasks,
    current_doctor: User = Depends(get_current_doctor)
):
    if decision not in ["accepted", "rejected"]:
        raise HTTPException(status_code=400, detail="Decision must be 'accepted' or 'rejected'")

    appointments = load_appointments()
    found = False

    for a in appointments:
        if a.get("appointment_id") == appointment_id and a.get("doctor") == current_doctor.full_name:
            a["status"] = decision
            a["updated_at"] = datetime.utcnow().isoformat()
            found = True

            # Send email to patient
            patient_email = a.get("patient_email")
            patient_name = a.get("patient")
            time = a.get("time")
            if patient_email:
                if decision == "accepted":
                    subject = "Appointment Confirmed"
                    body = f"""
                    <p>Dear {patient_name},</p>
                    <p>Your appointment with Dr. {current_doctor.full_name} at <b>{time}</b> has been <b>confirmed</b>.</p>
                    <p>Appointment ID: {appointment_id}</p>
                    """
                else:
                    subject = "Appointment Rejected"
                    body = f"""
                    <p>Dear {patient_name},</p>
                    <p>We are sorry. Your appointment with Dr. {current_doctor.full_name} at <b>{time}</b> has been <b>rejected</b>.</p>
                    <p>Appointment ID: {appointment_id}</p>
                    """
                background_tasks.add_task(send_email, [patient_email], subject, body)
            break

    if not found:
        raise HTTPException(status_code=404, detail="Appointment not found")

    save_appointments(appointments)
    return {"message": f"Appointment {appointment_id} has been {decision}"}

# Doctor Profile
@router.get("/profile")
def view_profile(current_doctor: User = Depends(get_current_doctor)):
    return {
        "id": str(current_doctor.id),
        "name": current_doctor.full_name,
        "email": current_doctor.email,
        "username": current_doctor.username,
    }

@router.put("/profile")
def update_profile(
    name: str | None = None,
    email: str | None = None,
    password: str | None = None,
    db: Session = Depends(get_db),
    current_doctor: User = Depends(get_current_doctor)
):
    if name:
        current_doctor.full_name = name
    if email:
        current_doctor.email = email
    if password:
        current_doctor.password_plain = password
    db.commit()
    db.refresh(current_doctor)
    return {"message": "Profile updated successfully"}
