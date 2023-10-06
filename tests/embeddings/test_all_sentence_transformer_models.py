import os
import pytest 
import time

from llmware.library import Library
from llmware.embeddings import EmbeddingHandler
from llmware.exceptions import UnsupportedEmbeddingDatabaseException
from llmware.models import ModelCatalog
from llmware.retrieval import Query
from llmware.setup import Setup
from llmware.configs import LLMWareConfig
from llmware.resources import CloudBucketManager
from sentence_transformers import SentenceTransformer

import sys
sys.path.append(os.path.join(os.path.dirname(__file__),".."))
from utils import Logger

'''
This test downloads takes a long time and downloads many GB of models so it's "off" by default. Here's the output when it run on Sept 24:


+-------+---------------------------------------+-----------+---------------------------------------------------------+
|   Num | Model                                 |   Seconds | Top Hit                                                 |
+=======+=======================================+===========+=========================================================+
|     1 | all-MiniLM-L12-v1                     |     12.33 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 5)   |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|     2 | all-MiniLM-L12-v2                     |      9.2  | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 5)   |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|     3 | all-MiniLM-L6-v1                      |      9.27 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 3)   |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|     4 | all-MiniLM-L6-v2                      |      9.24 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 5)   |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|     5 | all-distilroberta-v1                  |     13.57 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 4)   |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|     6 | all-mpnet-base-v1                     |     17.13 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 11)  |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|     7 | all-mpnet-base-v2                     |     15.92 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 11)  |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|     8 | all-roberta-large-v1                  |     32.43 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 4)   |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|     9 | average_word_embeddings_glove.6B.300d |      8.56 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 5)   |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|    10 | average_word_embeddings_komninos      |      8.3  | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 4)   |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|    11 | gtr-t5-base                           |     15.67 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 1)   |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|    12 | gtr-t5-large                          |     30.3  | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 11)  |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|    13 | gtr-t5-xl                             |     88.93 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 3)   |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|    14 | gtr-t5-xxl                            |    604.63 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 11)  |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|    15 | msmarco-bert-base-dot-v5              |     18.37 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 3)   |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|    16 | msmarco-distilbert-base-tas-b         |     13.7  | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 3)   |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|    17 | msmarco-distilbert-dot-v5             |     11.93 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 3)   |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|    18 | multi-qa-MiniLM-L6-cos-v1             |     10.27 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 3)   |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|    19 | multi-qa-MiniLM-L6-dot-v1             |      9.72 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 10)  |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|    20 | multi-qa-distilbert-cos-v1            |     11.97 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 11)  |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|    21 | multi-qa-distilbert-dot-v1            |     11.93 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 10)  |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|    22 | multi-qa-mpnet-base-cos-v1            |     18.19 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 3)   |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|    23 | multi-qa-mpnet-base-dot-v1            |     17.04 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 3)   |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|    24 | paraphrase-MiniLM-L12-v2              |     10.24 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 5)   |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|    25 | paraphrase-MiniLM-L3-v2               |      8.24 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 10)  |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|    26 | paraphrase-MiniLM-L6-v2               |      8.27 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 5)   |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|    27 | paraphrase-TinyBERT-L6-v2             |     10.02 | Eos License Agreement for Copyrighted Music.pdf(page 2) |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|    28 | paraphrase-albert-small-v2            |     11.19 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 5)   |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|    29 | paraphrase-distilroberta-base-v2      |     12.21 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 5)   |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|    30 | paraphrase-mpnet-base-v2              |     16.56 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 3)   |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|    31 | paraphrase-multilingual-MiniLM-L12-v2 |     11.24 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 5)   |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|    32 | paraphrase-multilingual-mpnet-base-v2 |     14.04 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 5)   |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|    33 | sentence-t5-base                      |     13.49 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 3)   |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|    34 | sentence-t5-large                     |     22.91 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 11)  |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|    35 | sentence-t5-xl                        |     58.86 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 11)  |
+-------+---------------------------------------+-----------+---------------------------------------------------------+
|    36 | sentence-t5-xxl                       |    290.67 | Amphitrite EXECUTIVE EMPLOYMENT AGREEMENT.pdf(page 11)  |
+-------+---------------------------------------+-----------+---------------------------------------------------------+

To run this test, remove "off_" from the method name.
'''

def off_test_all_embedding_models():

    # This model list was generated by here https://www.sbert.net/docs/pretrained_models.html and selecting the "All Models" switch
    sentence_transformer_models = [
        'all-MiniLM-L12-v1',
        'all-MiniLM-L12-v2',
        'all-MiniLM-L6-v1',
        'all-MiniLM-L6-v2',
        'all-distilroberta-v1',
        'all-mpnet-base-v1',
        'all-mpnet-base-v2',
        'all-roberta-large-v1',
        'average_word_embeddings_glove.6B.300d',
        'average_word_embeddings_komninos',
        #'distiluse-base-multilingual-cased-v1', See: https://github.com/aibloks/llmware/issues/57
        #'distiluse-base-multilingual-cased-v2', See: https://github.com/aibloks/llmware/issues/57
        'gtr-t5-base',
        'gtr-t5-large',
        'gtr-t5-xl',
        'gtr-t5-xxl',
        'msmarco-bert-base-dot-v5',
        'msmarco-distilbert-base-tas-b',
        'msmarco-distilbert-dot-v5',
        'multi-qa-MiniLM-L6-cos-v1',
        'multi-qa-MiniLM-L6-dot-v1',
        'multi-qa-distilbert-cos-v1',
        'multi-qa-distilbert-dot-v1',
        'multi-qa-mpnet-base-cos-v1',
        'multi-qa-mpnet-base-dot-v1',
        'paraphrase-MiniLM-L12-v2',
        'paraphrase-MiniLM-L3-v2',
        'paraphrase-MiniLM-L6-v2',
        'paraphrase-TinyBERT-L6-v2',
        'paraphrase-albert-small-v2',
        'paraphrase-distilroberta-base-v2',
        'paraphrase-mpnet-base-v2',
        'paraphrase-multilingual-MiniLM-L12-v2',
        'paraphrase-multilingual-mpnet-base-v2',
        'sentence-t5-base',
        'sentence-t5-large',
        'sentence-t5-xl',
        'sentence-t5-xxl'
    ]

    Logger().log("\ntest_all_sentence_transformer_models()")
    os.environ["TOKENIZERS_PARALLELISM"] = "false" # This just disables a warning that gets shown when pytest forks the process
    
    output_table_headers = ['Num','Model','Seconds','Top Hit']
    output_table_data = []
    
    # Create our small library
    Logger().log("Creating the test library...")
    library = Library().create_new_library("test_sentence_transformer_models")
    sample_files_path = Setup().load_sample_files()
    library.add_files(os.path.join(sample_files_path,"SmallLibrary"))

    for i, model_name in enumerate(sentence_transformer_models):
        if model_name not in ["model-to-skip"]:  # Easy way to quickly ignore some models if necessary
            Logger().log("Processing " + model_name + " ...")
            # Create the embedding
            start_time = time.time()
            model = SentenceTransformer(model_name)
            embedding_summary = library.install_new_embedding(from_sentence_transformer=True, embedding_model_name=model_name, vector_db="milvus", model=model)

            # Do a query
            query = "wages"
            query_obj =  Query(library,from_sentence_transformer=True, embedding_model=model, embedding_model_name =model_name)
            query_results = query_obj.semantic_query(query, result_count=5)
            answer_time = round(time.time()-start_time, 2)
            if not query_results["results"] or not query_results["results"][0]:
                top_hit = "No results found!"
            else:
                top_result = query_results["results"][0]
                top_hit = top_result["file_source"] + "(page " + str(top_result["page_num"]) + ")"

            EmbeddingHandler(library).delete_index(embedding_db="milvus", model=query_obj.embedding_model)
            
            # Capture the output data
            output_row = [i+1,model_name,answer_time,top_hit]
            output_table_data.append(output_row)
        else:
            output_row = [i+1,model_name,"NA", "NA(Skipped)"]
            output_table_data.append(output_row)
    
    Logger().log_table(output_table_headers,output_table_data)    
    library.delete_library(confirm_delete=True)
