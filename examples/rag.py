# This example demonstrates Retrieval Augmented Retrieval (RAG):
import os
from llmware.library import Library
from llmware.retrieval import Query
from llmware.prompts import Prompt
from llmware.setup import Setup

# Update this value with your own API Key, either by setting the env var or editing it directly here:
openai_api_key = os.environ["OPENAI_API_KEY"]

# A self-contained end-to-end example of RAG
def end_to_end_rag():
    
    # Create a library called "Agreements", and load it with llmware sample files
    print (f"\n > Creating library 'Agreements'...")
    library = Library().create_new_library("Agreements")
    sample_files_path = Setup().load_sample_files()
    library.add_files(os.path.join(sample_files_path,"Agreements"))

    # Create vector embeddings for the library using the "industry-bert-contracts" model and store them in Milvus
    print (f"\n > Generating vector embeddings using embedding model: 'industry-bert-contracts'...")
    library.install_new_embedding(embedding_model_name="industry-bert-contracts", vector_db="milvus")

    # Perform a semantic search against our library.  This will gather evidence to be used in the LLM prompt
    print (f"\n > Performing a semantic query...")
    os.environ["TOKENIZERS_PARALLELISM"] = "false" # Avoid a HuggingFace tokenizer warning
    query_results = Query(library).semantic_query("Termination", result_count=20)

    # Create a new prompter using the GPT-4 and add the query_results captured above
    prompt_text = "Summarize the termination provisions"
    print (f"\n > Prompting LLM with '{prompt_text}'")
    prompter = Prompt().load_model("gpt-4", api_key=openai_api_key)
    sources = prompter.add_source_query_results(query_results)

    # Prompt the LLM with the sources and a query string
    responses = prompter.prompt_with_source(prompt_text, prompt_name="summarize_with_bullets")
    for response in responses:
        print ("\n > LLM response\n" + response["llm_response"])
    
    # Finally, generate a CSV report that can be shared
    print (f"\n > Generating CSV report...")
    report_data = prompter.send_to_human_for_review()
    print ("File: " + report_data["report_fp"] + "\n")

end_to_end_rag()

# **********************************************************************************************************
# ************************************** SAMPLE OUTPUT *****************************************************
# **********************************************************************************************************
'''
> python examples/rag.py

 > Creating library 'Agreements'...

 > Generating vector embeddings using embedding model: 'industry-bert-contracts'...

 > Performing a semantic query...

 > Prompting LLM with 'Summarize the termination provisions'

 > LLM response
- Employment period ends on the first occurrence of either the 6th anniversary of the effective date or a company sale.
- Early termination possible as outlined in sections 3.1 through 3.4.
- Employer can terminate executive's employment under section 3.1 anytime without cause, with at least 30 days' prior written notice.
- If notice is given, the executive is allowed to seek other employment during the notice period.

 > Generating CSV report...
File: /Users/turnham/llmware_data/prompt_history/interaction_report_Fri Sep 29 12:07:42 2023.csv

'''
