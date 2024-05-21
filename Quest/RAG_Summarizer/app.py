import os
import sqlite3
import streamlit as st
from transformers import pipeline
from llmware.setup import Setup
from llmware.library import Library
from llmware.prompts import Prompt
from llmware.retrieval import Query
from llmware.configs import LLMWareConfig

# Ensure necessary directories exist
os.makedirs("data/sample_files", exist_ok=True)
os.makedirs("data/database", exist_ok=True)

# llmware configuration
LLMWareConfig().set_active_db("sqlite")
LLMWareConfig().set_vector_db("chromadb")  # Set vector DB to ChromaDB
LLMWareConfig().set_config("debug_mode", 2)

# extract text from PDF
def extract_text_from_pdf(pdf_path):
    import PyPDF2
    with open(pdf_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + "\n"
    return text

# store text in SQLite
def store_text_in_db(text, db_name="data/database/documents.db"):
    os.makedirs(os.path.dirname(db_name), exist_ok=True)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS documents (id INTEGER PRIMARY KEY, content TEXT)")
    c.execute("INSERT INTO documents (content) VALUES (?)", (text,))
    conn.commit()
    conn.close()

# retrieve text from database based on query
def retrieve_text_from_db(query, db_name="data/database/documents.db"):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT content FROM documents")
    documents = c.fetchall()
    conn.close()

    relevant_texts = []
    for doc in documents:
        if query.lower() in doc[0].lower():
            relevant_texts.append(doc[0])
    
    return "\n".join(relevant_texts)

# responce from llm
def generate_response(context, question):
    nlp = pipeline("text-generation", model="gpt2")
    input_text = context + "\n\nQ: " + question + "\nA:"
    response = nlp(input_text, max_length=500, num_return_sequences=1)

    print("Debug: Response from model:", response)

    generated_text = response[0].get('generated_text') or response[0].get('text')

    if generated_text:
        return generated_text.split("A:")[1].strip()
    else:
        return "Unable to generate response."

# library
def setup_library(library_name, ingestion_folder_path):
    library = Library().create_new_library(library_name)
    library.add_files(input_folder_path=ingestion_folder_path, chunk_size=400, max_chunk_size=600, smart_chunking=1)
    return library

# vector embeddings
def install_vector_embeddings(library, embedding_model_name):
    try:
        library.install_new_embedding(embedding_model_name=embedding_model_name, vector_db=LLMWareConfig().get_vector_db(), batch_size=100)
        st.success("Vector embeddings have been installed on the library.")
    except Exception as e:
        st.error(f"Error installing vector embeddings: {e}")
    return library

# UI
def main():
    st.title("RAG Summarizer with llmware")
    st.write("Upload a PDF and ask questions about its content.")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file is not None:
        # save uploaded PDF to 'data/sample_files' folder
        pdf_path = os.path.join("data/sample_files", uploaded_file.name)
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # text to database
        text = extract_text_from_pdf(pdf_path)
        store_text_in_db(text)

        # store in library
        library_name = "streamlit_library"
        library = setup_library(library_name, "data/sample_files")
        st.success("PDF content has been parsed and stored in the library.")
        
        # vector embeddings
        embedding_model = "mini-lm-sbert"
        library = install_vector_embeddings(library, embedding_model)

    query = st.text_input("Enter your query")
    if st.button("Get Answer"):
        if query:
            context = retrieve_text_from_db(query)
            if context:
                response = generate_response(context, query)
                st.subheader("Answer:")
                st.write(response)
            else:
                st.write("No relevant information found in the documents.")

if __name__ == "__main__":
    main()
