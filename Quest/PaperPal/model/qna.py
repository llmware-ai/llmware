from llmware.models import ModelCatalog
import sys
import json

# Load the model
model = ModelCatalog().load_model(
    selected_model="slim-boolean-tool", sample=False, temperature=0.0, max_output=200
)

# Read the script file
try:
    with open("../media/paper.txt", "r") as file:
        script = file.read()
except Exception as e:
    raise ValueError(f"Error reading script file: {e}")

if len(sys.argv) > 1:
    question = sys.argv[1] + " (explain)"
else:
    raise ValueError("No question provided as a command line argument.")

try:
    response = model.function_call(script, function="boolean", params=[question])
except Exception as e:
    raise ValueError(f"Error calling model function: {e}")


try:
    llm_response = response["llm_response"]
    answer = llm_response["answer"][0]
    explanation = llm_response["explanation"][0]
except KeyError as e:
    raise ValueError(f"Error processing model response: missing key {e}")
except IndexError as e:
    raise ValueError(f"Error processing model response: list index out of range {e}")

response_object = {"question": question, "answer": answer, "explanation": explanation}

print(json.dumps(response_object, indent=2))
