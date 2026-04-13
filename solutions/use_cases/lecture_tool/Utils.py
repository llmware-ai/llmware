from llmware.library import Library
from llmware.retrieval import Query


ACCOUNT_NAME = 'lecture_tool'


"""
Creates a list of all libraries created with the application based on the
ACCOUNT_NAME.
"""
def get_stored_libraries():
    all_library_cards = Library().get_all_library_cards(account_name=ACCOUNT_NAME)

    library_list = []
    for card in all_library_cards:
        library_list.append(card['library_name'])

    return library_list


"""
Creates a list of unique filenames in a specified library.
"""
def get_stored_files(library_name):
    library = Library().load_library(library_name, account_name=ACCOUNT_NAME)

    file_list = []
    for library_info in Query(library).get_whole_library():
        if library_info['file_source'] not in file_list:
            file_list.append(library_info['file_source'])

    return file_list
