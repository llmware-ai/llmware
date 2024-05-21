import React, { useState } from "react";
import { CiCircleQuestion } from "react-icons/ci";
import { useQnaMutation } from "../slices/summarizeApiSlice";
import Loading from "./Loading";

const Result = ({ res }) => {
  const [chat, setChat] = useState(false);
  const [question, setQuestion] = useState("");
  const [qaPairs, setQaPairs] = useState([]);

  const [qna, { isLoading }] = useQnaMutation();

  const handleQuestionSubmit = async () => {
    if (question.trim() === "") return;

    try {
      console.log("Submitting question:", question); 

      const res = await qna({ question }).unwrap();

      console.log("Raw backend response:", res); 

      const jsonString = res.join("");

      console.log("Joined JSON string:", jsonString);

      const parsedRes = JSON.parse(jsonString);

      console.log("Parsed response:", parsedRes); 

      const formattedQuestion = parsedRes.question.replace(" (explain)", "");

      setQaPairs([
        ...qaPairs,
        { question: formattedQuestion, answer: parsedRes },
      ]);
      setQuestion("");
    } catch (error) {
      console.error("Failed to fetch the answer:", error);
    }
  };

  return (
    <div>
      <div
        style={{
          outline: "1px solid black",
          marginTop: "1rem",
          borderRadius: "0.5rem",
          padding: "1rem",
          background:
            "linear-gradient(to bottom,rgba(255, 255, 255, 0.2) 0%,rgba(0, 0, 0, 0.15) 100%)",
        }}
      >
        <h2>Summary of the Paper in Important Points</h2>
        <ul>
          {res["Research Paper"].map((point, index) => (
            <li key={index}>{point}</li>
          ))}
        </ul>
      </div>
      {!chat ? (
        <div style={{ marginTop: "1rem" }}>
          Have any questions regarding the paper?{" "}
          <span
            style={{ fontWeight: 900, cursor: "pointer", color: "blue" }}
            onClick={() => {
              setChat(true);
            }}
          >
            Ask now!
          </span>
        </div>
      ) : (
        <div
          style={{
            outline: "1px solid black",
            marginTop: "1rem",
            borderRadius: "0.5rem",
            padding: "1rem",
            background:
              "linear-gradient(to bottom,rgba(255, 255, 255, 0.2) 0%,rgba(0, 0, 0, 0.15) 100%)",
            position: "relative",
            height: "20rem",
          }}
        >
          <div style={{ maxHeight: "18rem", overflow: "scroll" }}>
            {qaPairs.length === 0 ? (
              <div
                style={{
                  textAlign: "center",
                  marginTop: "5rem",
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                  flexDirection: "column",
                  gap: 5,
                }}
              >
                <CiCircleQuestion size={30} />
                Ask Your First Question
              </div>
            ) : (
              <div
                style={{
                  border: "0.2px solid black",
                  padding: "0.25rem",
                  borderRadius: "0.25rem",
                }}
              >
                {isLoading ? (
                  <Loading size={15} style={"0.25rem"} />
                ) : (
                  qaPairs.map((qa, index) => (
                    <div key={index} style={{ marginBottom: "1rem" }}>
                      <p style={{ fontWeight: "bold" }}>Q: {qa.question}</p>
                      <p>
                        A: {qa.answer.answer}, {qa.answer.explanation}
                      </p>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
          <div
            style={{
              position: "absolute",
              bottom: 5,
              left: 100,
              display: "flex",
              width: "80%",
              margin: "auto",
              gap: 4,
            }}
          >
            <input
              className="chat-ip"
              style={{
                width: "90%",
                backgroundColor: "grey",
                border: "1px solid black",
                borderRadius: "0.25rem",
                padding: "0.5rem 1rem",
              }}
              value={question}
              placeholder="Ask questions regarding research paper..."
              onChange={(e) => {
                setQuestion(e.target.value);
              }}
            />
            <button
              style={{
                width: "8%",
                backgroundColor: "grey",
                border: "1px solid black",
                borderRadius: "0.25rem",
                cursor: "pointer",
              }}
              onClick={handleQuestionSubmit}
            >
              Ask
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Result;
