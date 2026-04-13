from llmware.library import Library
from llmware.retrieval import Query

import streamlit as st

import os
import sys

sys.path.insert(0, os.getcwd())

from Utils import get_stored_files, get_stored_libraries

ACCOUNT_NAME = 'lecture_tool'


#
# Accesses transcription by concatenating text from each block corresponding to
# the specified filename in the specified library.
#
@st.cache_data(show_spinner=False)
def get_transcript(library_name, filename):
    library = Library().load_library(library_name, account_name=ACCOUNT_NAME)
    print('\nupdate: library card - ', library.get_library_card())

    query = Query(library)

    text = ''
    for result in query.get_whole_library():
        if result['file_source'] == filename:
            text += result['text_search']

    return text


#
# Main block for GUI logic.
#
if __name__ == '__main__':
    st.title('View your transcripts')

    st.write('### Prompt info')

    library_name = st.selectbox(
        'Select the library:',
        tuple(get_stored_libraries())
    )

    if library_name:
        filename = st.selectbox(
            'Select the file:',
            tuple(get_stored_files(library_name))
        )

    if (st.button('View')):
        with st.spinner('Loading transcript... don\'t leave this page!'):
            response = get_transcript(library_name, filename)
            
            st.write('### Transcript')
            st.write(response)
