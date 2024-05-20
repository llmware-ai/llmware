# app.py
from flask import Flask, render_template, request, jsonify, session
from story_generator import generate_story_ideas

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace 'your_secret_key' with a real secret key for production

@app.route('/')
def index():
    session.clear()  # Clear previous story data
    return render_template('index.html')

@app.route('/generate_story', methods=['POST'])
def generate_story():
    data = request.get_json()
    genre = data['genre']
    character = data['character']
    setting = data['setting']
    conflict = data['conflict']
    continue_story = data.get('continue_story', False)
    current_story = session.get('current_story', "")

    generated_story = generate_story_ideas("phi-3-gguf", genre, character, setting, conflict, continue_story, current_story)
    session['current_story'] = generated_story  # Save the current story to session

    return jsonify({'generated_story': generated_story})

if __name__ == '__main__':
    app.run(debug=True)
