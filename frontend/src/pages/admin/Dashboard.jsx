import React, { useEffect, useState } from "react";
import Sidebar from "../../components/admin/Sidebar";
import { getDoctors, getAppointments } from "../../api/admin";

export default function Dashboard({ admin }) {
  const [doctors, setDoctors] = useState([]);
  const [appointments, setAppointments] = useState([]);

  // Random specializations for demo
  const specializations = [
    "Cardiology",
    "Neurology",
    "Dermatology",
    "Pediatrics",
    "Orthopedics",
    "Oncology",
    "Endocrinology",
    "ENT",
    "Radiology",
    "Gastroenterology",
  ];

  useEffect(() => {
    const fetchData = async () => {
      try {
        const docs = await getDoctors();
        const apps = await getAppointments();
        // assign each doctor a random specialization if not present
        const withSpec = docs.map((d, i) => ({
          ...d,
          specialization: specializations[i % specializations.length],
        }));
        setDoctors(withSpec);
        setAppointments(apps);
      } catch (err) {
        console.error("Error loading dashboard data:", err);
      }
    };
    fetchData();
  }, []);

  return (
    <div style={{ display: "flex" }}>
      <Sidebar />
      <div style={{ margin: "20px", flex: 1 }}>
        <h2>Welcome, {admin}</h2>
        <p>Here’s a quick overview of your system.</p>

        {/* Doctors Section */}
        <h3>Doctors Overview</h3>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
            gap: "15px",
            marginBottom: "30px",
          }}
        >
          {doctors.map((doc) => (
            <div
              key={doc.id}
              style={{
                border: "1px solid #ddd",
                borderRadius: "8px",
                padding: "15px",
                background: "#f9f9f9",
                boxShadow: "0px 2px 6px rgba(0,0,0,0.1)",
              }}
            >
              <h4>{doc.name}</h4>
              <p style={{ margin: "5px 0", color: "#666" }}>
                {doc.specialization}
              </p>
              <p style={{ fontSize: "12px", color: "#999" }}>{doc.email}</p>
            </div>
          ))}
        </div>

        {/* Appointments Section */}
        <h3>Recent Appointments</h3>
        <table
          border="1"
          cellPadding="8"
          style={{
            width: "100%",
            borderCollapse: "collapse",
            marginTop: "10px",
            background: "#fff",
          }}
        >
          <thead style={{ background: "#f0f0f0" }}>
            <tr>
              <th>ID</th>
              <th>Patient</th>
              <th>Age</th>
              <th>Diagnosis</th>
              <th>Doctor</th>
              <th>Date</th>
              <th>Time</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {appointments.length > 0 ? (
              appointments.map((a) => (
                <tr key={a.appointment_id}>
                  <td>{a.appointment_id}</td>
                  <td>{a.patient_name}</td>
                  <td>{a.age}</td>
                  <td>{a.diagnosis}</td>
                  <td>{a.doctor}</td>
                  <td>{a.date}</td>
                  <td>{a.time}</td>
                  <td>{a.status}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="8" style={{ textAlign: "center" }}>
                  No appointments found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
