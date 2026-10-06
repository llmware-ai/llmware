from fastapi import APIRouter, HTTPException
import os
from pydantic import BaseModel
from llmware.models import ModelCatalog
import serpapi
from dotenv import load_dotenv


load_dotenv()


# Register the Ollama model
ModelCatalog().register_ollama_model(model_name="mistral")

# Load the registered Ollama model
mistral_model = ModelCatalog().load_model("mistral")

# Define Pydantic model for input validation
class CarrierGuidanceInput(BaseModel):
    name: str
    email: str
    phone: str
    education: str
    degree: str
    skills: str
    experience: str
    projects: str
    job_title: str

# Initialize router
process_resume = APIRouter()

@process_resume.post("/process-guidance")
async def process_carrier_guidance(input_data: CarrierGuidanceInput):
    """
    Process carrier guidance details and interact with Ollama's Mistral model.
    """
    try:

        # Construct prompt for the model
        params = {
            "engine": "google",
            "q": f"import job keyword  for resume for job title {input_data.job_title}",
            "api_key": os.getenv("serpapi_api"),
        }

        search = serpapi.search(params)
        results = search
        print(results['organic_results'])


        prompt = (f"""
            Analyze the following career guidance details:\n\n
            Name: {input_data.name}\n
            Email: {input_data.email}\n
            Phone: {input_data.phone}\n
            Education: {input_data.education}\n
            Degree: {input_data.degree}\n
            Skills: {input_data.skills}\n
            Experience: {input_data.experience}\n
            Projects: {input_data.projects}\n\n
            Job Title: {input_data.job_title}\n
            
            Provide the 2 page Resume for the above details. you can refer the following job keywords for building resume: {results['organic_results'][0]["title"]} , {results['organic_results'][1]["title"]} , {results['organic_results'][2]["title"]}"""
        )

        # Call the Mistral model for inference
        response = mistral_model.inference(prompt)

        # Return the model's response
        return {"status": "success", "message": "Analysis completed successfully", "advice": response["llm_response"]}

    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")