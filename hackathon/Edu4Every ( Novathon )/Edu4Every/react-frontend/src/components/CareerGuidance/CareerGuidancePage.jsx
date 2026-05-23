import React, { useState } from "react";
import axios from "axios";
import { CompassIcon, SearchIcon, CheckCircleIcon } from "lucide-react";

const CareerGuidancePage = () => {
  const [formData, setFormData] = useState({
    currentEducation: "degree",
    interestedFields: "",
    skills: "",
    careerGoals: "",
  });
  const [careerRecommendations, setCareerRecommendations] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const response = await axios.post(
        "https://5940-111-92-80-102.ngrok-free.app/ai-roadmap/career-roadmap",
        {
          currentEducation: formData.currentEducation,
          interestedFields: formData.interestedFields,
          skills: formData.skills,
          careerGoals: formData.careerGoals,
        }
      );

      if (response?.data) {
        setCareerRecommendations(response.data.roadmap);
      } else {
        console.error("Invalid response:", response.data.message || "Unknown error");
      }
    } catch (error) {
      console.error("Career guidance error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 flex flex-col items-center">
      <div className="bg-white shadow-xl rounded-xl p-6 w-full max-w-4xl">
        <div className="flex items-center mb-6">
          <CompassIcon className="w-10 h-10 text-blue-500 mr-4" />
          <h1 className="text-3xl font-bold text-gray-800">Career RoadMap</h1>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-gray-700 font-medium mb-2">
              Current Education Level
            </label>
            <select
              name="currentEducation"
              value={formData.currentEducation}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="high_school">High School</option>
              <option value="diploma">Diploma</option>
              <option value="undergraduate">Undergraduate</option>
              <option value="degree">Degree</option>
              <option value="graduate">PostGraduate</option>
            </select>
          </div>
          <div>
            <label className="block text-gray-700 font-medium mb-2">
              Interested Career Fields
            </label>
            <input
              type="text"
              name="interestedFields"
              value={formData.interestedFields}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., AI, Healthcare, Engineering"
            />
          </div>
          <div>
            <label className="block text-gray-700 font-medium mb-2">Your Skills</label>
            <textarea
              name="skills"
              value={formData.skills}
              onChange={handleInputChange}
              rows={4}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="List your current skills and strengths"
            ></textarea>
          </div>
          <div>
            <label className="block text-gray-700 font-medium mb-2">Career Goals</label>
            <textarea
              name="careerGoals"
              value={formData.careerGoals}
              onChange={handleInputChange}
              rows={4}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Describe your short-term and long-term career objectives"
            ></textarea>
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-500 text-white py-3 rounded-lg hover:bg-blue-600 transition-colors font-semibold flex items-center justify-center"
          >
            {isLoading ? (
              <div className="animate-spin mr-2">
                <SearchIcon className="w-5 h-5" />
              </div>
            ) : (
              "Get Career Recommendations"
            )}
          </button>
        </form>
      </div>

      {careerRecommendations && (
        <div className="bg-white shadow-xl rounded-xl p-6 mt-8 w-full max-w-4xl">
          <div className="flex items-center mb-6">
            <CheckCircleIcon className="w-10 h-10 text-green-500 mr-4" />
            <h2 className="text-2xl font-bold text-gray-800">Career Recommendations</h2>
          </div>
          <div className="space-y-4 bg-gray-50 p-4 rounded-lg">
            {careerRecommendations.split("\n").map((recommendation, index) => (
              <div
                key={index}
                className="flex items-start border-b pb-3 last:border-b-0"
              >
                <CheckCircleIcon className="w-5 h-5 text-green-500 mr-3 mt-1 flex-shrink-0" />
                <p className="text-gray-700">{recommendation}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default CareerGuidancePage;
