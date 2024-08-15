from llmware.library import Library

import streamlit as st

import os
import sys

sys.path.insert(0, os.getcwd())

from Utils import get_stored_libraries


ACCOUNT_NAME = 'lecture_tool'


#
# Creates an llmware Library.
#
def create_library(library_name):
    Library().create_new_library(library_name, account_name=ACCOUNT_NAME)
    print('\nupdate: library created - ', library_name)


#
# Deletes an existing library if it exists.
#
def delete_library(library_name):
    card = Library().check_if_library_exists(library_name, account_name=ACCOUNT_NAME)

    if card:
        Library().delete_library(library_name, confirm_delete=True, account_name=ACCOUNT_NAME)
        print('\nupdate: delete library - ', library_name)
    else:
        print('\nupdate: library does not exist - ', library_name)


#
# Main block for GUI logic.
#
if __name__ == '__main__':
    st.title('Manage your lecture libraries')

    st.write('### Delete library/libraries')

    stored_libraries = get_stored_libraries()
    library_names = st.multiselect(
        'Select library/libraries to delete:',
        stored_libraries,
        max_selections=len(stored_libraries)
    )

    if st.button('Delete'):
        for library_name in library_names:
            delete_library(library_name)

            st.success(f'Successfully deleted {library_name}')

    st.write('### Create library')

    library_name = st.text_input('Enter library name to create')

    if st.button('Create'):
        if library_name:
            create_library(library_name)

            st.success(f'Successfully created {library_name}')
