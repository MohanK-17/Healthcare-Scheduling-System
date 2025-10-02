/* import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Doctors from "./pages/Doctors";
import Appointments from "./pages/Appointments";

function App() {
  const [admin, setAdmin] = useState(null);

  const handleLoginSuccess = (adminUser) => {
    setAdmin(adminUser);
  };

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={admin ? <Navigate to="/dashboard" /> : <Login onLoginSuccess={handleLoginSuccess} />}
        />
        {admin && (
          <>
            <Route path="/dashboard" element={<Dashboard admin={admin} />} />
            <Route path="/doctors" element={<Doctors />} />
            <Route path="/appointments" element={<Appointments />} />
          </>
        )}
      </Routes>
    </Router>
  );
}

export default App;
 */

import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Appointments from "./pages/Appointments";
import Doctors from "./pages/Doctors";
import Dashboard from "./pages/Dashboard";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/appointments" element={<Appointments />} />
        <Route path="/doctors" element={<Doctors />} />
      </Routes>
    </Router>
  );
}

export default App;
