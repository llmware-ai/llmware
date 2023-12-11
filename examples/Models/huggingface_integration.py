
""" This example demonstrates the use of HuggingFace models
    1. Use llmware models available on HuggingFace for generating vector embeddings
    2. Load a basic decoder generative model from Huggingface and use it
    3. Customizing a generative model with weights from a custom fine-tuned model 
    4. Using a Transformers model for embedding
    5. Using a SentenceTransformers model for embedding
"""


import os
import torch
from llmware.configs import LLMWareConfig
from llmware.library import Library
from llmware.retrieval import Query
from llmware.models import ModelCatalog, HFEmbeddingModel
from llmware.prompts import Prompt
from llmware.setup import Setup
from llmware.util import CloudBucketManager


#   note: starting in llmware-0.1.10, transformers and sentence_transformers are included in the pip install

try:
    from transformers import AutoModel, AutoTokenizer, AutoModelForCausalLM
except ImportError:
    raise ImportError (
        "This example requires classes from the 'transformers' Python package. " 
        "You can install it with 'pip install transformers'"
    )
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    raise ImportError (
        "This example requires classes from the 'sentence-transformers' Python package" 
        "You can install it with 'pip install sentence-transformers'"
    )


# Load an llmware model from Hugging Face to generate vector embeddings
def use_llmware_hf_models_for_embedding():

    #   llmware industry models currently published on HuggingFace (more will be coming!)
    #   *** use any HF embedding model, e.g., BERT, Roberta, etc.
    #   e.g., llmware_industry_models = "llmware/industry-bert-sec-v0.1",
    #                                    "llmware/industry-bert-asset-management-v0.1",
    #                                    "llmware/industry-bert-contracts-v0.1",
    #                                    "llmware/industry-bert-insurance-v0.1"

    #   Choose one
    hf_model_name = "llmware/industry-bert-sec-v0.1"
    
    #   Load the model using the Transformer classes and then into llmware using an HFEmbeddingModel
    print (f"\n > Loading model '{hf_model_name}'from HuggingFace...")
    hf_tokenizer = AutoTokenizer.from_pretrained(hf_model_name)
    hf_model = AutoModel.from_pretrained(hf_model_name)

    #   pass instantiated HF model and tokenizer to HFEmbeddingModel class
    llmware_model = HFEmbeddingModel(model=hf_model, tokenizer=hf_tokenizer,model_name=hf_model_name)

    # Generate an vector embedding
    sample = "This is a sample sentence"
    vector_embedding = llmware_model.embedding(sample)
    print (f"\n > Generating a vector embedding for: '{sample}'\n\n{vector_embedding}")

    return vector_embedding


# Load a basic decoder generative model from Huggingface and use it
def load_and_use_decoder_generative_model():

    # These are some good 'off-the-shelf' smaller testing generative models from HuggingFace
    hf_model_testing_list = ["facebook/opt-125m", "facebook/opt-350m", "facebook/opt-1.3b",
                             "EleutherAI/pythia-70m-v0", "EleutherAI/pythia-160m-v0", "EleutherAI/pythia-410m-v0",
                             "EleutherAI/pythia-1b-v0", "EleutherAI/pythia-1.4b-v0"]

    # Here we'll just select one of the above models
    model_name = hf_model_testing_list[6]

    # Load the model using the Transformer classes
    print (f"\n > Loading model '{model_name}'from HuggingFace...")
    hf_model = AutoModelForCausalLM.from_pretrained(model_name)
    hf_tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Bring the model into llware.  These models were not trained on instruction following, 
    # so we set instruction_following to False
    model = ModelCatalog().load_hf_generative_model(hf_model, hf_tokenizer, instruction_following=False)

    # Make a call to the model
    prompt_text = "The future of artificial intelligence is likely to be"
    print (f"\n > Prompting the model with '{prompt_text}'")
    output = model.inference(prompt_text)["llm_response"]
    print(f"\nResponse:\n{prompt_text}{output}")

    return output


# Load a HuggingFace generative model and override the weights to use a custom user-developed fine-tuned model
def override_generative_model_weights_with_custom_fine_tuned_model():

    # These are some good 'off-the-shelf' smaller testing generative models from HuggingFace
    hf_model_testing_list = ["facebook/opt-125m", "facebook/opt-350m", "facebook/opt-1.3b",
                             "EleutherAI/pythia-70m-v0", "EleutherAI/pythia-160m-v0", "EleutherAI/pythia-410m-v0",
                             "EleutherAI/pythia-1b-v0", "EleutherAI/pythia-1.4b-v0"]

    # Select a model
    model_name = "EleutherAI/pythia-410m-v0"

    # Load the model using the Transformer classes
    print (f"\n > Loading model '{model_name}'from HuggingFace...")
    hf_model = AutoModelForCausalLM.from_pretrained(model_name)
    hf_tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Retrive the custom fine-tuned model
    # Note: This is a custom model that has been developed only for testing and demonstration purposes
    custom_model_name = "contracts-pythia-hf-410m-v0"
    print (f"\n > Loading custom model '{custom_model_name}'from llmware...")
    custom_model_path = os.path.join(LLMWareConfig.get_model_repo_path(),custom_model_name)
    if not os.path.exists(custom_model_path):
        CloudBucketManager().pull_single_model_from_llmware_public_repo(custom_model_name)

    # Override the hf_model default model weights with our own custom-trained weights and load it into llmware
    print (f"\n > Overriding model '{model_name}' to use custom-trained weights from '{custom_model_name}'...")
    hf_model.load_state_dict(torch.load(os.path.join(custom_model_path,"pytorch_model.bin"), map_location=torch.device('cpu')), strict=False)
    model = ModelCatalog().load_hf_generative_model(hf_model, hf_tokenizer, instruction_following=False)
    
    # Interact with the model
    prompt_text = "According to the terms of the executive stock option plan,"
    print (f"\n > Prompting the model with '{prompt_text}'")
    output = model.inference(prompt_text)["llm_response"]
    print(f"\nResponse:\n{prompt_text}{output}")

    return output


# Use a Transformers model for embedding
def use_transformers_model_for_embedding(library_name, model_name):   

    # Create a library and add some documents so we can do some vector embeddings
    print (f"\n > Creating a library...")
    library = Library().create_new_library(library_name)
    sample_files_path = Setup().load_sample_files()
    library.add_files(input_folder_path=os.path.join(sample_files_path, "SmallLibrary"))

    # Load the model
    print (f"\n > Loading model '{model_name}'")
    hf_model = AutoModel.from_pretrained(model_name)
    hf_tokenizer = AutoTokenizer.from_pretrained(model_name)
  
    # Create vector embeddings
    print (f"\n > Creating vector embeddings...")
    library.install_new_embedding(model=hf_model, tokenizer=hf_tokenizer, from_hf=True, vector_db="faiss", batch_size=50)
    
    # Perform a query
    query_term = "salary"
    print (f"\n > Performing query for {query_term}...")
    query = Query(library=library, embedding_model_name=model_name, embedding_model=hf_model, tokenizer=hf_tokenizer, from_hf=True)
    query_results = query.semantic_query(query_term,result_count=3)
    print (f"Top 3 Results:")
    for i, result in enumerate(query_results): 
        file_source = result["file_source"]
        page_num = result["page_num"]
        text = result["text"]
        print(f"\n - From {file_source} (page {page_num}):\n{text}")

    return 0


# Use a SentenceTransformers model for embedding
def use_sentence_transformers_model_for_embedding(library_name, model_name):

    # Create a library and add some documents so we can do some vector embeddings
    print (f"\n > Creating a library...")
    library = Library().create_new_library(library_name)
    sample_files_path = Setup().load_sample_files()
    library.add_files(input_folder_path=os.path.join(sample_files_path, "SmallLibrary"))

    # Load the model
    print (f"\n > Loading model '{model_name}'")
    sbert_model = SentenceTransformer(model_name)

    # Create vector embeddings
    print (f"\n > Creating vector embeddings...")
    library.install_new_embedding(model=sbert_model, embedding_model_name=model_name,
                                  from_sentence_transformer=True, vector_db="faiss", batch_size=100)

    # Perform a query
    query_term = "salary"
    print (f"\n > Performing query for {query_term}...")

    query= Query(library=library,
                 embedding_model_name=model_name,
                 embedding_model=sbert_model,
                 from_sentence_transformer=True)

    query_results = query.semantic_query(query_term, result_count=3)
    print (f"Top 3 Results:")
    for i, result in enumerate(query_results): 
        file_source = result["file_source"]
        page_num = result["page_num"]
        text = result["text"]
        print(f"\n - From {file_source} (page {page_num}):\n{text}")

    return query_results


if __name__ == "__main__":

    use_llmware_hf_models_for_embedding()
    load_and_use_decoder_generative_model()
    override_generative_model_weights_with_custom_fine_tuned_model()
    use_transformers_model_for_embedding("test_transformers", "bert-base-cased")
    use_sentence_transformers_model_for_embedding("test_sentence_transformers", "all-distilroberta-v1")
