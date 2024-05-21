import React from "react";
import ClipLoader from "react-spinners/ClipLoader";

const Loading = ({ size, style }) => {
  return (
    <div style={{ width: "fit-content", margin: style }}>
      <ClipLoader color="blue" size={size} />
    </div>
  );
};

export default Loading;
