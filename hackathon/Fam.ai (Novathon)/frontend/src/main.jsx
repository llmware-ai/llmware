import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import FamilyProfile from "./pages/Profiles/FamilyProfile.jsx";
import ProfilePage from "./pages/ProfilePage/ProfilePage.jsx";
import { StoreProvider } from "./context/StoreContext.jsx";
import Nav from "./components/Nav/Nav.jsx";

import { Toaster } from "react-hot-toast";

createRoot(document.getElementById("root")).render(
  <StoreProvider>
    <BrowserRouter>
      <Toaster />
      <Nav />
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/fam" element={<FamilyProfile />} />
        <Route path="/fam/:uid" element={<ProfilePage />} />
      </Routes>
    </BrowserRouter>
  </StoreProvider>
);
