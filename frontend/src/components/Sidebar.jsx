import React from "react";
import { Link } from "react-router-dom";

export default function Sidebar() {
  return (
    <div style={{ width: "200px", padding: "20px", background: "#f0f0f0", height: "100vh" }}>
      <h3>Admin Panel</h3>
      <nav>
        <ul style={{ listStyle: "none", padding: 0 }}>
          <li style={{ margin: "10px 0" }}>
            <Link to="/dashboard">Dashboard</Link>
          </li>
          <li style={{ margin: "10px 0" }}>
            <Link to="/doctors">Doctors</Link>
          </li>
          <li style={{ margin: "10px 0" }}>
            <Link to="/appointments">Appointments</Link>
          </li>
        </ul>
      </nav>
    </div>
  );
}
