import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LandingPage from "../pages/LandingPage";

import AuthorPage from "@/pages/AuthorPage";
import UploadFiles from "@/pages/UploadFiles";
import ChatPage from "@/pages/ChatPage/ChatPage";

const AppRoutes = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/author" element={<AuthorPage />} />
        <Route path="/upload-files" element={<UploadFiles />} />
        <Route path="/chat" element={<ChatPage />} />
      </Routes>
    </Router>
  );
};

export default AppRoutes;
