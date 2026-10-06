import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './components/LandingPage/LandingPage';
import StudentLogin from './components/Student/StudentLogin';
import TeacherLogin from './components/Teacher/TeacherLogin';
import StudentDashboard from './components/Student/StudentDashboard';
import TeacherDashboard from './components/Teacher/TeacherDashboard';
import CareerGuidancePage from './components/CareerGuidance/CareerGuidancePage';
import CareerGuidanceDashboard from './components/CareerGuidance/CareerGuidanceDashboard';
import CareerGuidanceLogin from './components/CareerGuidance/CareerGuidanceLogin'; // Added this import
import CallFeaturePage from './components/Student/CallFeaturePage';
import ResumeBuilderPage from './components/Student/ResumeBuilderPage';
import CustomerService from './components/chat/CustomerService';
import WritingAssistant from './components/Student/WritingAssistant';
import JobRecommendations from './components/CareerGuidance/JobRecommendations';
import VoiceRecordingComponent from './components/Teacher/VoiceRecordingComponent';
import CallAIPage from './components/CareerGuidance/CallAIPage';
import AssignmentGrading from './components/Teacher/AssignmentGrading'
import PdfFinder from './components/Student/PdfFinder';
import AIMocktest from './components/CareerGuidance/AIMocktest';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-background">
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          
          {/* Authentication Routes */}
          <Route path="/auth/student" element={<StudentLogin />} />
          <Route path="/auth/teacher" element={<TeacherLogin />} />
          <Route path="/auth/career-guidance" element={<CareerGuidanceLogin />} />
          
          {/* Dashboard Routes */}
          <Route path="/dashboard/student" element={<StudentDashboard />} />
          <Route path="/dashboard/teacher" element={<TeacherDashboard />} />
          <Route path="/dashboard/career-guidance" element={<CareerGuidancePage />} />
          <Route path="/dashboard/service-dashboard" element={<CustomerService />} />
          <Route path="/dashboard/career-guidance-dashboard" element={<CareerGuidanceDashboard />} />
          
          {/* Feature Routes */}
          <Route path="/call-feature" element={<CallFeaturePage />} />
          <Route path="/resume-builder" element={<ResumeBuilderPage />} />
          <Route path="/writing-assistant" element={<WritingAssistant />} />
          <Route path="/job-search" element={<JobRecommendations />} />
          <Route path="/voice-recording" element={<VoiceRecordingComponent />} />
          <Route path="/ai-phonecall-career" element={<CallAIPage />} />
          <Route path="/assignment" element={<AssignmentGrading/>} />
          <Route path="/pdf-qa" element={<PdfFinder />} />
          <Route path="/mock-test" element={<AIMocktest />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
