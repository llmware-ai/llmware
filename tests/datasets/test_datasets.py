import os
from llmware.dataset_tools import Datasets
from llmware.library import Library
from llmware.retrieval import Query
from llmware.parsers import Parser
from llmware.setup import Setup


def test_build_datasets():

    # Setup library
    library = Library().create_new_library("test_datasets")
    sample_files_path = Setup().load_sample_files()
    library.add_files(os.path.join(sample_files_path,"SmallLibrary"))
    library.generate_knowledge_graph()

    # build dataset
    ds = Datasets(library)

    #   basic dataset useful for industry domain adaptation for finetuning embedding models
    basic_embedding_ds = ds.build_text_ds(min_tokens=500, max_tokens=1000)
    assert basic_embedding_ds["testing_samples"] > 0

    #   simple self-supervised generative dataset- extracts text and splits into 'text' & 'completion'
    #   several generative "prompt_wrappers" are available - chat_gpt | alpaca | human_bot
    basic_generative_completion_ds = ds.build_gen_ds_targeted_text_completion(prompt_wrapper="alpaca")
    assert basic_generative_completion_ds["testing_samples"] > 0

    # generative self-supervised training sets created by pairing 'header_text' with 'text'
    xsum_generative_completion_ds = ds.build_gen_ds_headline_text_xsum(prompt_wrapper="human_bot")
    assert xsum_generative_completion_ds["testing_samples"] > 0
    topic_prompter_ds = ds.build_gen_ds_headline_topic_prompter(prompt_wrapper="chat_gpt")
    assert topic_prompter_ds["testing_samples"] > 0
    
    #  options:  filter a library by a key term as part of building the dataset
    filtered_ds = ds.build_text_ds(min_tokens=150,max_tokens=500, query="agreement", filter_dict={"master_index":1})
    assert filtered_ds["testing_samples"] > 0
    
    #   alternatively, pass a set of query results to create a dataset from those results only
    query_results = Query(library=library).query("salary")
    basic_embedding_ds=ds.build_text_ds(min_tokens=250,max_tokens=600, qr=query_results)
    assert basic_embedding_ds["testing_samples"] > 0
        
    # images with text dataset
    images_with_text_ds = ds.build_visual_ds_image_labels()
    assert images_with_text_ds["testing_samples"] > 0

    # last dataset -> do not test - likely to evaluate further and either change or remove
    # ds.build_gen_ds_paired_samples_top_block_extraction()

    library.delete_library()

    
def test_build_aws_transcribe_ds():

    # Setup library
    library = Library().create_new_library("aws_transcribe_ds")
    sample_files_path = Setup().load_sample_files()
    library.add_dialogs(os.path.join(sample_files_path,"AWS-Transcribe"))
    library.generate_knowledge_graph()

    ds = Datasets(library)

    generative_conversation_ds = ds.build_gen_dialog_ds(prompt_wrapper="human_bot",human_first=True)
    assert generative_conversation_ds["testing_samples"] > 0

    # generative model fine-tuning dataset build from llm prompt state history
    # supports 3 popular formats - alpaca, chatgpt, and 'human_bot'
    generative_curated_ds = ds.build_gen_ds_from_prompt_history(prompt_wrapper="alpaca")
    assert generative_curated_ds["batches"] > 0

    library.delete_library()
