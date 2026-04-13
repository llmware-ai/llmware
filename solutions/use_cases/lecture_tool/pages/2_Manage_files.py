from llmware.parsers import Parser
from llmware.library import Library

import streamlit as st

import os
import sys

sys.path.insert(0, os.getcwd())

from Utils import get_stored_libraries


SAVED_FILES_WD = os.path.join(os.getcwd(), 'saved_files')
ACCOUNT_NAME = 'lecture_tool'


#
# Deletes existing temporary files in saved_files directory.
#
def delete_all_saved_files():
    for file in os.listdir(SAVED_FILES_WD):
        os.remove(os.path.join(SAVED_FILES_WD, file))
        print('\nupdate: deleted temporary file - ', file)


#
# Uses Parser class to transcribe audio files uploaded and stores the output to
# the specified library.
#
def parse_lecture_file_and_store(filename, library_name):
    library = Library().load_library(library_name, account_name=ACCOUNT_NAME)

    parser_output = Parser(chunk_size=400, max_chunk_size=600, library=library).parse_voice(SAVED_FILES_WD, real_time_progress=True, copy_to_library=True)
    print('\nupdate: parser output - ', parser_output)

    print('\nupdate: library card - ', library.get_library_card())

    os.remove(os.path.join(SAVED_FILES_WD, filename))
    print('\nupdate: deleted temporary file - ', filename)


#
# Main block for GUI logic.
#
if __name__ == '__main__':
    st.title('Manage your lecture files')

    st.write('### Select library')

    stored_libraries = get_stored_libraries()
    library_name = st.selectbox(
        'Select library to manage files:',
        stored_libraries
    )

    st.write('### Add file(s)')

    files = st.file_uploader('Upload audio file(s)', type=['wav', 'mp3'], accept_multiple_files=True)

    if st.button('Upload'):
        delete_all_saved_files()

        for file in files:
            if file is not None:
                with open(os.path.join(SAVED_FILES_WD, file.name), 'wb') as f:
                    f.write(file.getbuffer())
                    print('\nupdate: added file to temporary storage - ', file.name)

                with st.spinner(f'Processing file {file.name}... don\'t leave this page!'):
                    parse_lecture_file_and_store(file.name, library_name)

                st.success(f'Successfully stored {file.name}')
