
""" This example provides a basic framework to build a "Biz Bot" designed to integrate both 'RAG' source documents
and 'SQL' tables (e.g., CSV files), and interface using natural language with a chatbot UI.

    Models - this example uses 3 models, running locally

        -- bling-phi-3-gguf     -   core RAG question-answer model
        -- slim-sql-tool        -   fast local text-to-sql model
        -- jina-reranker-turbo  -   reranking model from Jina AI
            -- for more info on Jina AI model - see https://huggingface.co/jinaai/jina-reranker-v1-turbo-en

    Database - the SQL functionality will load a table into SQLite (no install required)

    Pre-reqs -

    1.  Streamlit - to run this example requires an install of Streamlit, e.g., `pip3 install streamlit`

        -- To execute the script, run from the command line with:  `streamlit run biz_bot.py`
        -- For more information on the Streamlit Chat UI, see
            https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps

    Sample Data -

        -- by default, at startup, the app will load a sample Employment Agreement document and a simple customer table

        -- RAG test question:  'what is the annual rate of the base salary?'
        -- SQL test question:  'which customer has the lowest annual spend?'

    2.  Add new documents or CSV files on the left side panel upload buttons.

    All components of the Biz Bot will be running locally, so the speed will be determined greatly by the
    CPU/GPU capacities and ** memory ** of your machine.  We would recommend at least 16 GB of RAM, and ideally 32 GB
    to run this example.

"""

import os

import streamlit as st
from llmware.resources import CustomTable
from llmware.models import ModelCatalog
from llmware.prompts import Prompt
from llmware.parsers import Parser
from llmware.configs import LLMWareConfig
from llmware.agents import LLMfx
from llmware.setup import Setup

#   keeps a running state of any csv tables that have been loaded in the session to avoid duplicated inserts
if "loaded_tables" not in st.session_state:
    st.session_state["loaded_tables"] = []


def build_table(db=None, table_name=None,load_fp=None,load_file=None):

    """ Simple example script to take a CSV or JSON/JSONL and create a DB Table.

    """

    if not table_name:
        return 0

    # build the table only once - if name already found, do not add to table
    if table_name in st.session_state["loaded_tables"]:
        return 0

    custom_table = CustomTable(db=db, table_name=table_name)
    analysis = custom_table.validate_csv(load_fp, load_file)
    print("update: analysis from validate_csv: ", analysis)

    if load_file.endswith(".csv"):
        output = custom_table.load_csv(load_fp, load_file)
    elif load_file.endswith(".jsonl") or load_file.endswith(".json"):
        output = custom_table.load_json(load_fp, load_file)
    else:
        print("file type not supported for db load")
        return -1

    print("update: output from loading file: ", output)

    sample_range = min(10, len(custom_table.rows))
    for x in range(0,sample_range):
        print("update: sample rows: ", x, custom_table.rows[x])

    #  stress the schema data type and remediate - use more samples for more accuracy
    updated_schema = custom_table.test_and_remediate_schema(samples=20, auto_remediate=True)

    print("update: updated schema: ", updated_schema)

    #   insert the rows in the DB
    custom_table.insert_rows()

    st.session_state["loaded_tables"].append(table_name)

    return len(custom_table.rows)


@st.cache_resource
def load_reranker_model():

    """ Loads the reranker model used in the RAG process to rank the semantic similarity between all of the
    parsed text chunks and the user query. """

    reranker_model = ModelCatalog().load_model("jina-reranker-turbo")
    return reranker_model


@st.cache_resource
def load_prompt_model():

    """ Loads the core RAG model used for fact-based question-answering against the source materials. """

    prompter = Prompt().load_model("bling-phi-3-gguf", temperature=0.0, sample=False)
    return prompter


@st.cache_resource
def load_agent_model():

    """ Loads the Text2SQL model used for querying the CSV table. """

    agent = LLMfx()
    agent.load_tool("sql", sample=False, get_logits=True, temperature=0.0)
    return agent


@st.cache_resource
def parse_file(fp, doc):

    """ Executes a parsing job of a newly uploaded file, and saves the parser out as a set of text chunks
    with metadata. """

    parser_output = Parser().parse_one(fp, doc, save_history=False)
    st.cache_resource.clear()
    return parser_output


def get_rag_response(prompt, parser_output, reranker_model, prompter):

    """ Executes a RAG response. """

    #   if the number of text chunks is small, then will skip the reranker
    if len(parser_output) > 3:
        output = reranker_model.inference(prompt, parser_output, top_n=10, relevance_threshold=0.25)
    else:
        output = []
        for entries in parser_output:
            entries.update({"rerank_score": 0.0})
            output.append(entries)

    use_top = 3
    if len(output) > use_top:
        output = output[0:use_top]

    #   create the source from the top 3 text chunks
    sources = prompter.add_source_query_results(output)

    #   run the inference on the model with the source automatically packaged and attached
    responses = prompter.prompt_with_source(prompt, prompt_name="default_with_context")

    #   execute post-inference fact and source checking
    source_check = prompter.evidence_check_sources(responses)
    numbers_check = prompter.evidence_check_numbers(responses)
    nf_check = prompter.classify_not_found_response(responses,parse_response=True,evidence_match=False,ask_the_model=False)

    bot_response = ""
    for i, resp in enumerate(responses):
        bot_response = resp['llm_response']

        print("bot response - llm_response raw - ", bot_response)

        add_sources = True

        if "not_found_classification" in nf_check[i]:

            if nf_check[i]["not_found_classification"]:
                add_sources = False
                bot_response += "\n\n" + ("The answer to the question was not found in the source "
                                          "passage attached - please check the source again, and/or "
                                          "try to ask the question in a different way.")

        if add_sources:
            numbers_output = ""
            if "fact_check" in numbers_check[i]:
                fc = numbers_check[i]["fact_check"]
                if isinstance(fc, list) and len(fc) > 0:

                    max_fact_count = 1
                    count = 0

                    for fc_entries in fc:

                        if count < max_fact_count:

                            if "text" in fc_entries:
                                numbers_output += "Text: " + fc_entries["text"] + "\n\n"
                            if "source" in fc_entries:
                                numbers_output += "Source: " + fc_entries["source"] + "\n\n"
                            if "page_num" in fc_entries:
                                numbers_output += "Page Num: " + fc_entries["page_num"] + "\n\n"
                            count += 1

                bot_response += "\n\n" + numbers_output

            source_output = ""
            if not numbers_output:
                if "source_review" in source_check[i]:
                    fc = source_check[i]["source_review"]
                    if isinstance(fc, list) and len(fc) > 0:
                        fc = fc[0]
                        if "text" in fc:
                            source_output += "Text: " + fc["text"] + "\n\n"
                        if "match_score" in fc:
                            source_output += "Match Score: " + str(fc["match_score"]) + "\n\n"
                        if "source" in fc:
                            source_output += "Source: " + fc["source"] + "\n\n"
                        if "page_num" in fc:
                            source_output += "Page Num: " + str(fc["page_num"]) + "\n\n"

                    bot_response += "\n\n" + source_output

    prompter.clear_source_materials()

    return bot_response


def get_sql_response(prompt, agent, db=None, table_name=None):

    """ Executes a Text-to-SQL inference, and then also queries the database and returns the database query result. """

    #   note: there is an optional magic word " #SHOW" at the end of a user query, which is stripped from the query
    #   before generating the SQL, but is then used by the UI to display the SQL command produced.

    show_sql = False
    bot_response = ""

    if prompt.endswith(" #SHOW"):
        show_sql = True
        prompt = prompt[:-(len(" #SHOW"))]

    model_response = agent.query_custom_table(prompt, db=db, table=table_name)

    # insert additional error checking / post-processing of output here
    error_handle = False

    try:
        sql_query = model_response["sql_query"]
        db_response = model_response["db_response"]

        if not show_sql:
            bot_response = db_response
        else:
            bot_response = f"Answer: {db_response}\n\nSQL Query: {sql_query}"
    except:
        error_handle = True
        sql_query = None
        db_response = None

    if error_handle or not sql_query or not db_response:
        bot_response = (f"Sorry I could not find an answer to your question.<br/>"
                        f"Here is the SQL query that was generated by your question: "
                        f"<br/>{sql_query}.<br/> If this missed the mark, please try asking "
                        f"the question again with a little more specificity.")

    return bot_response


def biz_bot_ui_app (db="postgres", table_name=None, fp=None,doc=None):

    st.title(f"Biz Bot")

    parser_output = None

    if os.path.exists(os.path.join(fp,doc)):
        if not parser_output:
            parser_output = Parser().parse_one(fp, doc, save_history=False)

    prompter = load_prompt_model()
    reranker_model = load_reranker_model()
    agent = load_agent_model()

    # initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    with st.sidebar:

        st.write("Biz Bot")
        model_type = st.selectbox("Pick your mode", ("RAG","SQL"), index=0)

        uploaded_doc = st.file_uploader("Upload Document")
        uploaded_table = st.file_uploader("Upload CSV")

        if uploaded_doc:
            fp = LLMWareConfig().get_llmware_path()
            doc = uploaded_doc.name
            f = open(os.path.join(fp,doc), "wb")
            f.write(uploaded_doc.getvalue())
            f.close()
            parser_output = parse_file(fp, doc)
            st.write(f"Document Parsed and Ready - {len(parser_output)}")

        if uploaded_table:
            fp = LLMWareConfig().get_llmware_path()
            tab = uploaded_table.name
            f = open(os.path.join(fp,tab),"wb")
            f.write(uploaded_table.getvalue())
            f.close()
            table_name = tab.split(".")[0]
            st.write("Building Table - ", tab, table_name)
            st.write(st.session_state['loaded_tables'])
            row_count = build_table(db=db, table_name=table_name, load_fp=fp, load_file=tab)
            st.write(f"Completed - Table - {table_name} - Rows - {row_count} - is Ready.")

    # accept user input
    prompt = st.chat_input("Say something")
    if prompt:

        with st.chat_message("user"):
            st.markdown(prompt)

        with (st.chat_message("assistant")):

            if model_type == "RAG":
                bot_response = get_rag_response(prompt,parser_output, reranker_model, prompter)
                st.markdown(bot_response)
            else:
                bot_response = get_sql_response(prompt, agent, db=db, table_name=table_name)
                st.markdown(bot_response)

        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": bot_response})

    return 0


if __name__ == "__main__":

    #   note: there is a hidden 'magic' command in the chatbot - if you add " #SHOW" at the end of your query,
    #   then it will display the SQL command that was generated (very useful for debugging)

    db = "sqlite"
    table_name = "customer_table_1"

    #   By default, the BizBot starts with a loaded document and CSV (which can then be changed directly in the UI)

    #   pull customer_table.csv sample file from the same repo as this example, or alternatively
    #   substitute your own csv to get started

    local_csv_path = "/your/local/path/to/csv/"
    build_table(db=db, table_name=table_name,load_fp=local_csv_path, load_file="customer_table.csv")

    #   get sample agreement to use as a starting point or feel free to substitute your own document

    sample_files_path = Setup().load_sample_files(over_write=False)
    fp = os.path.join(sample_files_path, "Agreements")
    fn = "Nike EXECUTIVE EMPLOYMENT AGREEMENT.pdf"

    biz_bot_ui_app(db=db, table_name=table_name,fp=fp, doc=fn)

    #   IMPORTANT NOTE:  to run this script, follow the streamlit formalism and run from the cli, e.g.,
    #   `streamlit run biz_bot.py`





