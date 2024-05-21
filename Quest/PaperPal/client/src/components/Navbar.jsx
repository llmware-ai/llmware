import React from "react";
import { Link } from "react-router-dom";
import Logo from "../assets/logo.png";

const Navbar = () => {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-around",
        backgroundImage: "linear-gradient(to right, #434343 0%, black 100%)",
        padding: "1rem",
        borderRadius: "0.5rem",
        fontSize: "1.5rem"
      }}
    >
      <Link to="/" style={{ color: "whitesmoke", textDecoration: "none", fontStyle: "italic" }}>
        <div>
          <span
            style={{
              marginRight: "0.5rem",
              backgroundColor: "purple",
                          padding: "0.2rem 0.5rem",
              borderRadius: "50%"
            }}
          >
            PP
          </span>
          PaperPal
        </div>
      </Link>
      <div style={{ display: "flex", gap: "2rem" }}>
        <Link to="/" style={{ color: "whitesmoke", textDecoration: "none" }}>
          <div>Home</div>
        </Link>
        <Link
          to="/summarize"
          style={{ color: "whitesmoke", textDecoration: "none" }}
        >
          <div>Summarize</div>
        </Link>
      </div>
      <Link
        to="/summarize"
        style={{ color: "whitesmoke", textDecoration: "none" }}
      >
        <div
          style={{
            backgroundColor: "purple",
            padding: "0.25rem",
            borderRadius: "0.25rem",
          }}
        >
          Get Started
        </div>
      </Link>
    </div>
  );
};

export default Navbar;
