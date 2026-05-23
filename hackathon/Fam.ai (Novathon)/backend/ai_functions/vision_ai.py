import PIL
import google.generativeai as genai
from PIL import Image
import dotenv
import os

dotenv.load_dotenv()
genai.configure(api_key=os.environ.get('GOOGLE_AI_API'))
model = genai.GenerativeModel(model_name="gemini-1.5-flash")
classifier_prompt = "Classify the image. 1 for MRI and 2 for not MRI"
ocr_prompt = "Provide the summary from the medical prescription"


def ask_ai(img: PIL.Image, prompt: str):
    response = model.generate_content([
        prompt,
        img])
    return response.text
