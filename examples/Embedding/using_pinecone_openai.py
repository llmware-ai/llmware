'''This embedding example shows how you can use llmware in combination with OpenAI embedding models to create
a library that you can query semantically.

This example script can be easily extended towards RAG. You can, for exmaple, create a function
that reveices the result from the query as context for a LLM to generate an answer.
'''
import os
import logging


from llmware.library import Library
from llmware.retrieval import Query
from llmware.setup import Setup


logging.basicConfig(level = logging.INFO)
logger = logging.getLogger('llmware-pinecone-openai')


'''Change the values below to your API keys, and the cloud and region you want to use. If you want to use the
bash script, then you have to comment out the following code lines.

See the Pinecone documentation for details on available cloud and region options. During testing, we used
'aws' for cloud and 'us-west-2' for region.
'''
os.environ['USER_MANAGED_PINECONE_API_KEY'] = ''
os.environ['USER_MANAGED_PINECONE_CLOUD'] = ''
os.environ['USER_MANAGED_PINECONE_REGION'] = ''

os.environ['USER_MANAGED_OPENAI_API_KEY'] = ''



def set_up_api_keys(
    pinecone_api_key=os.getenv('USER_MANAGED_PINECONE_API_KEY', None),
    pinecone_cloud=os.getenv('USER_MANAGED_PINECONE_CLOUD', None),
    pinecone_region=os.getenv('USER_MANAGED_PINECONE_REGION', None),
    openai_api_key=os.getenv('USER_MANAGED_OPENAI_API_KEY', None)):
    '''This function sets the API keys for Pinecone and OpenAI, they have to be set!
    '''
    logger.info('Setting up Pinecone and OpenAI API keys')

    if pinecone_api_key in [None, '']:
        raise ValueError(f'You need to set the pinecone API key, got {pinecone_api_key}')

    if pinecone_cloud in [None, '']:
        raise ValueError(f'You need to set the pinecone cloud, got {pinecone_environment}')

    if pinecone_region in [None, '']:
        raise ValueError(f'You need to set the pinecone cloud, got {pinecone_region}')

    if openai_api_key in [None, '']:
        raise ValueError(f'You need to set the OpenAI API key, got {openai_api_key}')


    os.environ.setdefault('USER_MANAGED_PINECONE_API_KEY', pinecone_api_key)
    os.environ.setdefault('USER_MANAGED_PINECONE_CLOUD', pinecone_cloud)
    os.environ.setdefault('USER_MANAGED_PINECONE_REGION', pinecone_region)

    os.environ.setdefault('USER_MANAGED_OPENAI_API_KEY', openai_api_key)
    

def set_up_agreements():
    '''This function makes sure that the sample files are loaded, and returns the path the Agreements
    folter. We need the path to the agreements folder for the ``Library`` object.

    If you have your own data, simply exchange this function with another one that returns a path
    to you sample files.
    '''
    logger.info('Setting up Aggreements')

    sample_files_path = Setup().load_sample_files()
    return os.path.join(sample_files_path, "Agreements")


def set_up_library(
    input_folder_path,
    library_name='example_pinecone_openai'):
    '''This function creates the library with name ``library_name`` from ``directory``.
    '''
    logger.info(f'Setting up library with name {library_name} from directory {input_folder_path}')

    library = Library().create_new_library(library_name)
    library.add_files(input_folder_path=input_folder_path)
    return library


def set_up_embeddings(
    library,
    embedding_model='text-embedding-ada-002'):
    '''This function sets up the embeddings in ``library`` with the model ``embedding_model``.

    If you bring your own data and this data contains text and images, than you need to change ``embedding_model``
    to one that can process both simultanously.
    '''
    logger.info(f'Setting up embeddings in library {library.library_name} with model {embedding_model}')

    library.install_new_embedding(embedding_model_name=embedding_model, vector_db="pinecone")
    return library


def query_library(
    library,
    semantic_query='Salary'):
    '''This function executes the semantic query ``query`` on ``library``.

    If you want to query for something else, simply overwrite ``semantic_query``.
    '''
    query = Query(library)
    query_results = query.semantic_query(query=semantic_query, result_count=10, results_only=True)

    for idx, query_result in enumerate(query_results):
        # each query result is a dictionary with many useful keys
        text = query_result['text']
        file_source = query_result['file_source']
        page_num = query_result['page_num']
        distance = query_result['distance']

        # We truncate the text because we want to only show a peak.
        if len(text) > 125:  text = f'{text[0:125]} ...'

        logger.info(f'{idx} query result: {distance} distance '\
                    f'from file {file_source} and page number {page_num}, '\
                    f'here is sample text:\n{text}')

    return query_results


def main():
    '''This function first sets the environment variables for OpenAI and pinecone. Then, it sets up the example data,
    which in this case are the Agreements we provide as part of our sample data. Next, it creates a library with the
    content of the Agreements before it embedds the content. Finally, it performs a sematnic query on the library.
    '''
    set_up_api_keys()

    path_agreements = set_up_agreements()

    library = set_up_library(input_folder_path=path_agreements)

    library = set_up_embeddings(library=library)

    query_library(library=library)


if __name__ == '__main__':
    main()
