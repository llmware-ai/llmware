import React, { useState } from "react";
import { MdUploadFile } from "react-icons/md";
import { LuPaperclip } from "react-icons/lu";
import pdfToText from "react-pdftotext";
import Result from "./Result";
import { useSummarizeMutation } from "../slices/summarizeApiSlice";
import Loading from "./Loading";

const Summarize = () => {
  const [pdfText, setPdfText] = useState("");
  const [pageDisplay, setPageDisplay] = useState(true);
  const [apiResponse, setApiResponse] = useState({});

  const [summarize, { isLoading }] = useSummarizeMutation();

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    pdfToText(file)
      .then((text) => setPdfText(text))
      .catch((error) =>
        console.error("Failed to extract text from pdf:", error)
      );
  };

  const handleSummarization = async () => {
    const res = await summarize(pdfText).unwrap();
    console.log(res); // the response i.e summary points, passed as props to result.jsx
    setApiResponse(res);
    setPageDisplay(false);
  };

  return (
    <div>
      <div
        style={{
          color: "#1f1d1d",
          marginTop: "2rem",
          textAlign: "center",
          display: pageDisplay ? "block" : "none",
        }}
      >
        <LuPaperclip size={100} />
        <div style={{ marginBottom: "2rem", marginTop: "1rem" }}>
          <h2>Get Instant Research Summaries</h2>
          <p>
            Get concise and accurate summaries of complex research papers in
            seconds, making academic content more accessible and easier to
            understand.
          </p>
        </div>
        <div>
          <h2>Upload Research Paper</h2>
          <p>Currently accepting .pdf format</p>
          <label className="upload-button">
            <MdUploadFile size={30} />
            <input type="file" accept=".pdf" onChange={handleFileChange} />
          </label>
        </div>
        <div
          onClick={handleSummarization}
          style={{
            backgroundColor: "purple",
            width: "10rem",
            color: "whitesmoke",
            padding: "0.6rem",
            borderRadius: "0.3rem",
            margin: "2rem auto",
            cursor: "pointer",
            textAlign: "center",
          }}
        >
          Start Summarization
        </div>
      </div>
      <div>
        {isLoading && <Loading size={50} style={"auto"} />}
        {!pageDisplay && <Result res={apiResponse} />}
      </div>
    </div>
  );
};

export default Summarize;
