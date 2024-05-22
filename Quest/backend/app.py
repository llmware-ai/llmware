from flask import Flask, request, jsonify, render_template
from llmware.models import ModelCatalog
import requests

app = Flask(__name__)

# Load models
extract_model = ModelCatalog().load_model("slim-extract-tool", temperature=0.0, sample=False)
summary_model = ModelCatalog().load_model("slim-summary-tool", sample=False, temperature=0.0, max_output=200)
response_model = ModelCatalog().load_model("bling-stablelm-3b-tool", sample=False, temperature=0.0)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    user_query = request.json.get('query')
    response = get_response(user_query)
    log_message(user_query, response)
    return jsonify({'response': response})

def get_response(user_query):
    # Step 1: Extract relevant information from the query
    extract_keys = ["customer issue", "requested service", "preferred contact method"]
    extracted_info = {}
    for key in extract_keys:
        result = extract_model.function_call(user_query, params=[key])
        extracted_info[key.replace(" ", "_")] = result["llm_response"].get(key.replace(" ", "_"), "N/A")
    
    # Step 2: Summarize the extracted information for clarity
    summary = summary_model.function_call(str(extracted_info), params=["summarize"])
    
    # Step 3: Generate a response based on summarized information
    response = response_model.inference(summary["llm_response"], add_context=user_query)
    return response["llm_response"]

def log_message(user_query, response):
    with open('chat_log.txt', 'a') as log_file:
        log_file.write(f"User: {user_query}\nBot: {response}\n\n")

if __name__ == "__main__":
    app.run(debug=True)
