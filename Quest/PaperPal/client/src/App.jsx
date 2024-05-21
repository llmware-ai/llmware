import React from "react";
import Navbar from "./components/Navbar";
import { Outlet } from "react-router-dom";
import Footer from "./components/Footer";
const App = () => {
  return (
    <div className="app-main-div">
      <Navbar />
      <Outlet />
      <Footer />
    </div>
  );
};

export default App;
