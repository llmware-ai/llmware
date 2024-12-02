import os
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
import serpapi

# Load environment variables
load_dotenv()

# Initialize FastAPI router
router = APIRouter()


# Define the image search function
def search_images(query: str):
    try:
        # Setup parameters for SerpAPI request
        params = {
            "engine": "google_images",
            "q": query,
            "location": "Austin, TX, Texas, United States",
            "api_key": os.getenv("serpapi_api"),  # Ensure your .env file has the API key
        }

        # Perform the search using SerpAPI
        search = serpapi.search(params)

        # Get the first image result link
        image_url = search["images_results"][0]["original"]

        return image_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred while fetching images: {str(e)}")


# Define the API endpoint
@router.post("/search-image")
async def search_image(query: str):
    """Search for images based on the input query and return the image URL."""
    image_link = search_images(query)
    return {"image_url": image_link}
