import React, { useEffect, useState } from "react";
import { getAppointments, addAppointment, deleteAppointment, getDoctors } from "../api/admin";
import doctorSpecializationsData from "../data/doctorSpecializations.json";

const Appointments = () => {
  const [appointments, setAppointments] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [diagnoses, setDiagnoses] = useState([
    "Cardiology",
    "Dermatology",
    "Neurology",
    "Pediatrics",
    "Orthopedic",
    "ENT",
    "Psychiatry",
    "Gynecology",
    "General"
  ]);

  const [formData, setFormData] = useState({
    patient_name: "",
    age: "",
    diagnosis: "",
    doctor: "",
    date: ""
  });

  // Map diagnosis to JSON specialization
  const diagnosisToSpecialization = {
    "Cardiology": "Cardiologist",
    "Dermatology": "Dermatologist",
    "Neurology": "Neurologist",
    "Pediatrics": "Pediatrician",
    "Orthopedic": "Orthopedic",
    "ENT": "ENT",
    "Psychiatry": "Psychiatrist",
    "Gynecology": "Gynecologist",
    "General": "General"
  };

  // Fetch appointments
  const fetchAppointments = async () => {
    const data = await getAppointments();
    setAppointments(data);
  };

  // Fetch doctors
  const fetchDoctors = async () => {
    const data = await getDoctors();
    setDoctors(data);
  };

  useEffect(() => {
    fetchAppointments();
    fetchDoctors();
  }, []);

  // Reset doctor when diagnosis changes
  useEffect(() => {
    setFormData(prev => ({ ...prev, doctor: "" }));
  }, [formData.diagnosis]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Filter doctors based on diagnosis
  const availableDoctors = doctors.filter(d => {
    if (formData.diagnosis === "" || formData.diagnosis === "General") return true;
    const spec = doctorSpecializationsData.find(ds => ds.name === d.name);
    return spec?.specialization === diagnosisToSpecialization[formData.diagnosis];
  });

  // Convert ISO date-time to readable 12-hour format
  const displayTime12 = (iso) => {
    if (!iso) return "";
    const date = new Date(iso);
    let hours = date.getHours();
    const minutes = date.getMinutes().toString().padStart(2, "0");
    const ampm = hours >= 12 ? "PM" : "AM";
    hours = hours % 12 || 12;
    return `${hours.toString().padStart(2, "0")}:${minutes} ${ampm}`;
  };

  // Add appointment
  const handleAdd = async (e) => {
    e.preventDefault();
    if (!formData.patient_name || !formData.age || !formData.diagnosis || !formData.doctor || !formData.date) {
      alert("Please fill all fields");
      return;
    }

    const now = new Date().toISOString();

    const newApptData = {
      ...formData,
      age: Number(formData.age),
      time: now,       // current timestamp as appointment time
      created_at: now  // current timestamp as booking log
    };

    const newAppt = await addAppointment(newApptData);
    setAppointments([...appointments, newAppt]);

    setFormData({
      patient_name: "",
      age: "",
      diagnosis: "",
      doctor: "",
      date: ""
    });
  };

  // Delete appointment
  const handleDelete = async (id) => {
    await deleteAppointment(id);
    setAppointments(appointments.filter(a => a.appointment_id !== id));
  };

  return (
    <div>
      <h2>Appointments</h2>

      <form onSubmit={handleAdd} style={{ marginBottom: "20px" }}>
        <input
          name="patient_name"
          placeholder="Patient Name"
          value={formData.patient_name}
          onChange={handleChange}
          required
        />
        <input
          name="age"
          placeholder="Age"
          value={formData.age}
          onChange={handleChange}
          required
        />

        {/* Diagnosis Dropdown */}
        <select name="diagnosis" value={formData.diagnosis} onChange={handleChange} required>
          <option value="">Select Diagnosis</option>
          {diagnoses.map((d, idx) => <option key={idx} value={d}>{d}</option>)}
        </select>

        {/* Doctor Dropdown */}
        <select name="doctor" value={formData.doctor} onChange={handleChange} required>
          <option value="">Select Doctor</option>
          {availableDoctors.map(d => <option key={d.id} value={d.name}>{d.name}</option>)}
        </select>

        <input
          name="date"
          type="date"
          value={formData.date}
          onChange={handleChange}
          required
        />

        <button type="submit">Add Appointment</button>
      </form>

      <table border="1" style={{ marginTop: "20px", width: "100%" }}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Patient</th>
            <th>Age</th>
            <th>Diagnosis</th>
            <th>Doctor</th>
            <th>Date</th>
            <th>Appointment Time (Log)</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {appointments.map(a => (
            <tr key={a.appointment_id}>
              <td>{a.appointment_id}</td>
              <td>{a.patient_name}</td>
              <td>{a.age}</td>
              <td>{a.diagnosis}</td>
              <td>{a.doctor}</td>
              <td>{a.date}</td>
              <td>{displayTime12(a.time)}</td>
              <td>{a.status}</td>
              <td>
                <button onClick={() => handleDelete(a.appointment_id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Appointments;
