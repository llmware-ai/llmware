import os
from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import JSONResponse
from groq import Groq  # Importing the Groq client
from dotenv import load_dotenv

load_dotenv()
# Initialize the FastAPI router
router = APIRouter()

# Initialize the Groq client
client = Groq(
    api_key = os.getenv("groq_api")
)

@router.post("/generate-course")
async def generate_course(
    skill: str = Form(...),
    level: str = Form(...)
):
    """
    API endpoint to generate a course based on the provided skill and level.

    Parameters:
        skill (str): The skill the user wants to learn.
        level (str): The user's current level (e.g., beginner, intermediate, advanced).

    Returns:
        dict: Generated course content for the user.
    """
    try:
        # Send the request to Groq LLM for generating the course
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert course creator. Your role is to design courses for any skill based on the level provided."
                },
                {
                    "role": "user",
                    "content": (
                        f"Create a detailed course outline for the skill: '{skill}' tailored for a '{level}' level learner. "
                        "Include topics, subtopics, and key learning objectives."
                    ),
                }
            ],
            model="llama3-8b-8192",
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stop=None,
            stream=False,
        )

        # Extract the response
        course_content = chat_completion.choices[0].message.content

        # Return the generated course content
        return JSONResponse(
            content={
                "skill": skill,
                "level": level,
                "course": course_content
            },
            status_code=200,
        )

    except Exception as e:
        # Handle errors during course generation
        raise HTTPException(status_code=500, detail=f"Error generating course: {str(e)}")
