from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import os
from pydantic import BaseModel
from groq import Groq  # Importing the Groq client
from dotenv import load_dotenv
import requests
load_dotenv()


# Initialize the FastAPI router
router = APIRouter()

# Define the request model
class CareerGuidanceInput(BaseModel):
    currentEducation: str
    interestedFields: str
    skills: str
    careerGoals: str

# Initialize the Groq client
client = Groq(
    api_key = os.getenv("groq_api")
)




# Define input schema
class CallRequest(BaseModel):
    number: str  # Recipient phone number


@router.post("/initiate-call")
async def initiate_call(request: CallRequest):
    """API to initiate a call via the Bolna API"""
    try:
        # Define API URL and payload
        url = "https://api.bolna.dev/call"
        payload = {
            "agent_id": os.getenv("agent_id_carrer"),
            "recipient_phone_number": request.number,

        }
        headers = {
            "Authorization": f"Bearer {os.getenv('bolna_api')}",
            "Content-Type": "application/json",
        }

        # Make the API call
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return {"message": "Call initiated successfully. It will be initiated soon."}
        elif response.status_code == 403:  # Assuming 403 indicates no tokens left
            return {"message": "No tokens left to initiate the call."}
        else:
            # Handle unexpected status codes
            return {"message": "Failed to initiate the call. Please try again later.", "details": response.text}

    except Exception as e:
        # Handle any exceptions that occur during the process
        raise HTTPException(status_code=500, detail=f"Error initiating call: {str(e)}")
@router.post("/career-roadmap")
async def generate_career_roadmap(input_data: CareerGuidanceInput):
    """
    API endpoint to generate a career guidance roadmap for students.

    Parameters:
        input_data (CareerGuidanceInput): A model containing the student's details.

    Returns:
        JSONResponse: A structured roadmap for the student's chosen field.
    """
    try:
        # Extract fields from the input model
        currentEducation = input_data.currentEducation
        interestedFields = input_data.interestedFields
        skills = input_data.skills
        careerGoals = input_data.careerGoals

        # Use Groq's chat completion feature to generate the roadmap
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert career advisor."},
                {
                    "role": "user",
                    "content": (
                        f"Provide a detailed career roadmap for a student with the following details:\n"
                        f"Current Education: {currentEducation}\n"
                        f"Interested Fields: {interestedFields}\n"
                        f"Skills: {skills}\n"
                        f"Career Goals: {careerGoals}\n"
                        f"Generate the roadmap as a step-by-step plan."
                    ),
                },
            ],
            model="llama3-8b-8192",
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            stop=None,
            stream=False,
        )

        # Extract the response content
        roadmap = chat_completion.choices[0].message.content

        # Return the generated roadmap as JSON
        return JSONResponse(
            content={"roadmap": roadmap.replace("\n", "").replace("\t", "")},
            status_code=200,
        )

    except Exception as e:
        # Handle errors and exceptions
        raise HTTPException(status_code=500, detail=f"Failed to generate career roadmap: {str(e)}")