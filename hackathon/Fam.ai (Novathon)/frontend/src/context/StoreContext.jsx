import React, { createContext, useContext, useState } from "react";

// creating context
const StoreContext = createContext();

export const StoreProvider = ({ children }) => {
  const [wallet, setWallet] = useState(localStorage.getItem("wallet") || null);
  const value = {
    wallet,
    setWallet,
  };

  return (
    <StoreContext.Provider value={value}>{children}</StoreContext.Provider>
  );
};

export const useStore = () => {
  return useContext(StoreContext);
};