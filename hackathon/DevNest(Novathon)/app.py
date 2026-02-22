from flask import Flask, request, jsonify
from llmware.models import ModelCatalog
from llmware.gguf_configs import GGUFConfigs

# Set global configurations for the model
GGUFConfigs().set_config("max_output_tokens", 250)

# Initialize Flask app
app = Flask(__name__)

# Load the model with GPU acceleration enabled
MODEL_NAME = "llama-2-7b-chat-gguf"
model = None

try:
    model = ModelCatalog().load_model(
        MODEL_NAME, 
        temperature=0.3, 
        sample=True, 
        max_output=250, 
        use_gpu=True  # Ensure GPU is used if available
    )
    print("Model loaded successfully with GPU acceleration.")
except Exception as e:
    print(f"Failed to load the model: {e}")
    model = None

@app.route("/index")
def index():
    """Health check endpoint"""
    return jsonify({"message": "LLM Chat API is running!"})

@app.route("/chat", methods=["POST"])
def chat():
    """
    POST endpoint to send a prompt to the model and receive a response.
    """
    global model
    if not model:
        return jsonify({"error": "Model not loaded. Please check server logs."}), 500

    try:
        # Parse input JSON
        input_data = request.get_json()
        prompt = input_data.get("prompt", None)

        if not prompt:
            return jsonify({"error": "Missing 'prompt' in request body."}), 400

        # Generate response using the model
        model_response = model.inference(prompt)
        bot_response = model_response.get("llm_response", "No response generated.")

        # Return the response
        return jsonify({"prompt": prompt, "response": bot_response})

    except Exception as e:
        return jsonify({"error": f"Error during inference: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)  # Make it accessible on all network interfaces
