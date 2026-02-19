from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import JSONResponse
import os
from groq import Groq  # Importing the Groq client
from dotenv import load_dotenv
import json
import ast
load_dotenv()


# Initialize the FastAPI router
router = APIRouter()

# Initialize the Groq client
client = Groq(
    api_key = os.getenv("groq_api")
)

@router.post("/generate-questions")
async def generate_questions(
    job_role: str = Form(...),
    experience: str = Form(...)
):
    """
    API endpoint to generate interview questions with options based on job role and experience.

    Parameters:
        job_role (str): The job role for which questions are to be generated.
        experience (str): The candidate's experience level (e.g., entry-level, mid-level, senior).

    Returns:
        list: List of JSON objects containing questions and their options.
    """
    try:
        example_json = [
    {
        "question": "How would you concatenate two strings in Python?",
        "answers": [
            "You would use the '+' operator to concatenate the two strings.",
            "You would use the '=' operator to assign the second string to the first string.",
            "You would use a loop to iterate over the characters of the second string and add them to the first string.",
            "You would use a function to concatenate the two strings."
        ]
    },
    {
        "question": "What is the purpose of the strip() method in Python?",
        "answers": [
            "To remove the first and last characters of a string.",
            "To remove the first character of a string.",
            "To remove the last character of a string.",
            "To remove leading and trailing whitespace from a string."
        ]
    },

]
        # Send the request to Groq LLM to generate questions with options
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert in creating interview questions. Generate a set of questions for a given job role and experience level. "
                        "For each question, provide four options as possible answers."
                        "for each question and answer  remember to put double quotes before and after each option and question"
                    )
                },
                {
                    "role": "user",
                    "content": (f"""
                        Create 5 interview questions for the job role: '{job_role}' targeting candidates with '{experience}' experience. 
                        Remember to put double quotes before and after each option and question. Each question should have 4 options. Return the result as a JSON list in the format: {json.dumps(example_json)}  no other text along with it"""

                    )
                }
            ],
            model="llama3-8b-8192",
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stop=None,
            stream=False,
        )

        # Extract the response
        questions_with_options = chat_completion.choices[0].message.content
        data = questions_with_options.replace('\n', '').replace('\"', '').replace("  ","")
        print(data)
        # Return the questions and options as a JSON response
        return JSONResponse(
            content={"questions": data},
            status_code=200,
        )

    except Exception as e:
        # Handle errors during question generation
        raise HTTPException(status_code=500, detail=f"Error generating questions: {str(e)}")