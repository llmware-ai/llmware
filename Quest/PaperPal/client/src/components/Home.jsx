import React from "react";
import Logo from "../assets/logo.png";
import Box from "./Box";
import { Link } from "react-router-dom";

const Home = () => {
  return (
    <div>
      <div>
        <img
          src={Logo}
          style={{
            height: "25rem",
            width: "25rem",
            display: "block",
            margin: "auto",
            marginLeft: "49rem"
          }}
        ></img>
      </div>
      <Link
        to="/summarize"
        style={{ color: "whitesmoke", textDecoration: "none" }}
      >
        <div
          style={{
            backgroundColor: "purple",
            padding: "0.45rem",
            borderRadius: "0.25rem",
            width: "8rem",
            margin: "auto",
            marginBottom: "3rem",
            marginTop: "-2rem",
            textAlign: "center",
          }}
        >
          Get Started
        </div>
      </Link>
      <div style={{ display: "flex", gap: "1rem" }}>
        <Box
          title="Instant Research Summaries"
          text="Get concise and accurate summaries of complex research papers in seconds, making academic content more accessible and easier to understand."
        />
        <Box
          title="Intelligent Q&A"
          text="Ask any question related to the research paper and receive precise, contextually relevant answers to enhance your comprehension and research efficiency."
        />
        <Box
          title="User-Friendly Interface"
          text="Enjoy a seamless and intuitive experience designed for researchers, students, and professionals, ensuring efficient navigation and utilization of research content."
        />
      </div>
    </div>
  );
};

export default Home;
