import os
import sys
import time 

from llmware.models import ModelCatalog
from llmware.prompts import Prompt
sys.path.append(os.path.join(os.path.dirname(__file__),".."))
from utils import Logger

openai_api_key    = os.environ.get("OPENAI_API_KEY","")
anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY","")
ai21_api_key      = os.environ.get("AI21_API_KEY","")
google_api_key    = os.environ.get("GOOGLE_API_KEY","") 
cohere_api_key    = os.environ.get("COHERE_API_KEY", "")

def test_all_gen_models():
    Logger().log("\ntest_all_gen_models()")
    os.environ["TOKENIZERS_PARALLELISM"] = "false" # This just disables a warning that gets shown when pytest forks the process
    
    output_table_headers = ['Num','Model','Seconds','Answer']
    output_table_data = []
    
    for i, model in enumerate(ModelCatalog().list_generative_models()):
        if model["model_name"] not in ["HF-Generative"]:
            api_key = ""
            # Set the right api_key
            if model["model_family"] == "ClaudeModel": api_key = anthropic_api_key
            if model["model_family"] == "CohereGenModel": api_key = cohere_api_key
            if model["model_family"] == "JurassicModel": api_key = ai21_api_key
            if model["model_family"] == "GoogleGenModel": api_key = google_api_key
            if model["model_family"] == "OpenAIGenModel": api_key = openai_api_key
   
            # Setup the prompt and the context/question
            prompter = Prompt().load_model(model["model_name"], api_key=api_key)
            test_context = """The CEO has a salary of $350,000. 
                Padding with extra characters because Cohere requires a minimum of 250 characters for some reason
                Padding with extra characters because Cohere requires a minimum of 250 characters for some reason
                Padding with extra characters because Cohere requires a minimum of 250 characters for some reason""" 
            test_question = "What is the salary of the CEO?"
            
            # Ask the model the question
            start_time = time.time()
            response = prompter.prompt_main(test_question, prompt_name="number_or_none", context=test_context)
            answer_time = round(time.time()-start_time, 2)
            answer = response["llm_response"].strip()
            
            # Capture the output data
            output_row = [i+1,model["model_name"],answer_time,answer]
            output_table_data.append(output_row)
        else:
            output_row = [i+1,model["model_name"],"NA", "NA(Skipped)"]
            output_table_data.append(output_row)
    Logger().log_table(output_table_headers, output_table_data)