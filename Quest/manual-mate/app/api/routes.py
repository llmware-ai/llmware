from flask import Blueprint, request, jsonify, current_app
from app import create_app
import os

from app.services.manuals_processor import ManualsProcessor
from app.utils.manual_downloader import ManualDownloader
from llmware.library import Library
from llmware.retrieval import Query
from llmware.prompts import Prompt
from llmware.configs import LLMWareConfig

main = Blueprint('main', __name__)

ACTIVE_DB = os.environ['ACTIVE_DB']
LIBRARY_NAME = os.environ['LIBRARY_NAME']
EMBEDDING_MODEL_NAME = os.environ['EMBEDDING_MODEL_NAME']
VECTOR_DB = os.environ['VECTOR_DB'] 
LLM_MODEL_NAME = os.environ['LLM_MODEL_NAME']
LOCAL_DIRECTORY = os.environ['LOCAL_DIRECTORY']
BUCKET_NAME = os.environ['BUCKET_NAME']

LLMWareConfig().set_active_db(ACTIVE_DB)

@main.before_request
def before_request_logging():
    if current_app.debug:
        current_app.logger.info('Request from %s: %s %s',
                        request.remote_addr, request.method, request.full_path)

@main.route("/")
def home():
    return "Alive!"


@main.route('/process_manuals', methods=['POST'])
def process_manuals_endpoint():
    data = request.json
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    llm_model_name = data.get('model', LLM_MODEL_NAME)

    try:
        downloaded_path = ManualDownloader.load_manuals_files(
            LOCAL_DIRECTORY, BUCKET_NAME, over_write=True)
        manuals_path = os.path.join(downloaded_path, "")
        library = Library().create_new_library(LIBRARY_NAME)
        library.add_files(input_folder_path=manuals_path)
        library.install_new_embedding(
            embedding_model_name=EMBEDDING_MODEL_NAME, vector_db=VECTOR_DB)

        prompter = Prompt().load_model(llm_model_name)
        results = Query(library).semantic_query(prompt)

        processor = ManualsProcessor(manuals_path, results, prompter)
        response_data = processor.process(prompt)

        return jsonify({"response": response_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
