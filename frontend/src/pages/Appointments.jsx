import React, { useEffect, useState } from "react";
import { getAppointments, addAppointment, deleteAppointment, getDoctors } from "../api/admin";
import doctorSpecializationsData from "../data/doctorSpecializations.json"; // frontend JSON for doctor specializations

const Appointments = () => {
  const [appointments, setAppointments] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [specializations, setSpecializations] = useState([]);
  const [formData, setFormData] = useState({
    patient_name: "",
    age: "",
    diagnosis: "",
    specialization: "General",
    doctor: "",
    date: "",
    time: "",
    am_pm: "AM"
  });

  // Fetch appointments
  const fetchAppointments = async () => {
    const data = await getAppointments();
    setAppointments(data);
  };

  // Fetch doctors from backend + specializations from JSON
  const fetchDoctors = async () => {
    const data = await getDoctors();
    setDoctors(data);

    // extract unique specializations from JSON
    const specs = doctorSpecializationsData.map(d => d.specialization);
    const uniqueSpecs = Array.from(new Set(specs));
    setSpecializations(["General", ...uniqueSpecs]);
  };

  useEffect(() => {
    fetchAppointments();
    fetchDoctors();
  }, []);

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  // Filter doctors by selected specialization
  const filteredDoctors = formData.specialization === "General"
    ? doctors
    : doctors.filter(d => {
        const specObj = doctorSpecializationsData.find(ds => ds.name === d.name);
        return specObj?.specialization === formData.specialization;
      });

  const handleAdd = async (e) => {
    e.preventDefault();
    const formattedData = {
      ...formData,
      age: Number(formData.age),
      time: `${formData.time} ${formData.am_pm}`
    };

    const newAppt = await addAppointment(formattedData);
    setAppointments([...appointments, newAppt]);

    setFormData({
      patient_name: "",
      age: "",
      diagnosis: "",
      specialization: "General",
      doctor: "",
      date: "",
      time: "",
      am_pm: "AM"
    });
  };

  const handleDelete = async (id) => {
    await deleteAppointment(id);
    setAppointments(appointments.filter((a) => a.appointment_id !== id));
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
          type="number"
          value={formData.age}
          onChange={handleChange}
          required
        />
        

        {/* Specialization Dropdown */}
        <select name="specialization" value={formData.specialization} onChange={handleChange}>
          {specializations.map((spec, idx) => (
            <option key={idx} value={spec}>{spec}</option>
          ))}
        </select>

        {/* Doctor Dropdown filtered by specialization */}
        <select name="doctor" value={formData.doctor} onChange={handleChange} required>
          <option value="">Select Doctor</option>
          {filteredDoctors.map(d => (
            <option key={d.id} value={d.name}>{d.name}</option>
          ))}
        </select>

        <input
          name="date"
          type="date"
          value={formData.date}
          onChange={handleChange}
          required
        />

        <input
          name="time"
          type="time"
          value={formData.time}
          onChange={handleChange}
          required
        />

        <select name="am_pm" value={formData.am_pm} onChange={handleChange}>
          <option value="AM">AM</option>
          <option value="PM">PM</option>
        </select>

        <button type="submit">Add Appointment</button>
      </form>

      <table border="1" style={{ marginTop: "20px", width: "100%" }}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Patient</th>
            <th>Age</th>
            <th>Diagnosis</th>
            <th>Specialization</th>
            <th>Doctor</th>
            <th>Date</th>
            <th>Time</th>
            <th>Status</th>
            <th>Created At</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {appointments.map((a) => (
            <tr key={a.appointment_id}>
              <td>{a.appointment_id}</td>
              <td>{a.patient_name}</td>
              <td>{a.age}</td>
              <td>{a.diagnosis}</td>
              <td>{a.specialization || "General"}</td>
              <td>{a.doctor}</td>
              <td>{a.date}</td>
              <td>{a.time}</td>
              <td>{a.status}</td>
              <td>{a.created_at}</td>
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
