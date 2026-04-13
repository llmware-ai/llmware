
""" USING-LLM-FOR-TABLE-READING Recipes - this example consists of 3 recipes that illustrate the building blocks
of using locally-deployed small specialized language models for table question-answering with complex financial
and business documents.

    Note: this is a *** leading-edge *** set of recipes - it won't always work perfectly out of the box, and generally
    will require some tinkering with the pre-processing and post-processing and strategies at each step to
    improve accuracy.

    LLMs used:
        -- table reading:
            -- dragon-qwen2-7b-gguf
            -- dragon-yi-9b-gguf

        -- semantic reranker: jina-reranker-turbo (example 3)

    The recipes build on each other:

    Example 1 - basic recipe for using a LLM to answer a question based on a table text passage

    Example 2 - integrates parsing - parses a 10K document - extracts key tables - and then asks questions
                directly against the parsed, extracted tables (assumes we know the right questions to ask
                each table.

    Example 3 - integrates semantic similarity - parses and extracts tables from 10K, applies a semantic reranker
                to identify the table with the highest semantic similarity to our question, and then 'chooses'
                that table, and then runs the inference with the question and the highest ranked table.
    """

import os
import re
from llmware.models import ModelCatalog
from llmware.parsers import Parser
from llmware.setup import Setup
from llmware.util import Utilities


def example1_getting_started (model_name="dragon-qwen-7b-gguf"):

    """ Basic recipe for running an inference to read a table. """

    #   sample table text with \t separators between items

    text = ("\t2022 12/31/22\t2021 12/31/21\t2020 12/31/20\t2019 12/31/19 NET SALES OR REVENUES"
            "\t81,462\t53,823\t31,536\t24,578 Cost of Goods Sold (Excl Depreciation)\t57,066\t37,306\t22,584\t18,402 "
            "Depreciation, Depletion And Amortization\t3,543\t2,911\t2,322\t2,107 Depreciation\t2,655\t2,146\t1,802\t1,298 "
            "Amortization of Intangibles\t888\t51\t51\t44Amortization of Deferred Charges\t--\t714\t469\t765 GROSS "
            "INCOME\t20,853\t13,606\t6,630\t4,069 Selling, General & Admin Expenses\t7,021\t7,110\t4,636\t3,989 "
            "Research and Development Expense\t3,075\t2,593\t1,491\t1,343OPERATING INCOME\t13,832\t6,496\t1,994\t80 "
            "Extraordinary Charge - Pretax\t(228)\t(101)\t0\t(196) Non-Operating Interest Income\t297\t56\t30\t44 "
            "Other Income/Expenses - Net\t(15)\t263\t(122)\t92 Interest Expense On Debt\t167\t424\t796\t716 Interest "
            "Capitalized\t0\t53\t48\t31 PRETAX INCOME\t13,719\t6,343\t1,154\t(665) Income "
            "Taxes\t(1,132)\t(699)\t(292)\t(110) Current Domestic Income Tax\t62\t9\t4\t5 Current Foreign Income "
            "Tax\t1,266\t839\t248\t86Deferred Domestic Income Tax\t27\t0\t0\t(4) Deferred Foreign Income "
            "Tax\t(223)\t(149)\t40\t23 Minority Interest\t4\t120\t172\t95 NET INCOME BEFORE EXTRA ITEMS/PREFERRED "
            "DIVIDENDS\t12,583\t5,524\t690\t(870) NET INCOME USED TO CALCULATE BASIC EARNINGS PER "
            "SHARE\t12,583\t5,524\t690\t(870) Shares used in computing earnings per share - "
            "Fully Diluted\t3,475\t3,387\t3,249\t2,661Earning per Common Share - "
            "Basic\t4.02\t1.87\t0.25\t(0.33)Earning per Common Share - Fully Diluted\t3.62\t1.63\t0.21\t(0.33)() = "
            "Negative Values In U.S. Dollars Values are displayed in Millions except for earnings per share "
            "and where noted")

    questions = ["What is the pretax income in 2022?",
                 "What is the pretax income in 2021?",
                 "What is the amount of depreciation in 2020?",
                 "What is the fully diluted earnings per share in 2022?",
                 "What is the amount of dividends in 2021 and 2022?",
                 "What is the SG&A expense in 2022?",
                 "What were revenues in 2019?"]

    model = ModelCatalog().load_model(model_name, temperature=0.0, sample=False)

    for question in questions:
        print("question: ", question)
        response = model.inference(question, add_context=text)
        print("response: ", response)

    return True


def example2_parse_tables_and_ask_questions(model_name="dragon-qwen-7b-gguf"):

    """ Parse a 10K, extract key tables, and then ask specific questions to specific tables. """

    sample_files = Setup().load_sample_files()
    folder = "FinDocs"
    fp = os.path.join(sample_files, folder)
    fn = "Amazon-2021-Annual-Report.pdf"

    #   table_grid = True will provide a HTML representation of the table
    #   table_grid = False will provide a simpler /t and /n separators in representing the table

    parser_output = Parser(table_grid=False).parse_one_pdf(fp,fn)

    tables = []
    for i, chunks in enumerate(parser_output):
        if chunks["content_type"] == "table":
            print("text chunks: ", i, chunks)
            tables.append(chunks["table"])

    questions_by_table = [
        ["What is the amount of owned square footage of office space in North America?",
         "How many international stores?"
         ],

        ["What was the amount of cash at the end of 2020?",
         "What was the amount of cash at the end of 2021?",
         "What was net income in 2020?",
         "What was stock compensation in 2021?",
         "What was the amount of net increase in cash in 2020?"
         ],

        ["What were total net sales in 2021?"],

        ["What is the balance amount on January 1, 2019?"]

    ]

    model = ModelCatalog().load_model(model_name, temperature=0.0, sample=False)

    for t, table in enumerate(tables):

        print("\nEvaluating table: ", t, table)

        for q, question in enumerate(questions_by_table[t]):

            print("\nQuestion: ", q, question)
            response = model.inference(question, add_context=table)
            print("answer: ", response)

    return True


def example3_table_reading_e2e(model_name="dragon-qwen-7b-gguf"):

    """ Will parse, extract tables, apply semantic reranking to find the best fit table, and then ask the
    key question only to that table. """

    """ Parse a 10K, extract key tables, and then ask specific questions to specific tables. """

    question = "What was the amount of cash at the end of 2020?"

    #   Step 1 - parse and extract the tables from 10K

    sample_files = Setup().load_sample_files()
    folder = "FinDocs"
    fp = os.path.join(sample_files, folder)
    fn = "Amazon-2021-Annual-Report.pdf"

    #   table_grid = True will provide a HTML representation of the table
    #   table_grid = False will provide a simpler /t and /n separators in representing the table

    parser_output = Parser(table_grid=False).parse_one_pdf(fp, fn)

    tables = []
    print(f"\nStep 1 - parsing output - {fn} - created {len(parser_output)} text chunks total.")

    for i, chunks in enumerate(parser_output):
        if chunks["content_type"] == "table":
            print("tables found: ", i, chunks)

            if len(chunks["table"]) > 100:
                text_snippet = str(chunks["table"][0:100])
            else:
                text_snippet = chunks["table"]

            #  optional / clean up the text snippet for display on screen
            text_snippet = re.sub(r"[\n\r\t]","", text_snippet)

            tables.append({"text":chunks["table"],
                           "page_num": chunks["master_index"],
                           "file_source": chunks["file_source"],
                           "text_snippet": text_snippet})

    #   Step 2 - apply semantic ranking to compare the question with the extracted tables to find the
    #   table most likely to provide the answer

    print(f"\nStep 2 - select the extracted table most likely to be able to answer the question.")

    print("--option 1 - simple text search option (illustrative)")
    exact_key = "CASH EQUIVALENTS"
    results = Utilities().fast_search_dicts(exact_key,tables)
    for i, res in enumerate(results):
        print("text search results: ", i, exact_key,res)

    #   could use as a substitute below
    top_result = results[0]

    print(f"\n--option 2 - semantic similarity ranking (selected method)")

    reranker_model = ModelCatalog().load_model("jina-reranker-turbo")
    output = reranker_model.inference(question, tables)

    for i, ranking in enumerate(output):

        if i==0:
            print("TOP TABLE - ", i, ranking["rerank_score"], ranking["text_snippet"])
        else:
            print(i, ranking["rerank_score"], ranking["text_snippet"])

    top_table = output[0]

    print("\nTOP TABLE SOURCE: ", top_table["text"])

    #   Step 3 - run the query against the table to get the answer

    print(f"\nStep 3 - loading dragon model to answer the question using the 'top table' found")

    model = ModelCatalog().load_model(model_name, temperature=0.0, sample=False)

    print("question: ", question)
    response = model.inference(question, add_context=top_table["text"])
    print("response: ", response)
    print("source: ", top_table["file_source"])
    print("page num: ", top_table["page_num"])

    return response


if __name__ == "__main__":

    #   we would recommend either "dragon-qwen-7b-gguf" or "dragon-yi-9b-gguf"

    #   shows basic recipe for passing a table context and asking a question
    example1_getting_started(model_name="dragon-qwen-7b-gguf")

    #   parse, extract table, ask questions to tables
    example2_parse_tables_and_ask_questions(model_name="dragon-qwen-7b-gguf")

    #   *leading edge* - ask a question to a 100 page pdf 10k, find the right table, and get answer from it
    example3_table_reading_e2e(model_name="dragon-qwen-7b-gguf")

