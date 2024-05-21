
from llmware.prompts import Prompt
from llmware.configs import LLMWareConfig

from llm_embeddings import install_vector_embeddings, setup_library

from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
# from llmware.models import ModelCatalog


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

class Query(BaseModel):
	query: str
     
# Define a response model
class AnswerResponse(BaseModel):
    answer: str

@app.post("/answer",response_model=AnswerResponse)
async def answer(query_string: Query):
    model_name = "llmware/bling-1b-0.1"
    result_ans, page_no = fast_start_prompting(model_name,query_string.query)
    return AnswerResponse(answer=result_ans  + '    ---> MORE DETAIL AT PAGE-NO ' + str(page_no) + ' IN CONSTITUTION PAGE')


def hello_world_questions(sample_query='With what part criteria  shall be the citizens of Nepal?'):

    LLMWareConfig().set_active_db("sqlite")
    LLMWareConfig().set_vector_db("chromadb")
    library = setup_library("llm1")
    embedding_model_name = "mini-lm-sbert"
    context_dict = install_vector_embeddings(library, embedding_model_name, sample_query)


    # Ensure that context_dict has at least 5 items to avoid IndexError
    if len(context_dict) >= 5:
        # Concatenate the 'context' values from the first five items in context_dict using a loop
        combined_context = ''.join(context_dict[i]['context'] for i in range(5))

        # Create the test_list with the concatenated context
        test_list = [
            {
                "query": sample_query,
                "context": combined_context
            }
        ]
    else:
        # Handle the case where context_dict has fewer than 5 items
        print("Error: context_dict does not have at least 5 items.")


    return test_list, context_dict[0]['page_num']


def fast_start_prompting(model_name,query_qn):

    test_list, page_no = hello_world_questions(query_qn)
    prompter = Prompt().load_model(model_name)

    for i, entries in enumerate(test_list):
        print(f"\n{i+1}. Query: {entries['query']}")
     
        output = prompter.prompt_main(entries["query"],
                                      context=entries["context"],
                                      prompt_name="default_with_context",
                                      temperature=0.30)

        llm_response = output["llm_response"].strip("\n")
        print(f"LLM Response: {llm_response}")

    return llm_response, page_no


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)


