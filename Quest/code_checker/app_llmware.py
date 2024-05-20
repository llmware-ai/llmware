from flask import Flask, request, jsonify
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

app = Flask(__name__)

# Load the model and tokenizer
model_name = "llmware/bling-tiny-llama-v0"
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Add padding token if missing
if tokenizer.pad_token is None:
    tokenizer.add_special_tokens({'pad_token': tokenizer.eos_token})
    model.resize_token_embeddings(len(tokenizer))

# Define the /complete route
# def complete_code():
#     # Extract the prompt from the request JSON data
#     prompt = request.json['prompt']

#     # Tokenize the prompt
#     inputs = tokenizer(prompt, return_tensors="pt", padding="max_length", max_length=512)

#     # Generate completion using the model
#     with torch.no_grad():
#         outputs = model.generate(**inputs, max_length=512, temperature=0.9, num_return_sequences=1)

#     # Decode the generated completion
#     completion = tokenizer.decode(outputs[0], skip_special_tokens=True)

#     # Return the completion as a JSON response
#     return jsonify({"completion": completion})

# Define the /complete route
@app.route('/complete', methods=['POST'])
def complete_code():
    # Extract the prompt from the request JSON data
    prompt = request.json['prompt']

    # Tokenize the prompt
    inputs = tokenizer(prompt, return_tensors="pt", padding="max_length", max_length=512)

    # Generate completion using the model
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=1024, temperature=0.9, num_return_sequences=1)

    # Decode the generated completion
    completion = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Return the completion as a JSON response
    return jsonify({"completion": completion})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
