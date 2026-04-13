import marimo

__generated_with = "0.5.2"
app = marimo.App()


@app.cell
def __():
    import marimo as mo
    return mo,


@app.cell
def __(mo):
    mo.md(
    """ Fast Start Example #1 - Library - converting document files into an indexed knowledge collection.

        In this example, we will illustrate a basic recipe for completing the following steps:

          1. Create a library as a organizing construct for your knowledge-base
          2. Download sample files for a Fast Start - easy to 'swap out' and replace with your own files
          3. Use library.add_files method to automatically parse, text chunk and index the documents
          4. Run a basic text query against your new Library
    """)
    return


@app.cell
def __(mo):
    mo.md(f"\n**Step 0** - Import libraries, set database, initialize libraries, create sample folder")
    return


@app.cell
def __():
    import os
    from llmware.library import Library
    from llmware.retrieval import Query
    from llmware.setup import Setup
    from llmware.configs import LLMWareConfig
    return LLMWareConfig, Library, Query, Setup, os


@app.cell
def __(LLMWareConfig):
    #   optional - set the active DB to be used - by default, it is "mongo"
    #   if you are just getting started, and have not installed a separate db, select "sqlite"
    LLMWareConfig().set_active_db("sqlite")

    library_name = "example1_library"

    #   this is a list of document folders that will be pulled down by calling Setup()
    sample_folders = ["Agreements", "Invoices", "UN-Resolutions-500", "SmallLibrary", "FinDocs", "AgreementsLarge"]

    #   select one of the sample folders
    selected_folder = sample_folders[0]
    return library_name, sample_folders, selected_folder


@app.cell
def __(library_name, mo):
    mo.md(f"\n**Step 1** - creating library:  `{library_name}`")
    return


@app.cell
def __(Library, library_name):
    # create new library
    library = Library().create_new_library(library_name)
    return library,


@app.cell
def __(Setup):
    #   load the llmware sample files
    #   -- note: if you have used this example previously, UN-Resolutions-500 is new path
    #   -- to pull updated sample files, set: 'over_write=True'
    sample_files_path = Setup().load_sample_files(over_write=False)
    return sample_files_path,


@app.cell
def __(mo, sample_files_path):
    mo.md(f"\n**Step 2** - loading the llmware sample files and saving at: {sample_files_path}`")
    return


@app.cell
def __(os, sample_files_path, selected_folder):
    sample_folder = selected_folder
    #   note: to replace with your own documents, just point to a local folder path that has the documents
    ingestion_folder_path = os.path.join(sample_files_path, sample_folder)
    return ingestion_folder_path, sample_folder


@app.cell
def __(ingestion_folder_path, mo):
    mo.md(f"\n**Step 3** - parsing and indexing files from: {ingestion_folder_path}`")
    return


@app.cell
def __(ingestion_folder_path, library):
    #   add files is the key ingestion method - parses, text chunks and indexes all files in folder
    #       --will automatically route to correct parser based on file extension
    #       --supported file extensions:  .pdf, .pptx, .docx, .xlsx, .csv, .md, .txt, .json, .wav, and .zip, .jpg, .png
    parsing_output = library.add_files(ingestion_folder_path)
    return parsing_output,


@app.cell
def __(mo):
    mo.md(f"\n**Step 4** - completed parsing")
    return


@app.cell
def __(mo, parsing_output):
    mo.md(f"{parsing_output}`")
    return


@app.cell
def __(library):
    #   check the updated library card
    updated_library_card = library.get_library_card()
    doc_count = updated_library_card["documents"]
    block_count = updated_library_card["blocks"]
    return block_count, doc_count, updated_library_card


@app.cell
def __(mo):
    mo.md(f"\n **Step 5** - updated library card")
    return


@app.cell
def __(block_count, doc_count, mo, updated_library_card):
    mo.md(f"documents - {doc_count}, blocks - {block_count}, updated library card - {updated_library_card}")
    return


@app.cell
def __(library):
    #   check the main folder structure created for the library - check /images to find extracted images
    library_path = library.library_main_path
    return library_path,


@app.cell
def __(library_path, mo):
    mo.md(f"**Step 6** - library artifacts - including extracted images - saved at folder path - {library_path}")
    return


@app.cell
def __():
    #   use .add_files as many times as needed to build up your library, and/or create different libraries for
    #   different knowledge bases
    #   now, your library is ready to go and you can start to use the library for running queries
    #   if you are using the "Agreements" library, then a good easy 'hello world' query is "base salary"
    #   if you are using one of the other sample folders (or your own), then you should adjust the query
    #   queries are always created the same way, e.g., instantiate a Query object, and pass a library object
    #   --within the Query class, there are a variety of useful methods to run different types of queries
    test_query = "base salary"
    return test_query,


@app.cell
def __(mo, test_query):
    mo.md(f"**Step 7** - running a test query - {test_query}\n")
    return


@app.cell
def __(Query, library, test_query):
    query_results = Query(library).text_query(test_query, result_count=10)
    return query_results,


@app.cell
def __(query_results):
    for i, result in enumerate(query_results):

        #   note: each result is a dictionary with a wide range of useful keys
        #   -- we would encourage you to take some time to review each of the keys and the type of metadata available

        #   here are a few useful attributes
        text = result["text"]
        file_source = result["file_source"]
        page_number = result["page_num"]
        doc_id = result["doc_ID"]
        block_id = result["block_ID"]
        matches = result["matches"]

        #   -- if print to console is too verbose, then pick just a few keys for print
        print("query results: ", i, result)
    return (
        block_id,
        doc_id,
        file_source,
        i,
        matches,
        page_number,
        result,
        text,
    )


if __name__ == "__main__":
    app.run()