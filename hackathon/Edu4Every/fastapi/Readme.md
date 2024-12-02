# AI Educational and Career Support Platform

## Overview

This comprehensive platform provides a suite of AI-powered tools designed to support students, teachers, and job seekers through various stages of their educational and professional journey.

## Features

### 1. Assignment Correction AI
- Automatically grade student assignments
- Uses OCR to extract text from PDF submissions
- Compares student answers with teacher's reference answer
- Provides a grade out of 100

### 2. Job Recommendation System
- Analyzes user questionnaire responses
- Recommends personalized job roles
- Integrates with Google Jobs API to fetch relevant job listings

### 3. Resume Processing
- Generates professional 2-page resumes
- Utilizes job market keywords
- Customized based on user's education, skills, and experience

### 4. Additional Tools
- AI Writing Assistant
- AI Note Maker
- AI Call Assistant
- AI Learning Course Generator
- AI Mock Test Generator
- AI Career Roadmap Creator

## Technologies Used

### Backend
- FastAPI
- Python

### AI and Machine Learning
- LLMWare
- Groq AI
- Ollama
- Mistral AI Model

### APIs
- SerpAPI (for job searches)
- Bolna API (for call initiation)

## Setup and Installation

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Installation Steps
1. Clone the repository
```bash
git clone <repository-url>
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
Create a `.env` file with the following:
```
groq_api=your_groq_api_key
serpapi_api=your_serpapi_key
bolna_api=your_bolna_api_key
agent_id=your_agent_id
```

5. Run the application
```bash
uvicorn main:app --reload
```

## API Endpoints

### Assignment Correction
- `POST /correct-ai-assiagment/upload-and-process-pdf`
  - Uploads PDF and processes assignment

### Job Recommendation
- `POST /job_recommendation/recommend-jobs`
  - Generates job recommendations based on user profile

### Resume Processing
- `POST /process_carrier_guidance/process-guidance`
  - Generates personalized resume

## Security
- CORS configured
- API key protection
- Secure file handling

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Contact
Your Name - your.email@example.com

Project Link: [https://github.com/yourusername/your-project-name]