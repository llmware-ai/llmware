from flask import Flask, request, jsonify, render_template
from llmware.models import ModelCatalog
from llmware.agents import LLMfx

app = Flask(__name__)

# Load models
summary_model = ModelCatalog().load_model("slim-summary-tool", sample=False, temperature=0.0, max_output=200)
sentiment_model = LLMfx()
sentiment_model.load_tool("sentiment")
chatbot_model = ModelCatalog().load_model("bling-phi-3-gguf", sample=False, temperature=0.0)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    document_text = data['document_text']
    model_name = data['model_name']
    summary = summary_model.function_call(document_text)
    return jsonify({'summary': summary['llm_response']})

@app.route('/analyze_sentiment', methods=['POST'])
def analyze_sentiment():
    data = request.get_json()
    if 'essay_text' not in data:
        return jsonify({'error': 'Missing essay_text in request data'}), 400
    
    essay_text = data['essay_text']
    
    # Perform sentiment analysis
    sentiment_result = sentiment_model.sentiment(essay_text)
    
    # Extract sentiment and confidence score
    sentiment_value = sentiment_result["llm_response"]["sentiment"]
    confidence_level = sentiment_result["confidence_score"]

    return jsonify({
        'sentiment': sentiment_value,
        'confidence': confidence_level
    })

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data['user_input']
    model_name = data['model_name']
    
    # Print user input and model name for debugging
    print(f"User Input: {user_input}")
    print(f"Model Name: {model_name}")
    
    response = chatbot_model.inference(user_input)
    
    # Print the raw response from the model
    print(f"Model Response: {response}")
    
    # Handle empty response
    if not response:
        return jsonify({'response': 'No response from model'}), 500
    
    return jsonify({'response': response})

if __name__ == "__main__":
    app.run(debug=True)
