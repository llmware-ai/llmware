import marimo

__generated_with = "0.5.2"
app = marimo.App()


@app.cell
def __():
    import marimo as mo
    return mo,


@app.cell
def __(mo):
    mo.md("""     Fast Start Example #4 - RAG with Text Query

        This example shows a basic RAG recipe using text query combined with LLM prompt.

        We will show two different ways to achieve this basic recipe:

        -- Example 4A - this will integrate Library + Prompt - and is the most scalable general solution

        -- Example 4B - this will illustrate another capability of the Prompt class to add sources "inline"
         without necessarily a library in-place.  It is another useful tool when you want to be able to quickly
         pick up a document and start asking questions to it.

         Note: both of the examples are designed to achieve the same output.

    """)
    return


@app.cell
def __():
    import os
    import re
    from llmware.prompts import Prompt, HumanInTheLoop
    from llmware.setup import Setup
    from llmware.configs import LLMWareConfig
    from llmware.retrieval import Query
    from llmware.library import Library
    return (
        HumanInTheLoop,
        LLMWareConfig,
        Library,
        Prompt,
        Query,
        Setup,
        os,
        re,
    )


@app.cell
def __(mo):
    mo.md("""**Step 0:**  Select Model """)
    return


@app.cell
def __(LLMWareConfig):
    #   you can pick any model from the ModelCatalog
    #   we list a few representative good choices below

    LLMWareConfig().set_active_db("sqlite")

    example_models = ["llmware/bling-1b-0.1", "llmware/bling-tiny-llama-v0", "llmware/dragon-yi-6b-gguf"]

    #   to swap in a gpt-4 openai model - uncomment these two lines
    #   model_name = "gpt-4"
    #   os.environ["USER_MANAGED_OPENAI_API_KEY"] = "<insert-your-openai-key>"

    # use local cpu model
    model_name = example_models[0]
    return example_models, model_name


@app.cell
def __(mo):
    mo.md("""**Example #4a:**  Main general case to run a RAG workflow from a Library """)
    return


@app.cell
def __(Library, Setup, os):
    # Load the llmware sample files
    print (f"\n > Loading the llmware sample files...")
    sample_files_path_ = Setup().load_sample_files()
    contracts_path_ = os.path.join(sample_files_path_,"Agreements")

    contracts_lib = Library().create_new_library("example4_library")
    contracts_lib.add_files(contracts_path_)
    return contracts_lib, contracts_path_, sample_files_path_


@app.cell
def __(Query, contracts_lib, model_name):
    # questions that we want to ask each contract
    question_list_ = [{"topic": "executive employment agreement", "llm_query": "What are the names of the two parties?"},
                     {"topic": "base salary", "llm_query": "What is the executive's base salary?"},
                     {"topic": "governing law", "llm_query": "What is the governing law?"}]

    print (f"\n > Loading model {model_name}...")

    q = Query(contracts_lib)
    return q, question_list_


@app.cell
def __(q):
    # get a list of all of the unique documents in the library

    # doc id list
    doc_list = q.list_doc_id()
    print("update: document id list - ", doc_list)

    # filename list
    fn_list = q.list_doc_fn()
    print("update: filename list - ", fn_list)
    return doc_list, fn_list


@app.cell
def __(Prompt, doc_list, fn_list, model_name, q, question_list, re):
    verbose = False
    prompter_ = Prompt().load_model(model_name)

    for i, doc_id in enumerate(doc_list):

        print("\nAnalyzing contract: ", str(i+1), doc_id, fn_list[i])

        print("LLM Responses:")

        for question in question_list:

            query_topic = question["topic"]
            llm_question = question["llm_query"]

            doc_filter = {"doc_ID": [doc_id]}
            query_results = q.text_query_with_document_filter(query_topic,doc_filter,result_count=5,exact_mode=True)

            if verbose:
                # this will display the query results from the query above
                for j, qr in enumerate(query_results):
                    print("update: querying document - ", query_topic, j, doc_filter, qr)

            source = prompter_.add_source_query_results(query_results)

            #   *** this is the call to the llm with the source packaged in the context automatically ***
            responses = prompter_.prompt_with_source(llm_question, prompt_name="default_with_context", temperature=0.3)

            #   unpacking the results from the LLM
            for r, response in enumerate(responses):
                print("update: llm response -  ", llm_question, re.sub("[\n]"," ", response["llm_response"]).strip())

            # We're done with this contract, clear the source from the prompt
            prompter_.clear_source_materials()
    return (
        doc_filter,
        doc_id,
        i,
        j,
        llm_question,
        prompter_,
        qr,
        query_results,
        query_topic,
        question,
        r,
        response,
        responses,
        source,
        verbose,
    )


@app.cell
def __(HumanInTheLoop, LLMWareConfig, os, prompter_):
    #   Save jsonl report to jsonl to /prompt_history folder
    print("\nPrompt state saved at: ", os.path.join(LLMWareConfig.get_prompt_path(),prompter_.prompt_id))
    prompter_.save_state()

    #   Save csv report that includes the model, response, prompt, and evidence for human-in-the-loop review
    csv_output = HumanInTheLoop(prompter_).export_current_interaction_to_csv()
    print("\nCSV output saved at:  ", csv_output)
    return csv_output,


@app.cell
def __(mo):
    mo.md(""" **Example #4b:** Alternative implementation using prompt in-line capabilities without using a library """)
    return


@app.cell
def __(Prompt, Setup, model_name, os):
    # Load the llmware sample files
    print(f"\n > Loading the llmware sample files...")
    sample_files_path = Setup().load_sample_files()
    contracts_path = os.path.join(sample_files_path, "Agreements")

    # questions that we want to ask each contract
    question_list = [{"topic": "executive employment agreement", "llm_query": "What are the names of the two parties?"},
                     {"topic": "base salary", "llm_query": "What is the executive's base salary?"},
                     {"topic": "governing law", "llm_query": "What is the governing law?"}]

    print(f"\n > Loading model {model_name}...")

    prompter = Prompt().load_model(model_name)
    return contracts_path, prompter, question_list, sample_files_path


@app.cell
def __(contracts_path, os, prompter, question_list, re):
    _verbose = False

    for _i, _contract in enumerate(os.listdir(contracts_path)):

        # exclude potential mac os created file artifact in the samples folder path
        if _contract != ".DS_Store":

            print("\nAnalyzing contract: ", str(_i + 1), _contract)

            print("LLM Responses:")

            for _question in question_list:

                _query_topic = _question["topic"]
                _llm_question = _question["llm_query"]

                #   introducing "add_source_document"
                #   this will perform 'inline' parsing, text chunking and query filter on a document
                #   input is a file folder path, file name, and an optional query filter
                #   the source is automatically packaged into the prompt object

                _source = prompter.add_source_document(contracts_path,_contract,query=_query_topic)

                if _verbose:
                    print("update: document created source - ", _source)

                #   calling the LLM with 'source' information from the contract automatically packaged into the prompt
                _responses = prompter.prompt_with_source(_llm_question, prompt_name="default_with_context",
                                                        temperature=0.3)

                #   unpacking the LLM responses
                for _r, _response in enumerate(_responses):
                    print("update: llm response: ", _llm_question, re.sub("[\n]", " ",
                                                                         _response["llm_response"]).strip())

                # We're done with this contract, clear the source from the prompt
                prompter.clear_source_materials()
    return


if __name__ == "__main__":
    app.run()