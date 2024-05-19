import os
from dotenv import load_dotenv
from langchain_community.llms import HuggingFaceHub
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
import streamlit as st 

st.set_page_config(
    page_title="📚 Talk to Galvin's OS Textbook",
    page_icon="👻",
)
load_dotenv()

os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN")

prompt_template = """To provide the best response, consider the following context and question carefully:

Context: {context}
Question: {question}

Provide an accurate and concise response based on the given context and question.
"""

prompt = PromptTemplate(template=prompt_template, input_variables=["question", "context"])

embeddings = SentenceTransformerEmbeddings(model_name="llmware/industry-bert-insurance-v0.1")

load_vector_store = Chroma(persist_directory="operatingsystem/embed", embedding_function=embeddings)

lvs = load_vector_store.as_retriever(search_kwargs={"k":2})

repo = "llmware/bling-sheared-llama-1.3b-0.1"

hfllm = HuggingFaceHub(
    repo_id=repo, model_kwargs={"temperature": 0.3, "max_length": 500}
)

kwargs_type = {"prompt": prompt}

def quesans():
    qa = RetrievalQA.from_chain_type(
    llm=hfllm,
    chain_type="stuff",
    retriever=lvs,
    return_source_documents=True,
    chain_type_kwargs=kwargs_type,
    verbose=True
    )
    return qa

qa = quesans()

def main():

    st.title("📚 Talk to Galvin's OS Textbook ")

    st.markdown(
        """
        <style>
        body {
            background-color: #FFC0CB; 
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    text_query = st.text_area("Type your question here...", height=100)

    generate_response_btn = st.button("Get Answer")

    st.subheader("🎉 Answer 🎉")

    if generate_response_btn and text_query:
        with st.spinner("Generating response..."):
            text_response = qa(text_query)
            if text_response:
                st.write(text_response)
                st.success("Response generated!")
            else:
                st.error("Oops! I have no idea what you mean.")
            st.balloons() 

if __name__ == "__main__":
    main()

