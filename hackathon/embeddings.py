import pinecone
from llmware import LLMWareClient
from sklearn.metrics.pairwise import cosine_similarity
from feedback import generate_feedback  # Import the function from feedback.py

# Initialize LLMWare client
llmware_client = LLMWareClient(api_key="your_llmware_api_key")

# Initialize Pinecone client
pinecone.init(api_key="your_pinecone_api_key", environment="us-west1-gcp")
index = pinecone.Index("exam-eval")

def generate_embeddings(text):
    # Generate embeddings from text using LLMWare
    response = llmware_client.generate_embeddings(text)
    return response['vectors']

def store_embeddings(text, vectors, doc_id):
    # Store embeddings in Pinecone
    index.upsert([(doc_id, vectors, {"text": text})])

def retrieve_similar_content(query_text):
    # Retrieve similar content from the vector database
    query_vectors = generate_embeddings(query_text)
    result = index.query(query_vectors, top_k=5, include_metadata=True)
    return result['matches']

def evaluate_answer(student_answer, answer_key_vectors):
    # Compare student answer with the answer key using cosine similarity
    student_vectors = generate_embeddings(student_answer)
    similarity = cosine_similarity([student_vectors], [answer_key_vectors])
    score = round(similarity[0][0] * 100, 2)  # Convert to percentage
    return score

def generate_report(student_answers, answer_key):
    # Generate a report comparing answers to the answer key
    report = {}
    for q_id, student_answer in student_answers.items():
        key_vectors = generate_embeddings(answer_key[q_id])
        score = evaluate_answer(student_answer, key_vectors)
        reference = retrieve_similar_content(student_answer)[0]['metadata']['text']
        feedback = generate_feedback(student_answer, reference)  # Use the imported function
        report[q_id] = {"score": score, "feedback": feedback}
    return report
