from fastapi import FastAPI, Query
from prompt import SightLLM
from fastapi.middleware.cors import CORSMiddleware



libName = "innersight"
folder = "data"
embeddingsModel = "llmrails/ember-v1"
generativeModel = "TheBloke/zephyr-7B-beta-GGUF"
AI = SightLLM(libName, embeddingsModel, generativeModel, folder, 'sqlite', 'chromadb')
AI.libraryDetails()


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)



@app.get("/query/")
async def read_items(query: str = Query(None, min_length=1, max_length=200)):
    print(f"Generation started on prompt: {query}")
    llmResponse = AI.generatePrompt(query)
    return {
        "response": llmResponse
    }

