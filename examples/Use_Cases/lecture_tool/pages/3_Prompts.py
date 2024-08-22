from llmware.gguf_configs import GGUFConfigs
from llmware.library import Library
from llmware.prompts import Prompt
from llmware.retrieval import Query
from llmware.models import ModelCatalog

import streamlit as st

import os
import sys

sys.path.insert(0, os.getcwd())

from Utils import get_stored_files, get_stored_libraries

GENERAL_PURPOSE_MODEL = 'phi-3-gguf'
RAG_MODEL = 'bling-phi-3-gguf'
RERANKER_MODEL = 'jina-reranker-turbo'

ACCOUNT_NAME = 'lecture_tool'


#
# Calls the GENERAL_PURPOSE_MODEL defined above on the specified question.
#
@st.cache_data(show_spinner=False)
def prompt_general_question(question):
    # Set limit on output length
    GGUFConfigs().set_config("max_output_tokens", 1000)

    # Load in appropriate model
    prompter = Prompt().load_model(GENERAL_PURPOSE_MODEL, max_output=999)

    # Prompt the model with the question
    print('\nupdate: performing prompt')
    response = prompter.prompt_main(question)
    print('\nupdate: llm response - ', response)

    return response['llm_response']


#
# Calls the RAG_MODEL defined above to answer questions about lecture content.
#
# Accesses the library_name specified to pass either the entire library or a
# specified file from the library as source for reranking.
#
# RERANKER_MODEL defined above generates a list of the most relevant text blocks
# based on the question (prompt) with semantic reranking.

# These are passed as source to the RAG_MODEL for inference along with the
# question (prompt).
#
@st.cache_data(show_spinner=False)
def prompt_question_about_content_with_reranking(question, library_name, filename, topic=None):
    # Load in appropriate library
    library = Library().load_library(library_name, account_name=ACCOUNT_NAME)
    print('\nupdate: library card - ', library.get_library_card())

    # Create Query object
    query = Query(library)

    # Load in appropriate models
    rag_prompter = Prompt().load_model(RAG_MODEL, temperature=0.0, sample=False)
    reranker_model = ModelCatalog().load_model(RERANKER_MODEL, temperature=0.0, sample=False)

    # Access appropriate text blocks if all files are to be selected
    if filename == 'Select all files':
        print('\nupdate: all files selected')

        # Access entire library since no topic is specified
        if topic is None or topic == '':
            print('\nupdate: no topic provided, adding entire library as source')
            query_results = query.get_whole_library()

            # Change key in query results for compatibility with RAG call
            for result in query_results:
                result['text'] = result['text_search']
                del result['text_search']

            print('\nupdate: correct library chunks - ', query_results)
        # Access limited blocks from library based on topic specified
        else:
            # Perform text_query with the topic
            print('\nupdate: topic provided, performing text query for topic')
            query_results = query.text_query(topic)
            print('\nupdate: topic chunks - ', query_results)
    # Access appropriate text chunks if a specific file is selected
    else:
        print('\nupdate: file selected - ', filename)

        # Access all blocks for the specified file since no topic is specified
        if topic is None or topic == '':
            print('\nupdate: no topic provided, adding entire library as source')

            # Filter out only the blocks that correspond to the desired file
            query_results = query.apply_custom_filter(query.get_whole_library(), {'file_source': filename})

            # Change key in query results for compatibility with RAG call
            for result in query_results:
                result['text'] = result['text_search']
                del result['text_search']

            print('\nupdate: correct library chunks - ', query_results)
        # Access limited blocks from library based on topic and file specified
        else:
            # Perform a text query for the topic, then filter based on filename
            print('\nupdate: topic provided, performing text query for topic')
            query_results = query.apply_custom_filter(query.text_query(topic), {'file_source': filename})
            print('\nupdate: topic chunks - ', query_results)

    if len(query_results) == 0:
        print('\nupdate: sources are empty')
        return 'No result found. Please check to ensure your topic and file are accurate.', None, None
    
    # Perform semantic reranking to get relevant text blocks
    print('\nupdate: performing semantic ranking')
    reranker_output = reranker_model.inference(question, query_results, top_n=10, relevance_threshold=0.2)

    # Use only the 3 most relevant blocks if more are returned from rereanking
    use_top = 3
    if len(reranker_output) > use_top:
        reranker_output = reranker_output[:use_top]
    
    print('\nupdate: reranker output - ')
    for i, source in enumerate(reranker_output):
        print(i, ' - ', source)

    # Pass relevant blocks from reranking as source for RAG call
    sources = rag_prompter.add_source_query_results(reranker_output)
    print('\nupdate: sources - ', sources)

    # Perform RAG call with the question
    print('\nupdate: performing prompt')
    response = rag_prompter.prompt_with_source(question)

    # Store metadata about the RAG call for later use
    stats = rag_prompter.evidence_comparison_stats(response)
    ev_source = rag_prompter.evidence_check_sources(response)
    
    # Output LLM response
    for i, resp in enumerate(response):
        print('\nupdate: llm response - ', resp)
        print('\nupdate: compare with evidence - ', stats[i]['comparison_stats'])
        print('\nupdate: sources - ', ev_source[i]['source_review'])

    # Clear the source so the next call does not reuse previous source
    rag_prompter.clear_source_materials()

    source_file = response[0]['source_review'][0]['source'] if 'source_review' in response[0] and len(response[0]['source_review']) > 0 else None
    return response[0]['llm_response'], response[0]['evidence'], source_file


#
# Main block for GUI logic.
#
if __name__ == '__main__':
    st.title('Ask questions about lecture content')

    st.write('### Question info')

    question_type = st.selectbox(
        'Select the type of question:',
        ('Question about Content', 'General Question')
    )

    question = st.text_input('Enter your question:')

    if question_type == 'Question about Content':
        st.write('### Prompt info')

        topic = st.text_input('Optionally enter a topic:')

        library_name = st.selectbox(
            'Select the library:',
            tuple(get_stored_libraries())
        )

        if library_name:
            filename = st.selectbox(
                'Select the file:',
                tuple(['Select all files'] + get_stored_files(library_name))
            )

    if st.button('Prompt'):
        if question_type == 'General Question':
            with st.spinner('Processing request... don\'t leave this page!'):
                response = prompt_general_question(question)

                st.write('### Response')
                st.write(response)
        elif question_type == 'Question about Content':
            with st.spinner('Processing request... don\'t leave this page!'):
                response, evidence, source = prompt_question_about_content_with_reranking(question, library_name, filename, topic)
        
                st.write('### Response')
                st.write(response)

                if evidence:
                    st.write('### Evidence')
                    st.write('"' + evidence + '"')

                if source:
                    st.write('### File source')
                    st.write(source)
