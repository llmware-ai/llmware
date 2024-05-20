import os
import json
from llmware.library import Library
from llmware.retrieval import Query
from llmware.status import Status
from llmware.models import ModelCatalog
from llmware.configs import LLMWareConfig
from llmware.models import ModelCatalog
from llmware.prompts import Prompt


class SightLLM:
    def __init__(self, libName, embeddingsModel, generativeModel, folder, db='sqlite', vectorDB='chromadb'):
        LLMWareConfig().set_config("debug_mode", 2)
        LLMWareConfig().set_active_db(db)
        LLMWareConfig.set_vector_db(vectorDB)
        self.libName = libName
        self.embeddingsModel = embeddingsModel
        self.generativeModel = generativeModel
        self.folder : str = folder
        self.docsPath : str = os.path.join(os.getcwd(), folder)
        self.lib = self.buildLibrary()
        self.loadEmbeddings()
        self.model = Prompt().load_model(self.generativeModel)

        
        
    def buildLibrary(self):
        lib = Library().create_new_library(self.libName)
        lib.add_files(self.docsPath)
        return lib
    
    def libraryDetails(self):
        lib_details : dict = self.lib.get_library_card()
        detailsPrettified = json.dumps(lib_details, indent=4)
        print(detailsPrettified, end="\n\n")
        print("Model Details: ")
        print(self.model)
    
    
    def listModels(self):
        llm_local_models = ModelCatalog().list_open_source_models()
        for model in llm_local_models:
            print(f"{model['model_name']}  - ({model['model_family']})")
    
    
    def loadEmbeddings(self, batch=100):
        vectorDB = LLMWareConfig().get_vector_db()
        self.lib.install_new_embedding(
            embedding_model_name=self.embeddingsModel, 
            vector_db=vectorDB,
            batch_size=batch)
        update = Status().get_embedding_status("innersight", self.embeddingsModel)
        


    def generatePrompt(self, query):
        results = Query(self.lib).semantic_query(query, result_count=50)
        self.model.add_source_query_results(query_results=results)
        response = self.model.prompt_with_source(query, prompt_name="default_with_context", temperature=0.3, max_output=256)
        return response[0]['llm_response']

    