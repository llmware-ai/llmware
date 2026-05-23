import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from llmware.prompts import Prompt
from llmware.gguf_configs import GGUFConfigs

app = Flask(__name__)
CORS(app)

# Ensure upload directory exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure GGUF models
GGUFConfigs().set_config("max_output_tokens", 500)

# Predefined list of chat models
CHAT_MODELS = [
    "phi-3-gguf",
    "llama-2-7b-chat-gguf",
    "llama-3-instruct-bartowski-gguf",
    "openhermes-mistral-7b-gguf",
    "zephyr-7b-gguf",
    "tiny-llama-chat-gguf"
]

class DocumentQAHandler:
    def __init__(self, model_name="phi-3-gguf"):
        self.prompter = None
        self.model_name = model_name
        self.current_file = None

    def load_document(self, file_path):
        try:
            # Initialize the prompt with the model
            self.prompter = Prompt().load_model(
                self.model_name, 
                temperature=0.0,
                sample=False,
                max_output=450
            )
            
            # Add the source document
            sources = self.prompter.add_source_document(
                os.path.dirname(file_path), 
                os.path.basename(file_path)
            )
            
            self.current_file = os.path.basename(file_path)
            return True
        except Exception as e:
            print(f"Error loading document: {e}")
            return False

    def ask_question(self, question):
        if not self.prompter or not self.current_file:
            return "No document loaded. Please upload a document first."
        
        try:
            response = self.prompter.prompt_with_source(
                prompt=question, 
                prompt_name="default_with_context"
            )
            
            # Extract the LLM response
            if response and len(response) > 0:
                return response[0]["llm_response"]
            else:
                return "No response generated."
        except Exception as e:
            return f"Error processing question: {str(e)}"

    def clear_document(self):
        if self.prompter:
            self.prompter.clear_source_materials()
        self.current_file = None

# Global document QA handler
qa_handler = DocumentQAHandler()

# Global variable to store the current chat model
current_chat_model = None

def load_chat_model(model_name=None):
    """
    Load a chat model with error handling
    """
    global current_chat_model

    try:
        # If no model specified, use the first model in the list
        if not model_name:
            model_name = CHAT_MODELS[0]  # Default to first model

        # Load the model
        current_chat_model = Prompt(save_state=True).load_model(
            model_name,
            temperature=0.0,
            sample=False,
            max_output=450,
            register_trx=True
        )

        print(f"Model {model_name} loaded successfully.")
        return current_chat_model

    except Exception as e:
        print(f"Error loading model {model_name}: {e}")
        print(f"Traceback: {sys.exc_info()}")
        current_chat_model = None
        return None

# Initial model load
load_chat_model()

@app.route('/upload', methods=['POST'])
def upload_document():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Save the file
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    
    # Load the document
    if qa_handler.load_document(filepath):
        return jsonify({"message": f"File {file.filename} uploaded successfully"}), 200
    else:
        return jsonify({"error": "Failed to load document"}), 500

@app.route('/ask', methods=['POST'])
def ask_document_question():
    data = request.json
    question = data.get('question', '')
    
    if not question:
        return jsonify({"error": "No question provided"}), 400
    
    answer = qa_handler.ask_question(question)
    return jsonify({"answer": answer})

@app.route('/clear', methods=['POST'])
def clear_document():
    qa_handler.clear_document()
    return jsonify({"message": "Document cleared successfully"})

@app.route('/chat', methods=['POST'])
def chat():
    global current_chat_model

    try:
        # Get data from request
        data = request.json
        prompt = data.get('prompt', '')

        # Optional: Allow model selection
        model_name = data.get('model', None)

        # Reload model if different or not loaded
        if model_name and model_name != getattr(current_chat_model, 'model_name', None):
            current_chat_model = load_chat_model(model_name)
        elif not current_chat_model:
            current_chat_model = load_chat_model()

        # Validate model is loaded
        if not current_chat_model:
            return jsonify({"error": "Failed to load any chat model"}), 500

        # Generate response
        response_generator = current_chat_model.prompt_main(prompt)

        # Return response
        return jsonify({
            "response": response_generator['llm_response']
        })

    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/models', methods=['GET'])
def list_models():
    return jsonify({"models": CHAT_MODELS})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)