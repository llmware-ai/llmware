import os
from fastapi import APIRouter, HTTPException
from llmware.models import ModelCatalog

# Initialize FastAPI router
router = APIRouter()


# Register the Ollama model (you can register multiple models similarly)
def register_models():
    try:
        # Register and load the model
        ModelCatalog().register_ollama_model(model_name="smollm")
        model = ModelCatalog().load_model("smollm")
        return model
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register or load model: {str(e)}")


# Initialize the model
model = register_models()


@router.post("/check-sentence")
async def check_sentence(sentence: str):
    """API to check a sentence for grammar errors and provide suggestions."""
    try:
        # Call the model for inference
        response = model.inference(
            f"i will give you sentence to check - {sentence} . find any error in this sentence if there is error it will give suggestion to fix it and some suggestion on what i did wrong")

        # Process the response from the model
        return {"original_sentence": sentence, "suggestions": response["llm_response"].replace("\n", "")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing the sentence: {str(e)}")
