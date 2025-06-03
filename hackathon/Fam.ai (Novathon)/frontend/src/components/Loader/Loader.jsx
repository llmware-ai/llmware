import React from "react";
import { MutatingDots } from "react-loader-spinner";
import './Loader.scss'
const Loader = () => {
  return (
    <div className="loader">
      <MutatingDots
        visible={true}
        height="100"
        width="100"
        color="#000"
        secondaryColor="#000"
        radius="12.5"
        ariaLabel="mutating-dots-loading"
        wrapperStyle={{}}
        wrapperClass=""
      />
    </div>
  );
};

export default Loader;
