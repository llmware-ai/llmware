from ollama import Ollama

# Initialize Ollama client
ollama = Ollama(model_name="gemma2")

def generate_feedback(student_answer, reference_text):
    # Generate detailed feedback based on student answer and reference
    prompt = f"Compare the following:\n\nStudent Answer: {student_answer}\n\nReference: {reference_text}\n\nProvide detailed feedback."
    feedback = ollama.chat(prompt)
    return feedback
