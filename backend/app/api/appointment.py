from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from pathlib import Path
import json

from app.db.session import get_db
from app.models.user import User
from app.utils.email_utils import send_email

router = APIRouter(prefix="/appointments", tags=["appointments"])

APPOINTMENT_FILE = Path(__file__).parent.parent / "db" / "appointments.json"

def load_appointments() -> list[dict]:
    if not APPOINTMENT_FILE.exists():
        return []
    with open(APPOINTMENT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("appointments", [])

def save_appointments(appointments: list[dict]):
    with open(APPOINTMENT_FILE, "w", encoding="utf-8") as f:
        json.dump({"appointments": appointments}, f, indent=4)

@router.post("/book")
async def book_appointment(
    doctor_name: str,
    patient_name: str,
    time: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    appointments = load_appointments()
    
    appointment_id = f"APT-{int(datetime.utcnow().timestamp())}"
    appointment = {
        "appointment_id": appointment_id,
        "doctor": doctor_name,
        "patient": patient_name,
        "time": time,
        "status": "booked",
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    appointments.append(appointment)
    save_appointments(appointments)

    
    doctor = db.query(User).filter(User.full_name == doctor_name).first()
    if doctor and doctor.email:
        body = f"""
        <p>Dear Dr. {doctor.full_name},</p>
        <p>You have a new appointment booked by <b>{patient_name}</b> at <b>{time}</b>.</p>
        <p>Appointment ID: {appointment_id}</p>
        """
        background_tasks.add_task(send_email, [doctor.email], "New Appointment Booked", body)

    return {"message": "Appointment booked successfully", "appointment_id": appointment_id}
