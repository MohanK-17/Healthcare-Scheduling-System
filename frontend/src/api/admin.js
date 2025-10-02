
import axios from "axios";

const API_BASE = "http://127.0.0.1:8000/admin/admin";

// Default admin credentials (for now)
const AUTH = {
  username: "danielle.johnsonA01",
  password: "Admin#01Pass",
};

// --------------------
// Admin Login
// --------------------
export const loginAdmin = async (username, password) => {
  const res = await axios.post(`${API_BASE}/login`, { username, password });
  return res.data;
};

// --------------------
// Appointments
// --------------------
export const getAppointments = async () => {
  const res = await axios.get(`${API_BASE}/appointments`, { auth: AUTH });
  return res.data.appointments;
};

export const addAppointment = async (appointmentData) => {
  const res = await axios.post(`${API_BASE}/appointments`, null, {
    params: appointmentData,
    auth: AUTH,
  });
  return res.data.appointment;
};

export const deleteAppointment = async (id) => {
  const res = await axios.delete(`${API_BASE}/appointments/${id}`, { auth: AUTH });
  return res.data;
};

// --------------------
// Doctors CRUD
// --------------------
export const getDoctors = async () => {
  const res = await axios.get(`${API_BASE}/doctors`, { auth: AUTH });
  return res.data;
};

export const addDoctor = async (name, email, password, specialization) => {
  const res = await axios.post(
    `${API_BASE}/doctors`,
    null,
    {
      params: { name, email, password, specialization },
      auth: AUTH,
    }
  );
  return res.data;
};

export const updateDoctor = async (id, name, email, specialization) => {
  const res = await axios.put(
    `${API_BASE}/doctors/${id}`,
    null,
    {
      params: { name, email, specialization },
      auth: AUTH,
    }
  );
  return res.data;
};

export const deleteDoctor = async (id) => {
  const res = await axios.delete(`${API_BASE}/doctors/${id}`, { auth: AUTH });
  return res.data;
};
 
