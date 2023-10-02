''' This example demonstrates inspection of prompt history which can be particularly useful in AI Audit scenarios
      1. Prompt save persistence
      2. Prompt interaction history
      3. Prompt dialog tracker
      4. Prompt Interaction Report generation
      5. Prompt evidence verfication
'''
import json
import os
from llmware.library import Library
from llmware.prompts import Prompt
from llmware.retrieval import Query
from llmware.setup import Setup
from llmware.util import PromptState, Datasets

# Update these values with your own API Keys, either by setting env vars or editing them directly here:
openai_api_key    = os.environ["OPENAI_API_KEY"]

os.environ["TOKENIZERS_PARALLELISM"] = "false" # Avoiding a HuggingFace warning about process forking

# Demonstrate interacting with the prompts in a variety of ways
def prompt_operations(llm_model):

    # Create a new prompter with state persistence
    prompter = Prompt(save_state=True)
    # Capture the prompt_id (which can be used later to reload state)
    prompt_id = prompter.prompt_id
    # Load the model
    prompter.load_model(llm_model,api_key=openai_api_key)
    # Define a list of prompts
    prompts = [
        {"query": "How old is Bob?", "context": "John is 43 years old.  Bob is 27 years old."},
        {"query": "When did COVID start?", "context": "COVID started in March of 2020 in most of the world."},
        {"query": "What is the current stock price?", "context": "The stock is trading at $26 today."},
        {"query": "When is the big game?", "context": "The big game will be played on November 14, 2023."},
        {"query": "What is the CFO's salary?", "context": "The CFO has a salary of $285,000."},
        {"query": "What year is Michael in school?", "context": "Michael is starting 11th grade."}
        ]

    # Iterate through the prompt which will save each response dict in in the prompt_state    
    print (f"\n > Sending a series of prompts to {llm_model}...")
    for i, prompt in enumerate(prompts):
        print ("  - " + prompt["query"])
        response = prompter.prompt_main(prompt["query"],context=prompt["context"],register_trx=True)
    
    # Print how many interactions are now in the prompt history
    interaction_history = prompter.interaction_history
    print (f"\n > Prompt Interaction History now contains {len(interaction_history)} interactions")
    
    # Use the dialog_tracker to regenerate the conversation with the LLM
    print (f"\n > Reconstructed Dialog")
    dialog_history = prompter.dialog_tracker
    for i, conversation_turn in enumerate(dialog_history):
        print("  - ", i, "[user]: ", conversation_turn["user"])
        print("  - ", i, "[ bot]: ", conversation_turn["bot"])

    # Saving and cleae the prompt state
    prompter.save_state()
    prompter.clear_history()

    # Print the number of interactions
    interaction_history = prompter.interaction_history
    print (f"\n > Prompt history has been cleared")
    print (f"\n > Prompt Interaction History now contains {len(interaction_history)} interactions")

    # Reload the prompt state using the prompt_id and print again the number of interactions
    prompter.load_state(prompt_id)
    interaction_history = prompter.interaction_history
    print (f"\n > The previous prompt state has been re-loaded")
    print (f"\n > Prompt Interaction History now contains {len(interaction_history)} interactions")

    # Generate a Promppt transaction report
    prompt_transaction_report = PromptState().generate_interaction_report([prompt_id])
    print (f"\n > A prompt transaction report has been generated: {prompt_transaction_report}")


def prompt_fact_checking(library_name, llm_model):

    print (f"\n > Creating library {library_name}...")
    library = Library().create_new_library(library_name)
    sample_files_path = Setup().load_sample_files()
    library.add_files(os.path.join(sample_files_path,"SmallLibrary"))

     # Create vector embeddings for the library using the "industry-bert-contracts" model and store them in faiss
    print (f"\n > Generating vector embeddings using embedding model: 'industry-bert-contracts'...")
    library.install_new_embedding(embedding_model_name="industry-bert-contracts", vector_db="faiss")

    # Perform a semantic search against our library.  This will gather evidence to be used in the LLM prompt
    print (f"\n > Performing a semantic query...")
    query_results = Query(library).semantic_query("what are the termination provisions", result_count=20)

    # Create a new prompter based on the query results and the given llm_model
    print (f"\n > Prompting with query results...")
    prompter = Prompt(save_state=True)
    prompter.load_model(llm_model,api_key=openai_api_key)
    sources = prompter.add_source_query_results(query_results)
    response = prompter.prompt_with_source("Is the termination provision 12 months?")
   
    # Fact-check the first response
    print (f"\n > Checking sources")

    # Check sources
    source_check = prompter.evidence_check_sources(response)[0]["source_review"]
    print (f"\nEvidence check of sources:\n{json.dumps(source_check, indent=2)}")
    
    # Check numbers
    number_check = prompter.evidence_check_numbers(response)[0]["fact_check"]
    print (f"\nEvidence check of numbers:\n{json.dumps(number_check, indent=2)}")

    # Check comparison stats
    token_comparison = prompter.evidence_comparison_stats(response)[0]["comparison_stats"]
    print (f"\nEvidence check of comparison stats:\n{json.dumps(token_comparison, indent=2)}")


prompt_operations(llm_model="gpt-3.5-turbo")
prompt_fact_checking("test_fact_checking", llm_model="gpt-3.5-turbo")
