from fastapi import FastAPI
from pydantic import BaseModel
from llmware.prompts import Prompt
import re

# Load the model, can be:
# 1. llmware/dragon-yi-6b-gguf
# 2. llmware/bling-phi-3-gguf
# etc
model_name = "llmware/dragon-yi-6b-gguf"
prompter = Prompt().load_model(model_name)

app = FastAPI()

class Prompt(BaseModel):
    content: str
    os: str
    shell: str

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/suggest/")
def suggest(prompt: Prompt):
    response = prompter.prompt_main(f'shell command in {prompt.os} {prompt.shell} to ' + str(prompt.content) + "? answer with first one actionable commands only without description", context=f"operating system is {prompt.os}", prompt_name="default_with_context", temperature=0.9)
    lines = response['llm_response'].split('\n')
    first_line = next(line for line in lines if line.strip())
    filtered_response = re.sub(r"^\d+\.\s*", "", first_line)
    return {"result": f"{filtered_response}"}