"""
    ManualMate is a tool for easily accessing and understanding user manuals for a broad array of home appliances, such as washing machines and dryers.

    This application showcases the Retrieve and Generate (RAG) model, which comprises the following steps:

    1. It initiates with a natural language query to retrieve relevant text segments from an extensive library.
    2. These segments then serve as context in constructing prompts for posing questions to a sophisticated large language model (LLM).

    In this demonstration, we will explore:

    1. Building a comprehensive library and establishing embeddings.
    2. Performing an extensive semantic search throughout the library.
    3. Identifying and selecting the documents most relevant to the query.
    4. Processing each selected document to extract contextual information, which is then used to query our LLM for insights.
    5. Delivering precise answers through a JSON HTTP API.

"""

from app import create_app
from importlib import util
import logging
logging.basicConfig(level=logging.INFO)

app = create_app()

if not util.find_spec("chromadb"):
    print("\nto run this app with chromadb, you need to install the chromadb python sdk:  pip3 install chromadb")

if __name__ == '__main__':
    app.run(debug=True)
