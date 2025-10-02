# backend/app/api/admin.py
""" from fastapi import APIRouter, Depends, HTTPException, status
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
    # Debug print: see what password Swagger is actually sending
    print(f"[DEBUG] Admin login attempt: {credentials.username} / {credentials.password}")
    admin = verify_admin(credentials.username, credentials.password)
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return admin

# ======================
# Login endpoint
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
# Appointments Endpoints
# ======================
@router.get("/appointments")
def view_appointments(current_admin: dict = Depends(get_current_admin)):
    return {"appointments": load_appointments()}

@router.post("/appointments")
def add_appointment(
    patient_name: str,
    age: int,
    diagnosis: str,
    doctor: str,
    date: str,
    time: str,
    current_admin: dict = Depends(get_current_admin)
):
    appointments = load_appointments()
    if appointments:
        last_id = appointments[-1]["appointment_id"]
        number = int(last_id.split("-")[1])
        new_id = f"APT-{number+1:05d}"
    else:
        new_id = "APT-10001"

    new_appointment = {
        "appointment_id": new_id,
        "patient_name": patient_name,
        "age": age,
        "diagnosis": diagnosis,
        "doctor": doctor,
        "date": date,
        "time": time,
        "status": "booked",
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

    appointments.append(new_appointment)
    save_appointments(appointments)
    return {"message": "Appointment added successfully", "appointment": new_appointment}

@router.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: str, current_admin: dict = Depends(get_current_admin)):
    appointments = load_appointments()
    updated_appointments = [a for a in appointments if str(a.get("appointment_id")) != appointment_id]
    if len(updated_appointments) == len(appointments):
        raise HTTPException(status_code=404, detail=f"Appointment {appointment_id} not found")
    save_appointments(updated_appointments)
    return {"message": f"Appointment {appointment_id} deleted successfully"}

# ======================
# Doctor CRUD with DB
# ======================
@router.get("/doctors", response_model=List[dict])
def list_doctors(db: Session = Depends(get_db), current_admin: dict = Depends(get_current_admin)):
    doctors = db.query(User).filter(User.role == "doctor").all()
    return [{"id": str(d.id), "name": d.full_name, "email": d.email} for d in doctors]

@router.post("/doctors")
def add_doctor(name: str, email: str, db: Session = Depends(get_db), current_admin: dict = Depends(get_current_admin)):
    new_doctor = User(
        id=str(uuid.uuid4()),
        role="doctor",
        full_name=name,
        email=email,
        username=email,
        password_plain="temp"
    )
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    return {"message": f"Doctor {name} added successfully", "id": str(new_doctor.id)}

@router.put("/doctors/{doctor_id}")
def update_doctor(
    doctor_id: str,
    name: str | None = None,
    email: str | None = None,
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

 """

# backend/app/api/admin.py
# backend/app/api/admin.py
# backend/app/api/admin.py
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
    print(f"[DEBUG] Admin login attempt: {credentials.username} / {credentials.password}")
    admin = verify_admin(credentials.username, credentials.password)
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return admin

# ======================
# Login endpoint
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
# Appointments Endpoints
# ======================
@router.get("/appointments")
def view_appointments(current_admin: dict = Depends(get_current_admin)):
    return {"appointments": load_appointments()}

@router.post("/appointments")
def add_appointment(
    patient_name: str,
    age: int,
    diagnosis: str,
    doctor: str,
    date: str,
    time: str,
    current_admin: dict = Depends(get_current_admin)
):
    appointments = load_appointments()
    if appointments:
        last_id = appointments[-1]["appointment_id"]
        number = int(last_id.split("-")[1])
        new_id = f"APT-{number+1:05d}"
    else:
        new_id = "APT-10001"

    new_appointment = {
        "appointment_id": new_id,
        "patient_name": patient_name,
        "age": age,
        "diagnosis": diagnosis,
        "doctor": doctor,
        "date": date,
        "time": time,
        "status": "booked",
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

    appointments.append(new_appointment)
    save_appointments(appointments)
    return {"message": "Appointment added successfully", "appointment": new_appointment}

@router.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: str, current_admin: dict = Depends(get_current_admin)):
    appointments = load_appointments()
    updated_appointments = [a for a in appointments if str(a.get("appointment_id")) != appointment_id]
    if len(updated_appointments) == len(appointments):
        raise HTTPException(status_code=404, detail=f"Appointment {appointment_id} not found")
    save_appointments(updated_appointments)
    return {"message": f"Appointment {appointment_id} deleted successfully"}

# ======================
# Doctor CRUD with DB
# ======================
@router.get("/doctors", response_model=List[dict])
def list_doctors(db: Session = Depends(get_db), current_admin: dict = Depends(get_current_admin)):
    doctors = db.query(User).filter(User.role == "doctor").all()
    # Only send name, email, specialization
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
    name: str,
    email: str,
    specialization: str,
    password: str,   # ✅ Admin sets doctor password
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    new_doctor = User(
        id=str(uuid.uuid4()),
        role="doctor",
        full_name=name,
        email=email,
        username=email,
        password_plain=password,  # ✅ Store given password
        specialization=specialization
    )
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    return {
        "message": f"Doctor {name} added successfully",
        "id": str(new_doctor.id),
        "specialization": new_doctor.specialization
    }

@router.put("/doctors/{doctor_id}")
def update_doctor(
    doctor_id: str,
    name: str | None = None,
    email: str | None = None,
    specialization: str | None = None,
    password: str | None = None,   # ✅ Allow updating password
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
        doctor.password_plain = password   # ✅ Update password if provided
    db.commit()
    db.refresh(doctor)
    return {
        "message": f"Doctor {doctor.full_name} updated successfully",
        "specialization": doctor.specialization
    }

@router.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: str, db: Session = Depends(get_db), current_admin: dict = Depends(get_current_admin)):
    doctor = db.query(User).filter(User.id == doctor_id, User.role == "doctor").first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    db.delete(doctor)
    db.commit()
    return {"message": f"Doctor {doctor.full_name} deleted successfully"}
