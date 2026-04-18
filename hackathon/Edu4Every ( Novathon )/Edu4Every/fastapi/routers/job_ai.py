from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import json
from dotenv import load_dotenv
from groq import Groq
import serpapi

# Load environment variables
load_dotenv()

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("groq_api"))

# Define input model for receiving questions and answers
class QuestionAnswerDict(BaseModel):
    questions: dict

# Initialize SerpAPI client
def search_jobs(recommended_job: str):
    search_params = {
        "engine": "google_jobs",
        "q": recommended_job,
        "hl": "en",
        "api_key": os.getenv("serpapi_api"),
    }

    search = serpapi.search(search_params)
    search_results = search.get("jobs_results", [])

    jobs = []
    for result in search_results:
        job = {
            "title": result.get("company_name"),
            "link": result.get("share_link"),
        }
        jobs.append(job)
    return jobs

# Initialize FastAPI router
job_recommendation_router = APIRouter()

@job_recommendation_router.post("/recommend-jobs")
async def recommend_jobs(data: QuestionAnswerDict):
    try:
        # Generate chat completion for job recommendation
        question = data.questions
        example = "python developer"
        chat_response = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"After reviewing all questions and answers {question}, "
                        f"recommend one job role to apply for. Only respond with the answer in the format. {example}"
                        " Do not include any additional text."
                    ),
                }
            ],
            model="llama3-8b-8192",  # Specify the model
        )

        # Extract the recommended job title from the chat response
        recommended_job = chat_response.choices[0].message.content.strip()

        # Use SerpAPI to search for jobs related to the recommended job
        jobs = search_jobs(recommended_job)

        return {"status": "success", "recommended_jobs": jobs}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
