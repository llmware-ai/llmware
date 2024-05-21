import React from "react";

const Box = ({ title, text }) => {
  return (
    <div
      style={{
        backgroundImage: "linear-gradient(45deg, #8baaaa 0%, #ae8b9c 100%)",
        padding: "0.5rem",
        borderRadius: "0.5rem",
        boxShadow: "5px 5px grey",
      }}
    >
      <div style={{ fontWeight: 900 }}>{title}</div>
      <div>{text}</div>
    </div>
  );
};

export default Box;
