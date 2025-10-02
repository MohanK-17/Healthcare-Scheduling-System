/* 
import React, { useEffect, useState } from "react";
import { getDoctors, addDoctor, updateDoctor, deleteDoctor } from "../api/admin";
import doctorSpecsJSON from "../data/doctorSpecializations.json";

const Doctors = () => {
  const [doctors, setDoctors] = useState([]);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [specialization, setSpecialization] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const [editingId, setEditingId] = useState(null);
  const [editName, setEditName] = useState("");
  const [editEmail, setEditEmail] = useState("");
  const [editSpec, setEditSpec] = useState("");

  // In-memory copy of specialization JSON
  const [doctorSpecs, setDoctorSpecs] = useState(doctorSpecsJSON);

  // Fetch doctors from backend
  const fetchDoctors = async () => {
    try {
      setLoading(true);
      const data = await getDoctors();
      // Merge specialization
      const merged = data.map(d => {
        const spec = doctorSpecs.find(ds => ds.name === d.name);
        return { ...d, specialization: spec ? spec.specialization : "" };
      });
      setDoctors(merged);
      setLoading(false);
    } catch (err) {
      console.error("Fetch doctors error:", err.response || err);
      setError("Failed to fetch doctors");
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDoctors();
  }, []);

  // Add new doctor
  const handleAdd = async () => {
    if (!name || !email || !specialization) {
      setError("Please enter name, email, and specialization");
      return;
    }
    try {
      const newDoctor = await addDoctor(name, email); // only name & email in DB

      // Add to specialization JSON
      const newSpec = { name, specialization };
      setDoctorSpecs([...doctorSpecs, newSpec]);

      // Add doctor to table with specialization
      setDoctors([...doctors, { ...newDoctor, specialization }]);

      // Clear inputs
      setName("");
      setEmail("");
      setSpecialization("");
      setError("");
    } catch (err) {
      console.error("Add doctor error:", err.response || err);
      setError("Failed to add doctor");
    }
  };

  // Delete doctor
  const handleDelete = async (id) => {
    try {
      await deleteDoctor(id);
      const doctorToRemove = doctors.find(d => d.id === id);
      // Remove from specialization JSON
      setDoctorSpecs(doctorSpecs.filter(ds => ds.name !== doctorToRemove.name));
      // Remove from table
      setDoctors(doctors.filter(d => d.id !== id));
    } catch (err) {
      console.error("Delete doctor error:", err.response || err);
      setError("Failed to delete doctor");
    }
  };

  // Edit doctor
  const handleEdit = (doctor) => {
    setEditingId(doctor.id);
    setEditName(doctor.name);
    setEditEmail(doctor.email);
    setEditSpec(doctor.specialization);
    setError("");
  };

  // Save edited doctor
  const handleSave = async (id) => {
    if (!editName || !editEmail || !editSpec) {
      setError("Name, email, and specialization cannot be empty");
      return;
    }
    try {
      const updatedDoctor = await updateDoctor(id, editName, editEmail);

      // Update specialization JSON
      const updatedSpecs = doctorSpecs.map(ds =>
        ds.name === doctors.find(d => d.id === id).name
          ? { name: editName, specialization: editSpec }
          : ds
      );
      setDoctorSpecs(updatedSpecs);

      // Update table
      setDoctors(doctors.map(d => (d.id === id ? { ...updatedDoctor, specialization: editSpec } : d)));
      setEditingId(null);
      setEditName("");
      setEditEmail("");
      setEditSpec("");
      setError("");
    } catch (err) {
      console.error("Update doctor error:", err.response || err);
      setError("Failed to update doctor");
    }
  };

  // Cancel editing
  const handleCancel = () => {
    setEditingId(null);
    setEditName("");
    setEditEmail("");
    setEditSpec("");
    setError("");
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>Doctors</h2>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <div style={{ marginBottom: "10px" }}>
        <input
          placeholder="Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          style={{ marginRight: "5px" }}
        />
        <input
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={{ marginRight: "5px" }}
        />
        <input
          placeholder="Specialization"
          value={specialization}
          onChange={(e) => setSpecialization(e.target.value)}
          style={{ marginRight: "5px" }}
        />
        <button onClick={handleAdd}>Add Doctor</button>
      </div>

      {loading ? (
        <p>Loading doctors...</p>
      ) : (
        <table border="1" style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th style={{ padding: "5px" }}>Name</th>
              <th style={{ padding: "5px" }}>Email</th>
              <th style={{ padding: "5px" }}>Specialization</th>
              <th style={{ padding: "5px" }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {doctors.map((d) => (
              <tr key={d.id}>
                {editingId === d.id ? (
                  <>
                    <td>
                      <input value={editName} onChange={(e) => setEditName(e.target.value)} />
                    </td>
                    <td>
                      <input value={editEmail} onChange={(e) => setEditEmail(e.target.value)} />
                    </td>
                    <td>
                      <input value={editSpec} onChange={(e) => setEditSpec(e.target.value)} />
                    </td>
                    <td>
                      <button onClick={() => handleSave(d.id)}>Save</button>
                      <button onClick={handleCancel} style={{ marginLeft: "5px" }}>Cancel</button>
                    </td>
                  </>
                ) : (
                  <>
                    <td>{d.name}</td>
                    <td>{d.email}</td>
                    <td>{d.specialization}</td>
                    <td>
                      <button onClick={() => handleEdit(d)}>Edit</button>
                      <button onClick={() => handleDelete(d.id)} style={{ marginLeft: "5px" }}>Delete</button>
                    </td>
                  </>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default Doctors;
 */

import React, { useEffect, useState } from "react";
import { getDoctors, addDoctor, updateDoctor, deleteDoctor } from "../api/admin";
import doctorSpecializationsData from "../data/doctorSpecializations.json"; // JSON storing doctor specializations
import fs from "fs"; // Node fs used in case you are writing JSON from frontend

const Doctors = () => {
  const [doctors, setDoctors] = useState([]);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [specialization, setSpecialization] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const [editingId, setEditingId] = useState(null);
  const [editName, setEditName] = useState("");
  const [editEmail, setEditEmail] = useState("");
  const [editSpecialization, setEditSpecialization] = useState("");

  // Fetch doctors from backend
  const fetchDoctors = async () => {
    try {
      setLoading(true);
      const data = await getDoctors();
      setDoctors(data);
      setLoading(false);
    } catch (err) {
      console.error("Fetch doctors error:", err.response || err);
      setError("Failed to fetch doctors");
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDoctors();
  }, []);

  // Add new doctor
  const handleAdd = async () => {
    if (!name || !email || !specialization) {
      setError("Please enter name, email, and specialization");
      return;
    }

    try {
      const newDoctor = await addDoctor(name, email);

      // Add specialization in frontend JSON
      doctorSpecializationsData.push({ name: newDoctor.name, specialization });
      // Optional: save JSON file if environment allows (Node.js)
      // fs.writeFileSync("src/data/doctorSpecializations.json", JSON.stringify(doctorSpecializationsData, null, 2));

      setDoctors([...doctors, newDoctor]);
      setName("");
      setEmail("");
      setSpecialization("");
      setError("");
    } catch (err) {
      console.error("Add doctor error:", err.response || err);
      setError("Failed to add doctor");
    }
  };

  // Delete doctor
  const handleDelete = async (id) => {
    try {
      await deleteDoctor(id);
      setDoctors(doctors.filter(d => d.id !== id));

      // Remove from specialization JSON
      const doctor = doctors.find(d => d.id === id);
      const index = doctorSpecializationsData.findIndex(ds => ds.name === doctor.name);
      if (index !== -1) doctorSpecializationsData.splice(index, 1);

    } catch (err) {
      console.error("Delete doctor error:", err.response || err);
      setError("Failed to delete doctor");
    }
  };

  // Edit doctor
  const handleEdit = (doctor) => {
    setEditingId(doctor.id);
    setEditName(doctor.name);
    setEditEmail(doctor.email);

    const specObj = doctorSpecializationsData.find(ds => ds.name === doctor.name);
    setEditSpecialization(specObj ? specObj.specialization : "");
    setError("");
  };

  // Save edited doctor
  const handleSave = async (id) => {
    if (!editName || !editEmail || !editSpecialization) {
      setError("Name, email, and specialization cannot be empty");
      return;
    }
    try {
      const updatedDoctor = await updateDoctor(id, editName, editEmail);

      // Update specialization JSON
      const specIndex = doctorSpecializationsData.findIndex(ds => ds.name === updatedDoctor.name);
      if (specIndex !== -1) {
        doctorSpecializationsData[specIndex].specialization = editSpecialization;
      } else {
        doctorSpecializationsData.push({ name: updatedDoctor.name, specialization: editSpecialization });
      }

      setDoctors(doctors.map(d => (d.id === id ? updatedDoctor : d)));
      setEditingId(null);
      setEditName("");
      setEditEmail("");
      setEditSpecialization("");
      setError("");
    } catch (err) {
      console.error("Update doctor error:", err.response || err);
      setError("Failed to update doctor");
    }
  };

  // Cancel editing
  const handleCancel = () => {
    setEditingId(null);
    setEditName("");
    setEditEmail("");
    setEditSpecialization("");
    setError("");
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>Doctors</h2>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <div style={{ marginBottom: "10px" }}>
        <input
          placeholder="Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          style={{ marginRight: "5px" }}
        />
        <input
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={{ marginRight: "5px" }}
        />
        <input
          placeholder="Specialization"
          value={specialization}
          onChange={(e) => setSpecialization(e.target.value)}
          style={{ marginRight: "5px" }}
        />
        <button onClick={handleAdd}>Add Doctor</button>
      </div>

      {loading ? (
        <p>Loading doctors...</p>
      ) : (
        <table border="1" style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th style={{ padding: "5px" }}>Name</th>
              <th style={{ padding: "5px" }}>Email</th>
              <th style={{ padding: "5px" }}>Specialization</th>
              <th style={{ padding: "5px" }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {doctors.map((d) => {
              const specObj = doctorSpecializationsData.find(ds => ds.name === d.name);
              const spec = specObj ? specObj.specialization : "";
              return (
                <tr key={d.id}>
                  {editingId === d.id ? (
                    <>
                      <td>
                        <input
                          value={editName}
                          onChange={(e) => setEditName(e.target.value)}
                        />
                      </td>
                      <td>
                        <input
                          value={editEmail}
                          onChange={(e) => setEditEmail(e.target.value)}
                        />
                      </td>
                      <td>
                        <input
                          value={editSpecialization}
                          onChange={(e) => setEditSpecialization(e.target.value)}
                        />
                      </td>
                      <td>
                        <button onClick={() => handleSave(d.id)}>Save</button>
                        <button onClick={handleCancel} style={{ marginLeft: "5px" }}>Cancel</button>
                      </td>
                    </>
                  ) : (
                    <>
                      <td>{d.name}</td>
                      <td>{d.email}</td>
                      <td>{spec}</td>
                      <td>
                        <button onClick={() => handleEdit(d)}>Edit</button>
                        <button onClick={() => handleDelete(d.id)} style={{ marginLeft: "5px" }}>Delete</button>
                      </td>
                    </>
                  )}
                </tr>
              )
            })}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default Doctors;
